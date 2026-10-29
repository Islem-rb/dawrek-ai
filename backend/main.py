"""Dawrek API + static web apps.

    /         patient app (take a ticket, follow it live, chat)
    /staff    staff console (call next, done, no-show)
    /screen   waiting-room display (now serving, QR code to join)
    /insights manager dashboard (peaks, waits, what patients ask)
"""
from __future__ import annotations

import hmac
import logging
import os
import socket
import time
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # before importing modules that read env vars

from fastapi import Depends, FastAPI, Header, HTTPException, Request  # noqa: E402
from fastapi.concurrency import run_in_threadpool  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from backend.assistant import Assistant  # noqa: E402
from backend.insights import Insights  # noqa: E402
from backend.queue_engine import SERVICES, QueueEngine  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
PORT = int(os.getenv("PORT", 8000))
STAFF_PIN = os.getenv("STAFF_PIN", "").strip()  # set it when the app is public
MAX_AUDIO_BYTES = 5 * 1024 * 1024  # ~5 min of opus; the app records 30 s max

app = FastAPI(title="Dawrek", description="Smart multilingual patient queue", version="2.0.0")
queue = QueueEngine()
assistant = Assistant()
insights = Insights()


class TicketRequest(BaseModel):
    service: str
    name: str = Field("", max_length=40)


class CallRequest(BaseModel):
    service: str
    desk: int = Field(1, ge=1, le=20)


class ChatTurn(BaseModel):
    role: str
    content: str = Field(max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    ticket_id: str | None = None
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


class RateLimiter:
    """Sliding window per client: keeps a public demo from burning the free Groq quota."""

    def __init__(self, limit: int, per_seconds: int = 60):
        self.limit, self.window = limit, per_seconds
        self.hits: dict[str, deque] = defaultdict(deque)

    def check(self, request: Request) -> None:
        forwarded = request.headers.get("x-forwarded-for", "")
        key = forwarded.split(",")[0].strip() or (request.client.host if request.client else "?")
        now, hits = time.monotonic(), self.hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            raise HTTPException(429, "Too many requests, please wait a moment")
        hits.append(now)


chat_limit, voice_limit, ticket_limit = RateLimiter(15), RateLimiter(8), RateLimiter(10)


def require_staff(x_staff_pin: str = Header("")) -> None:
    if STAFF_PIN and not hmac.compare_digest(x_staff_pin.encode(), STAFF_PIN.encode()):
        raise HTTPException(401, "Staff PIN required")


staff_only = [Depends(require_staff)]


def _ticket_or_404(ticket_id: str) -> dict:
    try:
        return queue.ticket_view(ticket_id)
    except KeyError:
        raise HTTPException(404, "Ticket not found")


def _lan_url() -> str:
    """Address phones on the same Wi-Fi can open (used for the QR code)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return f"http://{s.getsockname()[0]}:{PORT}"
    except OSError:
        return f"http://localhost:{PORT}"


# ---- info ----------------------------------------------------------------

@app.get("/api/info")
def info():
    return {"ai_enabled": assistant.ai_enabled, "voice_enabled": assistant.ai_enabled,
            "staff_pin_required": bool(STAFF_PIN), "lan_url": _lan_url(),
            "services": [{"key": k, **v} for k, v in SERVICES.items()]}


@app.get("/api/queue")
def queue_state():
    return queue.snapshot()

# ---- patient ---------------------------------------------------------------

@app.post("/api/tickets")
def take_ticket(req: TicketRequest, request: Request):
    ticket_limit.check(request)
    if req.service not in SERVICES:
        raise HTTPException(400, "Unknown service")
    ticket = queue.take_ticket(req.service, req.name)
    return queue.ticket_view(ticket.id)


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    return _ticket_or_404(ticket_id)


@app.delete("/api/tickets/{ticket_id}")
def cancel_ticket(ticket_id: str):
    _ticket_or_404(ticket_id)
    queue.cancel(ticket_id)
    return queue.ticket_view(ticket_id)


@app.post("/api/chat")
def chat(req: ChatRequest, request: Request):
    chat_limit.check(request)
    ticket = None
    if req.ticket_id:
        try:
            ticket = queue.ticket_view(req.ticket_id)
        except KeyError:
            pass
    result = assistant.reply(req.message.strip(), ticket, [t.model_dump() for t in req.history])
    insights.record_chat(result["lang"], result["intent"], result["mode"])
    return result

@app.post("/api/transcribe")
async def transcribe(request: Request):
    """Raw audio body (webm/ogg/mp4) -> text. The client then sends the text to /api/chat."""
    voice_limit.check(request)
    if not assistant.ai_enabled:
        raise HTTPException(503, "Voice needs GROQ_API_KEY")
    audio = await request.body()
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Recording too long")
    if len(audio) < 1000:
        raise HTTPException(400, "Recording too short")
    try:
        text = await run_in_threadpool(assistant.transcribe, audio, request.headers.get("content-type", ""))
    except Exception as exc:
        logging.getLogger("dawrek").warning("Transcription failed: %s", exc)
        raise HTTPException(502, "Transcription failed")
    return {"text": text}

# ---- staff -----------------------------------------------------------------

@app.post("/api/staff/call", dependencies=staff_only)
def call_next(req: CallRequest):
    if req.service not in SERVICES:
        raise HTTPException(400, "Unknown service")
    ticket = queue.call_next(req.service, req.desk)
    return {"called": queue.ticket_view(ticket.id) if ticket else None}


def _staff_action(action, ticket_id: str) -> dict:
    _ticket_or_404(ticket_id)
    action(ticket_id)
    return queue.ticket_view(ticket_id)


@app.post("/api/staff/tickets/{ticket_id}/done", dependencies=staff_only)
def mark_done(ticket_id: str):
    return _staff_action(queue.mark_done, ticket_id)


@app.post("/api/staff/tickets/{ticket_id}/no-show", dependencies=staff_only)
def mark_no_show(ticket_id: str):
    return _staff_action(queue.mark_no_show, ticket_id)


@app.post("/api/staff/tickets/{ticket_id}/recall", dependencies=staff_only)
def recall(ticket_id: str):
    return _staff_action(queue.recall, ticket_id)


@app.post("/api/staff/demo", dependencies=staff_only)
def seed_demo():
    return {"added": len(queue.seed_demo())}


# ---- insights --------------------------------------------------------------

@app.get("/api/insights")
def get_insights():
    return insights.report(queue)


@app.post("/api/insights/simulate", dependencies=staff_only)
def simulate_day():
    insights.simulate_day()
    return insights.report(queue)


@app.delete("/api/insights/simulate", dependencies=staff_only)
def clear_simulation():
    insights.clear_simulation()
    return insights.report(queue)


@app.post("/api/staff/reset", dependencies=staff_only)
def reset():
    queue.reset()
    return {"ok": True}

# ---- pages -----------------------------------------------------------------

@app.get("/", include_in_schema=False)
def patient_page():
    return FileResponse(FRONTEND / "index.html")


@app.get("/staff", include_in_schema=False)
def staff_page():
    return FileResponse(FRONTEND / "staff.html")


@app.get("/screen", include_in_schema=False)
def screen_page():
    return FileResponse(FRONTEND / "screen.html")


@app.get("/insights", include_in_schema=False)
def insights_page():
    return FileResponse(FRONTEND / "insights.html")


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


if __name__ == "__main__":
    import uvicorn

    print(f"\n  Dawrek is running:\n    Patient app  {_lan_url()}\n    Staff        {_lan_url()}/staff"
          f"\n    Screen       {_lan_url()}/screen\n    Insights     {_lan_url()}/insights\n    AI           {'Groq ' if assistant.ai_enabled else 'offline mode (set GROQ_API_KEY)'}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
