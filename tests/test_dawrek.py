import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.assistant import Assistant, detect_intent, detect_language, is_emergency, offline_answer
from backend.queue_engine import QueueEngine


# ---------------------------------------------------------------- queue engine

def test_tickets_are_numbered_per_service():
    q = QueueEngine()
    assert q.take_ticket("consultation").number == "C-001"
    assert q.take_ticket("consultation").number == "C-002"
    assert q.take_ticket("lab").number == "L-001"


def test_position_and_eta_follow_the_line():
    q = QueueEngine()
    a, b, c = (q.take_ticket("consultation") for _ in range(3))
    view = q.ticket_view(c.id)
    assert view["people_ahead"] == 2 and view["position"] == 3 and view["eta_minutes"] == 24

    q.call_next("consultation", desk=1)
    assert q.ticket_view(a.id)["status"] == "called"
    assert q.ticket_view(c.id)["people_ahead"] == 1
    assert q.ticket_view(c.id)["now_serving"] == ["C-001"]


def test_calling_next_finishes_the_desk_current_patient():
    q = QueueEngine()
    a, b = q.take_ticket("lab"), q.take_ticket("lab")
    q.call_next("lab", desk=2)
    q.call_next("lab", desk=2)
    assert q.ticket_view(a.id)["status"] == "done"
    assert q.ticket_view(b.id)["status"] == "called"
    assert q.ticket_view(b.id)["desk"] == 2


def test_no_show_goes_to_back_then_is_dropped():
    q = QueueEngine()
    a, b = q.take_ticket("admin"), q.take_ticket("admin")
    q.call_next("admin", desk=1)
    q.mark_no_show(a.id)
    assert q.ticket_view(a.id)["status"] == "waiting"
    assert q.ticket_view(a.id)["people_ahead"] == 1  # b is now in front
    q.call_next("admin", desk=1)  # b
    q.call_next("admin", desk=1)  # a again
    q.mark_no_show(a.id)
    assert q.ticket_view(a.id)["status"] == "missed"


def test_cancel_removes_from_line():
    q = QueueEngine()
    a, b = q.take_ticket("imaging"), q.take_ticket("imaging")
    q.cancel(a.id)
    assert q.ticket_view(b.id)["people_ahead"] == 0
    assert q.snapshot()["services"][3]["waiting_count"] == 1


# ---------------------------------------------------------------- assistant

@pytest.mark.parametrize("text, lang", [
    ("قداش باقي قدامي؟", "tn"),
    ("شنوة الوراق اللي لازمني؟", "tn"),
    ("ما هي الوثائق المطلوبة للاستشارة؟", "ar"),
    ("9adech ba9i 9oddemi?", "arabizi"),
    ("chnowa lezmni njib?", "arabizi"),
    ("Combien de temps dois-je attendre ?", "fr"),
    ("How many people are ahead of me?", "en"),
])
def test_language_detection(text, lang):
    assert detect_language(text) == lang


@pytest.mark.parametrize("text", ["J'ai une douleur thoracique", "ما نجمش نتنفس", "I can't breathe", "عندي نزيف"])
def test_emergency_guardrail_bypasses_llm(text):
    result = Assistant().reply(text)
    assert result["mode"] == "safety" and "190" in result["reply"]


def test_offline_answer_uses_live_ticket():
    q = QueueEngine()
    q.take_ticket("consultation")
    t = q.take_ticket("consultation")
    answer = offline_answer("قداش باقي قدامي؟", "tn", q.ticket_view(t.id))
    assert "C-002" in answer and "1" in answer


def test_offline_answer_uses_knowledge_base_in_user_language():
    assert detect_intent("Quels documents apporter ?") == "documents_required"
    assert "CNAM" in offline_answer("Quels documents apporter ?", "fr", None)


# ---------------------------------------------------------------- API

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "queue", QueueEngine())
    monkeypatch.setattr(main.assistant, "client", None)  # never hit the network in tests
    monkeypatch.setattr(main, "STAFF_PIN", "")  # ignore a PIN set in the local .env
    for limiter in ("chat_limit", "voice_limit", "ticket_limit"):  # every test starts as a new visitor
        monkeypatch.setattr(main, limiter, main.RateLimiter(getattr(main, limiter).limit))
    return TestClient(main.app)


def test_full_patient_journey(client):
    t = client.post("/api/tickets", json={"service": "consultation", "name": "Amira"}).json()
    assert t["number"] == "C-001" and t["status"] == "waiting"

    chat = client.post("/api/chat", json={"message": "How many people are ahead of me?", "ticket_id": t["id"]}).json()
    assert chat["mode"] == "offline" and "C-001" in chat["reply"]

    called = client.post("/api/staff/call", json={"service": "consultation", "desk": 3}).json()["called"]
    assert called["id"] == t["id"] and called["desk"] == 3
    assert client.get(f"/api/tickets/{t['id']}").json()["status"] == "called"

    client.post(f"/api/staff/tickets/{t['id']}/done")
    assert client.get("/api/queue").json()["stats"]["served"] == 1


def test_api_validation(client):
    assert client.post("/api/tickets", json={"service": "spa"}).status_code == 400
    assert client.get("/api/tickets/nope").status_code == 404
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.get("/").status_code == 200 and client.get("/staff").status_code == 200


# ---------------------------------------------------------------- insights

def test_simulated_day_matches_knowledge_base():
    from backend.insights import compute, simulate_day
    day = simulate_day(seed=7)
    report = compute(day["tickets"], day["chats"])
    peak = max(report["by_hour"], key=lambda h: h["arrivals"])["hour"]
    assert peak in (8, 9, 14, 15)  # wait_times.txt: peaks 8-10h and 14-16h
    assert 10 <= report["kpis"]["avg_wait"] <= 45
    assert {r["kind"] for r in report["recommendations"]} >= {"darija", "top_question"}


def test_insights_record_live_chats(client, monkeypatch):
    from backend.insights import Insights
    monkeypatch.setattr(main, "insights", Insights())
    client.post("/api/tickets", json={"service": "lab"})
    client.post("/api/chat", json={"message": "9adech ba9i?"})
    client.post("/api/chat", json={"message": "J'ai une douleur thoracique"})
    report = client.get("/api/insights").json()
    assert report["kpis"]["patients"] == 1 and report["kpis"]["questions"] == 2
    assert report["languages"]["arabizi"] == 1 and report["topics"]["emergency"] == 1
    assert report["sources"]["simulated_date"] is None

    simulated = client.post("/api/insights/simulate").json()
    assert simulated["sources"]["simulated_date"] and simulated["kpis"]["patients"] > 100
    assert client.delete("/api/insights/simulate").json()["kpis"]["patients"] == 1
    assert client.get("/insights").status_code == 200


# ---------------------------------------------------------------- voice, staff PIN, rate limits

class FakeGroq:
    """Stands in for the Groq client: records the upload, returns a Darija transcript."""
    def __init__(self):
        self.uploads = []
        outer = self

        class Transcriptions:
            def create(self, file, **kwargs):
                outer.uploads.append((file[0], len(file[1]), kwargs["model"]))
                return type("T", (), {"text": " قداش باقي قدامي؟ "})()

        self.audio = type("Audio", (), {"transcriptions": Transcriptions()})()


def test_voice_transcription(client, monkeypatch):
    fake = FakeGroq()
    monkeypatch.setattr(main.assistant, "client", fake)
    r = client.post("/api/transcribe", content=b"\x1a" * 4000, headers={"Content-Type": "audio/webm;codecs=opus"})
    assert r.status_code == 200 and r.json()["text"] == "قداش باقي قدامي؟"
    assert fake.uploads == [("question.webm", 4000, "whisper-large-v3")]
    assert client.post("/api/transcribe", content=b"x", headers={"Content-Type": "audio/webm"}).status_code == 400


def test_voice_disabled_without_key(client):
    assert client.get("/api/info").json()["voice_enabled"] is False
    assert client.post("/api/transcribe", content=b"\x1a" * 4000).status_code == 503


def test_staff_pin_protects_staff_actions(client, monkeypatch):
    monkeypatch.setattr(main, "STAFF_PIN", "4321")
    assert client.get("/api/info").json()["staff_pin_required"] is True
    assert client.post("/api/staff/reset").status_code == 401
    assert client.post("/api/staff/reset", headers={"X-Staff-Pin": "0000"}).status_code == 401
    assert client.post("/api/staff/reset", headers={"X-Staff-Pin": "4321"}).status_code == 200
    assert client.post("/api/insights/simulate").status_code == 401
    # patients and the public screen never need the PIN
    assert client.post("/api/tickets", json={"service": "lab"}).status_code == 200
    assert client.get("/api/queue").status_code == 200


def test_rate_limit_per_client(client, monkeypatch):
    monkeypatch.setattr(main, "chat_limit", main.RateLimiter(2))
    ask = lambda ip: client.post("/api/chat", json={"message": "bonjour"}, headers={"X-Forwarded-For": ip}).status_code
    assert [ask("1.1.1.1"), ask("1.1.1.1"), ask("1.1.1.1")] == [200, 200, 429]
    assert ask("2.2.2.2") == 200  # another visitor is not affected


def test_offline_answer_when_next_in_line():
    q = QueueEngine()
    t = q.take_ticket("lab")
    assert "next" in offline_answer("How many people are ahead of me?", "en", q.ticket_view(t.id))


def test_busy_model_falls_back_to_next_model(monkeypatch):
    import httpx
    from groq import RateLimitError
    from backend import assistant as assistant_module

    calls = []

    class Completions:
        def create(self, model, **kwargs):
            calls.append(model)
            if model == assistant_module.GROQ_MODEL:
                response = httpx.Response(429, request=httpx.Request("POST", "https://api.groq.com"))
                raise RateLimitError("rate limited", response=response, body=None)
            message = type("M", (), {"content": "Fama 2 nas 9oddamek."})()
            return type("R", (), {"choices": [type("C", (), {"message": message})()]})()

    a = Assistant()
    a.client = type("Client", (), {"chat": type("Chat", (), {"completions": Completions()})()})()
    result = a.reply("9adech ba9i?")
    assert result["mode"] == "ai" and result["reply"] == "Fama 2 nas 9oddamek."
    assert calls == [assistant_module.GROQ_MODEL, *assistant_module.FALLBACK_MODELS]


# ---------------------------------------------------------------- appointments, learned wait times

def test_confirmed_appointments_go_first_but_walk_ins_still_move():
    q = QueueEngine()
    w1, w2 = q.take_ticket("consultation"), q.take_ticket("consultation")
    appts = [q.take_ticket("consultation", appointment=True) for _ in range(3)]
    assert q.ticket_view(appts[0].id)["people_ahead"] == 2  # unconfirmed: still a walk-in
    for a in appts:
        q.confirm_appointment(a.id)
    called = [q.call_next("consultation", 1).number for _ in range(5)]
    assert called == ["C-003", "C-004", "C-001", "C-005", "C-002"]  # 2 appointments, then 1 walk-in


def test_rejected_or_missed_appointment_loses_priority():
    q = QueueEngine()
    w = q.take_ticket("lab")
    a = q.take_ticket("lab", appointment=True)
    q.confirm_appointment(a.id, confirmed=False)
    assert q.ticket_view(a.id)["appointment"] is None and q.ticket_view(a.id)["people_ahead"] == 1
    b = q.take_ticket("lab", appointment=True)
    q.confirm_appointment(b.id)
    q.call_next("lab", 1)
    q.mark_no_show(b.id)
    assert q.ticket_view(b.id)["appointment"] is None


def test_wait_time_learns_from_real_visits_and_desks():
    import time as _time
    q = QueueEngine()
    tickets = [q.take_ticket("consultation") for _ in range(7)]
    assert q.ticket_view(tickets[6].id)["eta_minutes"] == 6 * 12  # configured average
    now = _time.time()
    for t in tickets[:3]:  # three real 6-minute visits
        t.status, t.called_at, t.finished_at = "done", now - 900, now - 540
    assert q.service_minutes("consultation") == (6.0, True)
    assert q.ticket_view(tickets[6].id)["eta_minutes"] == 3 * 6
    q.call_next("consultation", 1)
    q.call_next("consultation", 2)  # two desks now serve consultation
    assert q.ticket_view(tickets[6].id)["eta_minutes"] == 1 * 6 // 2


def test_misclicks_are_not_learned():
    import time as _time
    q = QueueEngine()
    for t in [q.take_ticket("lab") for _ in range(5)]:
        t.status, t.called_at, t.finished_at = "done", _time.time() - 10, _time.time()
    assert q.service_minutes("lab") == (5, False)


# ---------------------------------------------------------------- settings

@pytest.fixture
def clinic(client, monkeypatch, tmp_path):
    from backend.settings import ClinicSettings
    settings = ClinicSettings(tmp_path / "clinic.json")
    monkeypatch.setattr(main, "clinic", settings)
    yield settings
    settings.reset()  # SERVICES and the knowledge base are shared by the whole process


def test_settings_apply_live_and_persist(client, clinic):
    from backend import assistant as assistant_module
    from backend.settings import ClinicSettings
    r = client.put("/api/settings", json={
        "clinic_name": "Clinique El Menzah", "desks": 3,
        "services": {"imaging": {"enabled": False}, "lab": {"avg_minutes": 7}},
        "knowledge": {"documents_required": {"fr": "Apportez la carte CNAM et la carte d'identité."}},
    })
    assert r.status_code == 200
    info = client.get("/api/info").json()
    assert info["clinic_name"] == "Clinique El Menzah" and info["desks"] == 3
    assert client.post("/api/tickets", json={"service": "imaging"}).status_code == 400  # closed
    lab = client.post("/api/tickets", json={"service": "lab"}).json()
    client.post("/api/tickets", json={"service": "lab"})
    assert client.get("/api/queue").json()["services"][2]["eta_minutes"] == 7 * 2
    assert assistant_module.KB["documents_required"]["fr"].startswith("Apportez")
    assert lab["number"] == "L-001"

    saved = clinic.path.read_text(encoding="utf-8")
    clinic.reset()
    clinic.path.write_text(saved, encoding="utf-8")
    reloaded = ClinicSettings(clinic.path)
    reloaded.load()  # a restart reads the saved file back
    assert reloaded.clinic_name == "Clinique El Menzah" and main.SERVICES["imaging"]["enabled"] is False


def test_settings_validation_changes_nothing(client, clinic):
    assert client.put("/api/settings", json={"desks": 99}).status_code == 400
    bad = {"clinic_name": "X", "services": {k: {"enabled": False} for k in main.SERVICES}}
    assert client.put("/api/settings", json=bad).status_code == 400
    assert client.get("/api/info").json()["clinic_name"] == ""  # nothing half-applied
    assert all(s.get("enabled", True) for s in main.SERVICES.values())


def test_settings_need_the_staff_pin(client, clinic, monkeypatch):
    monkeypatch.setattr(main, "STAFF_PIN", "4321")
    assert client.get("/api/settings").status_code == 401
    assert client.put("/api/settings", json={"desks": 2}).status_code == 401
    assert client.get("/api/settings", headers={"X-Staff-Pin": "4321"}).status_code == 200


# ---------------------------------------------------------------- phone alerts

def test_phone_alerts_almost_and_called(client, monkeypatch):
    import pywebpush
    from backend.push import PushNotifier
    sent = []
    monkeypatch.setattr(pywebpush, "webpush", lambda sub, data, **kw: sent.append((sub["endpoint"], data)))
    monkeypatch.setattr(main, "push", PushNotifier())
    assert client.get("/api/info").json()["push_key"]
    from backend import push as push_module
    from py_vapid import _check_sub
    assert _check_sub(push_module.SUBJECT)  # the push services reject anything else

    tickets = [client.post("/api/tickets", json={"service": "admin"}).json() for _ in range(4)]
    last = tickets[3]
    sub = {"endpoint": "https://push.example/abc", "keys": {"p256dh": "x", "auth": "y"}}
    assert client.post(f"/api/tickets/{last['id']}/push", json={"subscription": sub, "lang": "fr"}).status_code == 200
    assert sent == []  # 3 ahead: not yet

    client.post("/api/staff/call", json={"service": "admin", "desk": 1})  # 2 ahead now
    assert len(sent) == 1 and "Bientôt" in sent[0][1]
    client.post("/api/staff/call", json={"service": "admin", "desk": 1})
    assert len(sent) == 1  # "almost" is sent once
    client.post("/api/staff/call", json={"service": "admin", "desk": 1})
    client.post("/api/staff/call", json={"service": "admin", "desk": 2})
    assert len(sent) == 2 and "guichet 2" in sent[1][1]
    client.post(f"/api/staff/tickets/{last['id']}/recall")
    assert len(sent) == 3  # a recall rings again

    bad = {"subscription": {"endpoint": "http://evil.local"}}
    assert client.post(f"/api/tickets/{last['id']}/push", json=bad).status_code == 400


def test_service_worker_and_manifest_are_served(client):
    assert client.get("/sw.js").headers["content-type"].startswith("text/javascript")
    assert client.get("/manifest.webmanifest").json()["start_url"] == "/"
    assert client.get("/settings").status_code == 200
