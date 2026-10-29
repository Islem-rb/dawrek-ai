"""In-memory live queue: tickets, positions, wait estimates, desk calls.

State lives in one process and resets on restart, which is what a demo needs.
Swapping it for a database only means re-implementing this class.
"""
from __future__ import annotations

import random
import threading
import time
import uuid
from dataclasses import dataclass, field

# Mirrors data/knowledge_base/services.txt. Emergencies are not queued:
# patients are sent straight to the emergency department instead.
SERVICES = {
    "consultation": {"prefix": "C", "avg_minutes": 12},
    "followup": {"prefix": "S", "avg_minutes": 10},
    "lab": {"prefix": "L", "avg_minutes": 5},
    "imaging": {"prefix": "R", "avg_minutes": 15},
    "admin": {"prefix": "A", "avg_minutes": 4},
}

WAITING, CALLED, DONE, CANCELLED, MISSED = "waiting", "called", "done", "cancelled", "missed"
MAX_NO_SHOWS = 2  # first absence: back of the line; second: ticket is dropped

DEMO_NAMES = ["Amira", "Youssef", "Mariem", "Hamza", "Salma", "Karim", "Ines", "Aziz", "Nour", "Fares"]


@dataclass
class Ticket:
    id: str
    number: str
    service: str
    name: str
    order: float
    created_at: float
    status: str = WAITING
    desk: int | None = None
    called_at: float | None = None
    finished_at: float | None = None
    no_shows: int = 0


@dataclass
class QueueEngine:
    tickets: dict[str, Ticket] = field(default_factory=dict)
    counters: dict[str, int] = field(default_factory=lambda: {s: 0 for s in SERVICES})
    calls: list[str] = field(default_factory=list)  # ticket ids, most recent last
    version: int = 0
    _order: float = 0.0
    _lock: threading.RLock = field(default_factory=threading.RLock)

    # ---- patient side -------------------------------------------------

    def take_ticket(self, service: str, name: str = "") -> Ticket:
        if service not in SERVICES:
            raise KeyError(service)
        with self._lock:
            self.counters[service] += 1
            self._order += 1
            number = f"{SERVICES[service]['prefix']}-{self.counters[service]:03d}"
            ticket = Ticket(
                id=uuid.uuid4().hex,
                number=number,
                service=service,
                name=name.strip()[:40],
                order=self._order,
                created_at=time.time(),
            )
            self.tickets[ticket.id] = ticket
            self._touch()
            return ticket

    def cancel(self, ticket_id: str) -> Ticket:
        with self._lock:
            ticket = self.tickets[ticket_id]
            if ticket.status in (WAITING, CALLED):
                ticket.status = CANCELLED
                ticket.finished_at = time.time()
                self._touch()
            return ticket

    def ticket_view(self, ticket_id: str) -> dict:
        with self._lock:
            ticket = self.tickets[ticket_id]
            ahead = self._ahead(ticket)
            return {
                "id": ticket.id,
                "number": ticket.number,
                "service": ticket.service,
                "name": ticket.name,
                "status": ticket.status,
                "desk": ticket.desk,
                "no_shows": ticket.no_shows,
                "people_ahead": ahead,
                "position": ahead + 1 if ticket.status == WAITING else 0,
                "eta_minutes": self._eta(ticket.service, ahead) if ticket.status == WAITING else 0,
                "now_serving": [t.number for t in self._serving(ticket.service)],
                "version": self.version,
            }

    # ---- staff side ---------------------------------------------------

    def call_next(self, service: str, desk: int) -> Ticket | None:
        """Finish whatever this desk was serving, then call the next patient."""
        if service not in SERVICES:
            raise KeyError(service)
        with self._lock:
            for t in self.tickets.values():
                if t.status == CALLED and t.desk == desk:
                    self._finish(t)
            waiting = self._waiting(service)
            if not waiting:
                self._touch()
                return None
            ticket = waiting[0]
            ticket.status, ticket.desk, ticket.called_at = CALLED, desk, time.time()
            self.calls.append(ticket.id)
            self._touch()
            return ticket

    def mark_done(self, ticket_id: str) -> Ticket:
        with self._lock:
            ticket = self.tickets[ticket_id]
            if ticket.status == CALLED:
                self._finish(ticket)
                self._touch()
            return ticket

    def mark_no_show(self, ticket_id: str) -> Ticket:
        """Absent when called: back to the end of the line (see queue_general.txt)."""
        with self._lock:
            ticket = self.tickets[ticket_id]
            if ticket.status != CALLED:
                return ticket
            ticket.no_shows += 1
            ticket.desk = None
            if ticket.no_shows >= MAX_NO_SHOWS:
                ticket.status = MISSED
                ticket.finished_at = time.time()
            else:
                self._order += 1
                ticket.status, ticket.order = WAITING, self._order
            self._touch()
            return ticket

    def recall(self, ticket_id: str) -> Ticket:
        """Announce a called ticket again (bumps it to the top of the board)."""
        with self._lock:
            ticket = self.tickets[ticket_id]
            if ticket.status == CALLED:
                self.calls.append(ticket.id)
                self._touch()
            return ticket

    def seed_demo(self, count: int = 8) -> list[Ticket]:
        with self._lock:
            weights = {"consultation": 5, "followup": 2, "lab": 3, "imaging": 1, "admin": 2}
            services = random.choices(list(weights), weights=list(weights.values()), k=count)
            return [self.take_ticket(s, random.choice(DEMO_NAMES)) for s in services]

    def reset(self) -> None:
        with self._lock:
            self.tickets.clear()
            self.calls.clear()
            self.counters = {s: 0 for s in SERVICES}
            self._order = 0.0
            self._touch()

    # ---- boards -------------------------------------------------------

    def snapshot(self) -> dict:
        with self._lock:
            services = []
            for key, cfg in SERVICES.items():
                waiting = self._waiting(key)
                services.append({
                    "key": key,
                    "prefix": cfg["prefix"],
                    "avg_minutes": cfg["avg_minutes"],
                    "waiting_count": len(waiting),
                    "eta_minutes": self._eta(key, len(waiting)),
                    "waiting": [self._brief(t) for t in waiting],
                    "serving": [self._brief(t) for t in self._serving(key)],
                })
            recent, seen = [], set()
            for tid in reversed(self.calls):
                t = self.tickets.get(tid)
                if t and tid not in seen:
                    seen.add(tid)
                    recent.append(self._brief(t))
                if len(recent) == 6:
                    break
            finished = [t for t in self.tickets.values() if t.status == DONE and t.called_at]
            waits = [(t.called_at - t.created_at) / 60 for t in finished]
            return {
                "version": self.version,
                "services": services,
                "recent_calls": recent,
                "call_seq": len(self.calls),
                "stats": {
                    "waiting": sum(s["waiting_count"] for s in services),
                    "served": len(finished),
                    "no_shows": sum(t.no_shows for t in self.tickets.values()),
                    "avg_wait_minutes": round(sum(waits) / len(waits), 1) if waits else 0,
                },
            }

    # ---- internals ----------------------------------------------------

    def _touch(self) -> None:
        self.version += 1

    def _finish(self, ticket: Ticket) -> None:
        ticket.status, ticket.finished_at = DONE, time.time()

    def _waiting(self, service: str) -> list[Ticket]:
        return sorted(
            (t for t in self.tickets.values() if t.service == service and t.status == WAITING),
            key=lambda t: t.order,
        )

    def _serving(self, service: str) -> list[Ticket]:
        return sorted(
            (t for t in self.tickets.values() if t.service == service and t.status == CALLED),
            key=lambda t: t.desk or 0,
        )

    def _ahead(self, ticket: Ticket) -> int:
        if ticket.status != WAITING:
            return 0
        return sum(1 for t in self._waiting(ticket.service) if t.order < ticket.order)

    @staticmethod
    def _eta(service: str, people_ahead: int) -> int:
        return people_ahead * SERVICES[service]["avg_minutes"]

    @staticmethod
    def _brief(t: Ticket) -> dict:
        return {"id": t.id, "number": t.number, "service": t.service, "name": t.name,
                "status": t.status, "desk": t.desk, "no_shows": t.no_shows}
