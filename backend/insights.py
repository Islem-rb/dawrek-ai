"""Manager insights: what happened in the queue and what patients asked the assistant.

Two data sources are combined:
  - live: tickets from the running QueueEngine and every real chat message
  - simulated: one realistic past day, generated on demand for demos and clearly flagged
"""
from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from backend.queue_engine import DONE, MISSED, SERVICES, QueueEngine

HOURS = list(range(7, 18))  # 07:00 to 17:59
LANGS = ["tn", "arabizi", "ar", "fr", "en"]
TOPICS = ["position", "documents_required", "wait_times", "appointments", "services", "queue_general", "emergency"]

# Simulation knobs, shaped after data/knowledge_base/wait_times.txt (peaks 8-10h and 14-16h).
SIM_ARRIVALS_PER_HOUR = {7: 6, 8: 32, 9: 35, 10: 17, 11: 13, 12: 7, 13: 10, 14: 26, 15: 25, 16: 9}
SIM_SERVICE_MIX = {"consultation": 45, "followup": 15, "lab": 22, "imaging": 8, "admin": 10}
SIM_DESKS = {"consultation": 2, "followup": 1, "lab": 1, "imaging": 1, "admin": 1}
SIM_NO_SHOW_RATE = 0.06
SIM_QUESTIONS_PER_PATIENT = 0.7
SIM_LANG_MIX = {"tn": 46, "arabizi": 21, "fr": 22, "ar": 7, "en": 4}
SIM_TOPIC_MIX = {"position": 38, "documents_required": 22, "wait_times": 14, "appointments": 12,
                 "services": 8, "queue_general": 4, "emergency": 2}


@dataclass
class Insights:
    chats: list[dict] = field(default_factory=list)       # live chat events
    simulated: dict | None = None                          # {"date", "tickets", "chats"}
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_chat(self, lang: str, intent: str, mode: str) -> None:
        with self._lock:
            self.chats.append({"at": time.time(), "lang": lang, "intent": intent, "mode": mode})

    def simulate_day(self, seed: int | None = None) -> None:
        with self._lock:
            self.simulated = simulate_day(seed)

    def clear_simulation(self) -> None:
        with self._lock:
            self.simulated = None

    def report(self, queue: QueueEngine) -> dict:
        with queue._lock:
            live_tickets = [_ticket_record(t) for t in queue.tickets.values()]
        with self._lock:
            tickets = live_tickets + (self.simulated["tickets"] if self.simulated else [])
            chats = self.chats + (self.simulated["chats"] if self.simulated else [])
            sources = {"live_tickets": len(live_tickets), "live_questions": len(self.chats),
                       "simulated_date": self.simulated["date"] if self.simulated else None}
        return {"sources": sources, **compute(tickets, chats)}


def _ticket_record(t) -> dict:
    return {"service": t.service, "created_at": t.created_at, "called_at": t.called_at,
            "finished_at": t.finished_at, "status": t.status, "no_shows": t.no_shows}


def compute(tickets: list[dict], chats: list[dict]) -> dict:
    def hour(ts: float) -> int:
        return datetime.fromtimestamp(ts).hour

    called = [t for t in tickets if t["called_at"]]
    waits = [(t["called_at"] - t["created_at"]) / 60 for t in called]
    done = [t for t in tickets if t["status"] == DONE and t["called_at"] and t["finished_at"]]
    service_times = [(t["finished_at"] - t["called_at"]) / 60 for t in done]
    no_show_tickets = sum(1 for t in tickets if t["no_shows"])

    by_hour = []
    for h in HOURS:
        arrivals = [t for t in tickets if hour(t["created_at"]) == h]
        hw = [(t["called_at"] - t["created_at"]) / 60 for t in arrivals if t["called_at"]]
        by_hour.append({"hour": h, "arrivals": len(arrivals), "avg_wait": _avg(hw)})

    by_service = []
    for key in SERVICES:
        st = [t for t in tickets if t["service"] == key]
        sw = [(t["called_at"] - t["created_at"]) / 60 for t in st if t["called_at"]]
        by_service.append({"service": key, "patients": len(st), "avg_wait": _avg(sw),
                           "max_wait": round(max(sw), 1) if sw else 0})

    languages = {lang: sum(1 for c in chats if c["lang"] == lang) for lang in LANGS}
    topics = {topic: sum(1 for c in chats if c["intent"] == topic) for topic in TOPICS}

    return {
        "kpis": {
            "patients": len(tickets),
            "served": len(done),
            "avg_wait": _avg(waits),
            "avg_service": _avg(service_times),
            "no_show_rate": round(100 * no_show_tickets / len(tickets), 1) if tickets else 0,
            "questions": len(chats),
            "darija_share": round(100 * (languages["tn"] + languages["arabizi"]) / len(chats)) if chats else 0,
            "emergencies": topics["emergency"],
        },
        "by_hour": by_hour,
        "by_service": by_service,
        "languages": languages,
        "topics": topics,
        "recommendations": recommendations(by_hour, by_service, languages, topics, len(tickets),
                                           no_show_tickets, len(chats)),
    }


def recommendations(by_hour, by_service, languages, topics, n_tickets, n_no_show, n_chats) -> list[dict]:
    """Structured, language-neutral advice; the dashboard turns each `kind` into a sentence."""
    recs = []
    if n_tickets >= 10:
        peak = max(by_hour, key=lambda h: h["arrivals"])
        slowest = max(by_service, key=lambda s: s["avg_wait"])
        if slowest["avg_wait"] >= 15:
            recs.append({"kind": "add_desk", "service": slowest["service"], "hour": peak["hour"],
                         "arrivals": peak["arrivals"], "wait": slowest["avg_wait"]})
        if n_no_show / n_tickets >= 0.04:
            recs.append({"kind": "no_shows", "rate": round(100 * n_no_show / n_tickets, 1)})
    if n_chats >= 5:
        asked = {k: v for k, v in topics.items() if k not in ("position", "emergency")}
        top = max(asked, key=asked.get)
        if asked[top]:
            recs.append({"kind": "top_question", "topic": top, "share": round(100 * asked[top] / n_chats)})
        darija = languages["tn"] + languages["arabizi"]
        if darija:
            recs.append({"kind": "darija", "share": round(100 * darija / n_chats),
                         "arabizi": round(100 * languages["arabizi"] / n_chats)})
    if topics["emergency"]:
        recs.append({"kind": "emergency", "count": topics["emergency"]})
    return recs


def simulate_day(seed: int | None = None) -> dict:
    """A plausible past day (yesterday): arrivals, a real queue per service, and chat questions."""
    rng = random.Random(seed)
    day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    services, weights = list(SIM_SERVICE_MIX), list(SIM_SERVICE_MIX.values())

    arrivals = []
    for h, count in SIM_ARRIVALS_PER_HOUR.items():
        for _ in range(count):
            at = day + timedelta(hours=h, seconds=rng.uniform(0, 3600))
            arrivals.append((at.timestamp(), rng.choices(services, weights)[0]))
    arrivals.sort()

    # First-come-first-served queue per service with N desks.
    desk_free = {s: [0.0] * SIM_DESKS[s] for s in services}
    tickets = []
    for created, service in arrivals:
        desks = desk_free[service]
        i = min(range(len(desks)), key=desks.__getitem__)
        called = max(created, desks[i]) + rng.uniform(15, 60)
        if rng.random() < SIM_NO_SHOW_RATE:
            tickets.append({"service": service, "created_at": created, "called_at": called,
                            "finished_at": called + 60, "status": MISSED, "no_shows": 2})
            desks[i] = called + 60
            continue
        avg = SERVICES[service]["avg_minutes"]
        duration = max(2.0, rng.gauss(avg, avg * 0.3)) * 60
        desks[i] = called + duration
        tickets.append({"service": service, "created_at": created, "called_at": called,
                        "finished_at": called + duration, "status": DONE, "no_shows": 0})

    chats = []
    langs, lw = list(SIM_LANG_MIX), list(SIM_LANG_MIX.values())
    topics, tw = list(SIM_TOPIC_MIX), list(SIM_TOPIC_MIX.values())
    for t in tickets:
        if rng.random() < SIM_QUESTIONS_PER_PATIENT:
            chats.append({"at": t["created_at"] + rng.uniform(60, 900), "lang": rng.choices(langs, lw)[0],
                          "intent": rng.choices(topics, tw)[0], "mode": "ai"})

    return {"date": day.date().isoformat(), "tickets": tickets, "chats": chats}


def _avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 1) if values else 0
