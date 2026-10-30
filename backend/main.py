"""Dawrek API + static web apps.

    /         patient app (take a ticket, follow it live, chat)
    /staff    staff console (call next, done, no-show)
    /screen   waiting-room display (now serving, QR code to join)
    /insights manager dashboard (peaks, waits, what patients ask)
    /settings clinic settings (services, desks, assistant knowledge)
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

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request  # noqa: E402
from fastapi.concurrency import run_in_threadpool  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from backend.assistant import Assistant  # noqa: E402
from backend.insights import Insights  # noqa: E402
from backend.push import PushNotifier  # noqa: E402
from backend.queue_engine import SERVICES, QueueEngine  # noqa: E402
from backend.settings import ClinicSettings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
PORT = int(os.getenv("PORT", 8000))
STAFF_PIN = os.getenv("STAFF_PIN", "").strip()  # set it when the app is public
MAX_AUDIO_BYTES = 5 * 1024 * 1024  # ~5 min of opus; the app records 30 s max

app = FastAPI(title="Dawrek", description="Smart multilingual patient queue", version="2.0.0")
queue = QueueEngine()
assistant = Assistant()
insights = Insights()
clinic = ClinicSettings()
clinic.load()
push = PushNotifier()


class TicketRequest(BaseModel):
    service: str
    name: str = Field("", max_length=40)
    appointment: bool = False


class PushRequest(BaseModel):
    subscription: dict
    lang: str = "tn"


class AppointmentRequest(BaseModel):
    confirmed: bool = True


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
            "push_key": push.public_key, **clinic.public(),
            "services": [{"key": k, "enabled": True, **v} for k, v in SERVICES.items()]}


@app.get("/api/queue")
def queue_state():
    return queue.snapshot()

# ---- patient ---------------------------------------------------------------

@app.post("/api/tickets")
def take_ticket(req: TicketRequest, request: Request):
    ticket_limit.check(request)
    try:
        ticket = queue.take_ticket(req.service, req.name, req.appointment)
    except KeyError:
        raise HTTPException(400, "Unknown or closed service")
    return queue.ticket_view(ticket.id)


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    return _ticket_or_404(ticket_id)


@app.delete("/api/tickets/{ticket_id}")
def cancel_ticket(ticket_id: str, background: BackgroundTasks):
    ticket = _ticket_or_404(ticket_id)
    queue.cancel(ticket_id)
    push.unsubscribe(ticket_id)
    background.add_task(push.notify_queue, queue, ticket["service"])  # everyone behind moved up
    return queue.ticket_view(ticket_id)


@app.post("/api/tickets/{ticket_id}/push")
def subscribe_push(ticket_id: str, req: PushRequest, background: BackgroundTasks):
    """The phone agreed to alerts: remember where to send them for this ticket."""
    ticket = _ticket_or_404(ticket_id)
    if not push.enabled:
        raise HTTPException(503, "Phone alerts are off on this server")
    if not str(req.subscription.get("endpoint", "")).startswith("https://"):
        raise HTTPException(400, "Invalid subscription")
    push.subscribe(ticket_id, req.subscription, req.lang)
    background.add_task(push.notify_queue, queue, ticket["service"])  # maybe it's already almost their turn
    return {"ok": True}


@app.delete("/api/tickets/{ticket_id}/push")
def unsubscribe_push(ticket_id: str):
    push.unsubscribe(ticket_id)
    return {"ok": True}


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
def call_next(req: CallRequest, background: BackgroundTasks):
    if req.service not in SERVICES:
        raise HTTPException(400, "Unknown service")
    ticket = queue.call_next(req.service, req.desk)
    background.add_task(push.notify_queue, queue, req.service)  # sent after the response: staff never wait
    return {"called": queue.ticket_view(ticket.id) if ticket else None}


def _staff_action(action, ticket_id: str, background: BackgroundTasks | None = None) -> dict:
    _ticket_or_404(ticket_id)
    action(ticket_id)
    ticket = queue.ticket_view(ticket_id)
    if background:
        background.add_task(push.notify_queue, queue, ticket["service"])
    return ticket


@app.post("/api/staff/tickets/{ticket_id}/done", dependencies=staff_only)
def mark_done(ticket_id: str):
    return _staff_action(queue.mark_done, ticket_id)


@app.post("/api/staff/tickets/{ticket_id}/no-show", dependencies=staff_only)
def mark_no_show(ticket_id: str, background: BackgroundTasks):
    return _staff_action(queue.mark_no_show, ticket_id, background)


@app.post("/api/staff/tickets/{ticket_id}/recall", dependencies=staff_only)
def recall(ticket_id: str, background: BackgroundTasks):
    ticket = _staff_action(queue.recall, ticket_id)
    if ticket["status"] == "called":  # ring the phone again too
        background.add_task(push.send, ticket_id, "called", "recall", True, number=ticket["number"], desk=ticket["desk"])
    return ticket


@app.post("/api/staff/tickets/{ticket_id}/appointment", dependencies=staff_only)
def confirm_appointment(ticket_id: str, req: AppointmentRequest, background: BackgroundTasks):
    """Staff checked the patient's appointment: confirmed tickets get priority in the line."""
    return _staff_action(lambda tid: queue.confirm_appointment(tid, req.confirmed), ticket_id, background)


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

# ---- settings --------------------------------------------------------------

@app.get("/api/settings", dependencies=staff_only)
def get_settings():
    return clinic.full()


@app.put("/api/settings", dependencies=staff_only)
def update_settings(data: dict):
    try:
        return clinic.update(data)
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, str(exc))


@app.post("/api/settings/reset", dependencies=staff_only)
def reset_settings():
    return clinic.reset()

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


@app.get("/settings", include_in_schema=False)
def settings_page():
    return FileResponse(FRONTEND / "settings.html")


@app.get("/sw.js", include_in_schema=False)
def service_worker():
    # Served from the root so it can control every page (phone alerts + home-screen app).
    return FileResponse(FRONTEND / "sw.js", media_type="text/javascript", headers={"Cache-Control": "no-cache"})


@app.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(FRONTEND / "manifest.webmanifest", media_type="application/manifest+json")


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


if __name__ == "__main__":
    import uvicorn

    print(f"\n  Dawrek is running:\n    Patient app  {_lan_url()}\n    Staff        {_lan_url()}/staff"
          f"\n    Screen       {_lan_url()}/screen\n    Insights     {_lan_url()}/insights\n    AI           {'Groq ' if assistant.ai_enabled else 'offline mode (set GROQ_API_KEY)'}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
