"""Multilingual patient assistant.

Flow for every message:
  1. detect the language (Tunisian Darija in Arabic or Latin script, MSA, French, English)
  2. emergency guardrail: urgent symptoms get a fixed, instant answer, never the LLM
  3. build context = the patient's live ticket + the knowledge base in their language
  4. ask Groq; if no API key or the call fails, answer offline from the same data

The knowledge base is ~15 short paragraphs, so it goes straight into the prompt.
No vector database needed at this size.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

log = logging.getLogger("dawrek.assistant")

KB_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"
# gpt-oss-120b wrote the most natural Tunisian in our tests (Oct 2026); llama-3.3 was retired by Groq.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
# Each Groq model has its own free quota (8k tokens/min, 1k requests/day), so a busy demo spills over to the next.
FALLBACK_MODELS = [m.strip() for m in os.getenv("GROQ_FALLBACK_MODELS", "qwen/qwen3.8-27b").split(",") if m.strip()]
# Reasoning models think before answering; keep that minimal (qwen supports turning it off).
REASONING = {"openai/gpt-oss": "low", "qwen/qwen3": "none"}
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3")  # full v3 handles Arabic dialects better than turbo
# Whisper uses the prompt as context: a few Darija/French queue words steer spelling toward Tunisian.
WHISPER_PROMPT = "عسلامة، قداش باقي قدامي في الطابور؟ شنوة الوراق اللي لازمني؟ التيكيت، الموعد، CNAM. Bonjour, rendez-vous."
AUDIO_EXTENSIONS = {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/mpeg": "mp3",
                    "audio/wav": "wav", "audio/x-wav": "wav", "audio/aac": "m4a"}
EMERGENCY_NUMBER = "190"  # SAMU Tunisia

LANG_NAMES = {
    "tn": "Tunisian Darija written in Arabic script",
    "arabizi": "Tunisian Darija written ONLY in Latin letters and numbers (Arabizi, e.g. '9adech', '3andek', 'lezmek'). "
               "Never use Arabic script, transliterate everything",
    "ar": "Modern Standard Arabic",
    "fr": "French",
    "en": "English",
}
# Which knowledge-base section each language reads from.
KB_SECTION_FOR = {"tn": "tn", "arabizi": "tn", "ar": "ar", "fr": "fr", "en": "fr"}
SECTION_HEADERS = {"ARABIC (Modern Standard)": "ar", "TUNISIAN DARIJA": "tn", "FRENCH": "fr"}

SERVICE_LABELS = {
    "consultation": {"tn": "استشارة عامة", "ar": "الاستشارة العامة", "fr": "Consultation générale", "en": "General consultation"},
    "followup": {"tn": "متابعة طبية", "ar": "المتابعة الطبية", "fr": "Suivi médical", "en": "Medical follow-up"},
    "lab": {"tn": "تحاليل", "ar": "التحاليل المخبرية", "fr": "Analyses", "en": "Lab tests"},
    "imaging": {"tn": "أشعة وإيكو", "ar": "الأشعة والتصوير", "fr": "Radiologie", "en": "Imaging"},
    "admin": {"tn": "خدمات إدارية", "ar": "الخدمات الإدارية", "fr": "Administratif", "en": "Administrative"},
}

# ---------------------------------------------------------------- knowledge base

def load_knowledge_base(kb_dir: Path = KB_DIR) -> dict[str, dict[str, str]]:
    """{topic: {lang: text}} where topic is the file stem (appointments, wait_times, ...)."""
    kb: dict[str, dict[str, str]] = {}
    for path in sorted(kb_dir.glob("*.txt")):
        sections: dict[str, list[str]] = {}
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("---") and stripped.endswith("---"):
                current = SECTION_HEADERS.get(stripped.strip("- ").strip())
                if current:
                    sections[current] = []
            elif current:
                sections[current].append(line)
        kb[path.stem] = {lang: "\n".join(lines).strip() for lang, lines in sections.items()}
    return kb


KB = load_knowledge_base()
CLINIC = {"name": ""}  # set from the settings page

# ---------------------------------------------------------------- language detection

ARABIC_CHARS = re.compile(r"[؀-ۿ]")
WORDS = re.compile(r"[\w']+", re.UNICODE)
ARABIZI_NUMERAL_WORD = re.compile(r"^(?=.*[a-z])(?=.*[2-9])[a-z2-9]+$")

DARIJA_WORDS = {
    "شنوة", "شنوا", "شنية", "قداش", "باش", "برشا", "برشة", "متاع", "متاعي", "نحب", "كيفاش", "وقتاش",
    "علاش", "وين", "توا", "برك", "فما", "ياسر", "نجم", "تنجم", "نستنى", "نتسنى", "الوراق", "اللي",
    "موش", "مش", "ماذابيا", "عيشك", "بربي", "يعيشك", "شكون", "هاذي", "بالحق", "نجيب", "ملا", "زادة",
    "زادا", "عسلامة", "تو", "باهي", "قدامي", "نعمل", "يلزمني", "لازمني", "ماهو",
}
ARABIZI_WORDS = {
    "chnowa", "chnoua", "chniya", "chneya", "kifech", "kifach", "winou", "win", "taw", "tawa", "nheb",
    "bech", "barcha", "mta", "famma", "fama", "ena", "enti", "inti", "brabi", "behi", "mouch", "mech",
    "chkoun", "dour", "dawri", "chhal", "aslema", "ahla", "yezzi", "zeda", "mte3i", "nesta", "nestanna",
}
FRENCH_WORDS = {
    "je", "le", "la", "les", "est", "combien", "quels", "quel", "quelle", "pour", "mon", "ma", "mes",
    "rendez", "attendre", "bonjour", "des", "une", "un", "dois", "faut", "temps", "papiers", "est-ce",
    "que", "quand", "comment", "merci", "salut", "suis", "il", "reste", "avant", "moi", "documents",
}
ENGLISH_WORDS = {
    "the", "what", "how", "my", "is", "when", "wait", "need", "do", "i", "appointment", "long", "hello",
    "hi", "many", "people", "before", "me", "turn", "which", "bring", "should", "can", "thanks", "you",
}


def detect_language(text: str) -> str:
    """Return one of: tn, arabizi, ar, fr, en."""
    if ARABIC_CHARS.search(text):
        words = set(WORDS.findall(text))
        return "tn" if words & DARIJA_WORDS or any(w.lstrip("و") in DARIJA_WORDS for w in words) else "ar"
    words = [w.lower() for w in WORDS.findall(text)]
    if any(ARABIZI_NUMERAL_WORD.match(w) for w in words) or any(w in ARABIZI_WORDS for w in words):
        return "arabizi"
    fr = sum(w in FRENCH_WORDS for w in words) + len(re.findall(r"[éèêàçùûôî]", text.lower()))
    en = sum(w in ENGLISH_WORDS for w in words)
    return "en" if en > fr else "fr"

# ---------------------------------------------------------------- emergency guardrail

EMERGENCY_TERMS = [
    # French / English
    "urgence", "urgent", "douleur thoracique", "poitrine", "respire pas", "respirer", "saigne", "hémorragie",
    "inconscient", "évanoui", "avc", "crise cardiaque", "emergency", "chest pain", "can't breathe",
    "cannot breathe", "bleeding", "unconscious", "fainted", "stroke", "heart attack",
    # Arabic / Darija
    "عاجل", "طوارئ", "نزيف", "ننزف", "صدري", "ما نجمش نتنفس", "منجمش نتنفس", "ضيق تنفس", "مغمى", "طاح",
    "فاقد الوعي", "جلطة", "أزمة قلبية", "سكتة", "ماو نتنفس",
    # Arabizi
    "sadri", "ma najemch netnaffes", "manajamch netnafes", "nezef", "ta7", "ourjence",
]

EMERGENCY_REPLY = {
    "tn": "⚠️ إذا الحالة عاجلة ما تستناش في الطابور! امشي طول للطوارئ ولا عيّط للـSAMU على {n}. الطوارئ ما تحتاجش موعد.",
    "arabizi": "⚠️ Ken el 7ala 3ajla ma tostannech fel queue! Emchi toul lel urgences walla 3ayet lel SAMU 3la {n}. El urgences ma t7tajch maw3ed.",
    "ar": "⚠️ إذا كانت الحالة طارئة فلا تنتظر في الطابور! توجّه مباشرة إلى قسم الطوارئ أو اتصل بالإسعاف (SAMU) على الرقم {n}.",
    "fr": "⚠️ Si c'est urgent, n'attendez pas dans la file ! Allez directement aux urgences ou appelez le SAMU au {n}. Les urgences ne nécessitent pas de rendez-vous.",
    "en": "⚠️ If this is an emergency, don't wait in the queue! Go straight to the emergency department or call SAMU at {n}. No appointment needed.",
}


def is_emergency(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in EMERGENCY_TERMS)

# ---------------------------------------------------------------- live ticket context

LIVE_TEMPLATES = {
    "waiting": {
        "tn": "تيكيتك {number} ({service}). قدامك {ahead} أشخاص، تقريبا {eta} دقيقة.",
        "arabizi": "Ticket mte3ek {number} ({service}). 9oddamek {ahead} 3bed, ta9riban {eta} d9i9a.",
        "ar": "رقم تذكرتك {number} ({service}). أمامك {ahead} أشخاص، والانتظار المتوقع حوالي {eta} دقيقة.",
        "fr": "Votre ticket est {number} ({service}). Il y a {ahead} personne(s) devant vous, environ {eta} min d'attente.",
        "en": "Your ticket is {number} ({service}). {ahead} people ahead of you, about {eta} min wait.",
    },
    "next": {
        "tn": "تيكيتك {number} ({service}): إنت اللي بعد! حضّر روحك.",
        "arabizi": "Ticket mte3ek {number} ({service}): enti elli ba3d! 7adher rou7ek.",
        "ar": "تذكرتك {number} ({service}): أنت التالي! استعد.",
        "fr": "Votre ticket {number} ({service}) : vous êtes le prochain ! Préparez-vous.",
        "en": "Your ticket {number} ({service}): you're next! Get ready.",
    },
    "called": {
        "tn": "دورك توا! تيكيت {number}، امشي للشباك {desk}.",
        "arabizi": "Dourek taw! Ticket {number}, emchi lel guichet {desk}.",
        "ar": "حان دورك الآن! التذكرة {number}، توجّه إلى الشباك {desk}.",
        "fr": "C'est votre tour ! Ticket {number}, présentez-vous au guichet {desk}.",
        "en": "It's your turn! Ticket {number}, please go to desk {desk}.",
    },
    "closed": {
        "tn": "التيكيت {number} ما عادش في الطابور ({status}). تنجم تاخو تيكيت جديد.",
        "arabizi": "Ticket {number} ma 3adech fel queue ({status}). Tnajem te5ou ticket jdid.",
        "ar": "التذكرة {number} لم تعد في الطابور ({status}). يمكنك أخذ تذكرة جديدة.",
        "fr": "Le ticket {number} n'est plus dans la file ({status}). Vous pouvez prendre un nouveau ticket.",
        "en": "Ticket {number} is no longer in the queue ({status}). You can take a new ticket.",
    },
}


SERVING_SUFFIX = {
    "tn": " توا يعدّيو: {serving}.", "arabizi": " Taw yet3addew: {serving}.", "ar": " يُخدم الآن: {serving}.",
    "fr": " En cours : {serving}.", "en": " Now serving: {serving}.",
}


def describe_ticket(ticket: dict | None, lang: str) -> str | None:
    if not ticket:
        return None
    label_lang = KB_SECTION_FOR[lang] if lang != "arabizi" else "fr"
    fields = {
        "number": ticket["number"],
        "service": SERVICE_LABELS[ticket["service"]][label_lang],
        "ahead": ticket["people_ahead"],
        "eta": ticket["eta_minutes"],
        "serving": ", ".join(ticket["now_serving"]),
        "desk": ticket["desk"],
        "status": ticket["status"],
    }
    kind = ticket["status"] if ticket["status"] in ("waiting", "called") else "closed"
    if kind == "waiting" and ticket["people_ahead"] == 0:
        kind = "next"
    text = LIVE_TEMPLATES[kind][lang].format(**fields)
    if kind in ("waiting", "next") and fields["serving"]:
        text += SERVING_SUFFIX[lang].format(**fields)
    return text

# ---------------------------------------------------------------- offline answers

INTENT_KEYWORDS = {
    "position": ["قداش", "باقي", "دوري", "دورى", "قدامي", "أمامي", "كم بقي", "متى دوري", "position", "combien de personnes",
                 "mon tour", "devant moi", "reste", "my turn", "ahead", "how long", "how many", "9adech", "ba9i",
                 "dour", "dawri", "chhal", "9oddemi", "9odami", "mon ticket", "my ticket", "تيكيت", "ticket"],
    "documents_required": ["وراق", "أوراق", "اوراق", "وثائق", "ورقة", "بطاقة", "document", "papier", "pièce", "piece",
                           "cnam", "wra9", "wra9i", "lezm", "njib", "papers", "bring", "carte", "id card", "passport", "باسبور"],
    "appointments": ["موعد", "مواعيد", "rendez", "rdv", "appointment", "annul", "cancel", "maw3ed", "mau3ed",
                     "reschedul", "reprogram", "إلغاء", "نلغي", "نبدل", "booking", "réserv", "حجز", "نحجز"],
    "services": ["خدمات", "خدمة", "service", "analyse", "تحاليل", "تحليل", "أشعة", "اشعة", "إيكو", "radio", "lab",
                 "x-ray", "imaging", "khadamet", "échographie", "scanner"],
    "wait_times": ["وقت", "ذروة", "زحمة", "انتظار", "نستنى", "heure", "pointe", "peak", "busy", "wa9t", "attente",
                   "attendre", "wait", "zo7ma", "temps"],
    "queue_general": ["طابور", "كيفاش", "comment", "how does", "file", "queue", "fonctionne", "work", "kifech"],
}

OFFLINE_NOTE = {
    "tn": "(وضع بدون ذكاء اصطناعي)", "arabizi": "(mode offline)", "ar": "(وضع غير متصل)",
    "fr": "(mode hors ligne)", "en": "(offline mode)",
}


# Only the relevant topics go into the prompt: smaller prompts stretch the free token quota.
TOPICS_FOR_INTENT = {
    "position": ["wait_times", "queue_general"],
    "wait_times": ["wait_times", "queue_general"],
    "documents_required": ["documents_required"],
    "appointments": ["appointments"],
    "services": ["services"],
}


def detect_intent(text: str) -> str:
    low = text.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in low for k in keywords):
            return intent
    return "queue_general"


def offline_answer(message: str, lang: str, ticket: dict | None) -> str:
    intent = detect_intent(message)
    if intent == "position" and ticket:
        return describe_ticket(ticket, lang)
    if intent == "position":
        intent = "wait_times"
    text = KB.get(intent, {}).get(KB_SECTION_FOR[lang], "")
    live = describe_ticket(ticket, lang)
    return "\n\n".join(p for p in (text, live, OFFLINE_NOTE[lang]) if p)

# ---------------------------------------------------------------- LLM

SYSTEM_PROMPT = """You are Dawrek (دورك), the friendly assistant of a clinic's smart queue in Tunisia.
{clinic}You help patients waiting in line: their place in the queue, wait times, required documents,
appointments and available services.

LANGUAGE: Reply ONLY in {lang_name}. Match the patient's language and script exactly, even if the
reference information below is written in another language.

RULES:
- Use ONLY the live ticket status and the reference information below. Never invent numbers, prices or rules.
- If you don't know, say so and suggest asking the reception desk.
- Never give medical advice or diagnoses. For anything that sounds urgent, tell them to go to the
  emergency department or call SAMU at {emergency}.
- Be warm and short: 1-3 sentences, plain words, no markdown headings.

LIVE TICKET STATUS:
{live}

REFERENCE INFORMATION:
{kb}

REMEMBER: answer ONLY in {lang_name}."""


class Assistant:
    def __init__(self) -> None:
        self.client = None
        key = os.getenv("GROQ_API_KEY", "").strip()
        if key:
            from groq import Groq
            self.client = Groq(api_key=key, timeout=20, max_retries=0)  # fail fast, then try the next model

    @property
    def ai_enabled(self) -> bool:
        return self.client is not None

    def reply(self, message: str, ticket: dict | None = None, history: list[dict] | None = None) -> dict:
        lang = detect_language(message)

        if is_emergency(message):
            return {"reply": EMERGENCY_REPLY[lang].format(n=EMERGENCY_NUMBER), "lang": lang, "mode": "safety",
                    "intent": "emergency"}

        intent = detect_intent(message)
        if self.client:
            try:
                return {"reply": self._ask_llm(message, lang, ticket, history or []), "lang": lang, "mode": "ai",
                        "intent": intent}
            except Exception as exc:  # network, quota, bad key: degrade, don't break the demo
                log.warning("Groq call failed, using offline answer: %s", exc)

        return {"reply": offline_answer(message, lang, ticket), "lang": lang, "mode": "offline", "intent": intent}

    def transcribe(self, audio: bytes, content_type: str) -> str:
        """Speech to text with Groq Whisper. Raises if the AI is disabled or the call fails."""
        if not self.client:
            raise RuntimeError("Voice needs GROQ_API_KEY")
        ext = AUDIO_EXTENSIONS.get(content_type.split(";")[0].strip().lower(), "webm")
        result = self.client.audio.transcriptions.create(
            file=(f"question.{ext}", audio), model=WHISPER_MODEL, prompt=WHISPER_PROMPT,
            response_format="json", temperature=0,
        )
        return result.text.strip()

    def _ask_llm(self, message: str, lang: str, ticket: dict | None, history: list[dict]) -> str:
        # Arabizi gets the Latin-script (French) reference so the model transliterates instead of copying Arabic.
        section = "fr" if lang == "arabizi" else KB_SECTION_FOR[lang]
        topics = TOPICS_FOR_INTENT.get(detect_intent(message), list(KB))  # unclear question: send everything
        kb_text = "\n\n".join(f"[{topic}]\n{KB[topic].get(section, '')}" for topic in topics)
        live = describe_ticket(ticket, "en") or "The patient has no ticket yet. They can take one in the app."
        clinic = f"The clinic is called {CLINIC['name']}.\n" if CLINIC["name"] else ""
        system = SYSTEM_PROMPT.format(lang_name=LANG_NAMES[lang], emergency=EMERGENCY_NUMBER, live=live, kb=kb_text,
                                      clinic=clinic)

        messages = [{"role": "system", "content": system}]
        for turn in history[-6:]:
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                messages.append({"role": turn["role"], "content": str(turn["content"])[:1000]})
        messages.append({"role": "user", "content": message})

        text = self._complete(messages)
        if lang == "arabizi" and ARABIC_CHARS.search(text):
            # Models drift back into Arabic script on longer Arabizi answers: one rewrite pass fixes it.
            text = self._complete(messages + [
                {"role": "assistant", "content": text},
                {"role": "user", "content": "Rewrite your answer in Tunisian Arabizi using ONLY Latin letters and "
                                            "numbers (no Arabic script). Same meaning, same length."},
            ])
        return text

    def _complete(self, messages: list[dict]) -> str:
        from groq import RateLimitError

        for model in [GROQ_MODEL, *FALLBACK_MODELS]:
            effort = next((v for prefix, v in REASONING.items() if model.startswith(prefix)), None)
            try:
                response = self.client.chat.completions.create(
                    model=model, messages=messages, temperature=0.2, max_tokens=1024,
                    extra_body={"reasoning_effort": effort} if effort else None,
                )
            except RateLimitError:
                log.info("%s is at its free-tier limit, trying the next model", model)
                continue
            text = (response.choices[0].message.content or "").strip()
            if text:
                return text
        raise RuntimeError("all models busy or empty")
