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
