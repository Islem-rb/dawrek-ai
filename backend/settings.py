"""Clinic settings edited from the /settings page: name, desks, services, assistant knowledge.

Saved as JSON (data/clinic_settings.json by default, or SETTINGS_FILE). Hosts with a temporary disk,
like Render's free plan, lose the file on restart, so the page can also export and import it.
"""
from __future__ import annotations

import copy
import json
import logging
import os
import threading
from pathlib import Path

from backend import assistant
from backend.queue_engine import SERVICES

log = logging.getLogger("dawrek.settings")

SETTINGS_FILE = Path(os.getenv("SETTINGS_FILE", Path(__file__).resolve().parent.parent / "data" / "clinic_settings.json"))
MAX_DESKS = 20
KB_LANGS = ("tn", "ar", "fr")
MAX_KB_CHARS = 4000  # per topic and language: keeps prompts inside the free Groq quota

DEFAULT_SERVICES = copy.deepcopy(SERVICES)
DEFAULT_KB = copy.deepcopy(assistant.KB)


class ClinicSettings:
    def __init__(self, path: Path = SETTINGS_FILE):
        self.path = path
        self.clinic_name = ""
        self.desks = 6
        self._lock = threading.Lock()

    # ---- read ---------------------------------------------------------

    def public(self) -> dict:
        """What every page may see."""
        return {"clinic_name": self.clinic_name, "desks": self.desks}

    def full(self) -> dict:
        """Everything the settings page edits (staff only)."""
        return {
            **self.public(),
            "services": {k: {"enabled": v.get("enabled", True), "avg_minutes": v["avg_minutes"]} for k, v in SERVICES.items()},
            "knowledge": {topic: {lang: texts.get(lang, "") for lang in KB_LANGS} for topic, texts in assistant.KB.items()},
        }

    # ---- write --------------------------------------------------------

    def update(self, data: dict) -> dict:
        """Validate a partial update, then apply it live and save it. Raises ValueError on bad input."""
        with self._lock:
            name = str(data.get("clinic_name", self.clinic_name) or "").strip()[:60]
            desks = int(data.get("desks", self.desks))
            if not 1 <= desks <= MAX_DESKS:
                raise ValueError(f"desks must be between 1 and {MAX_DESKS}")
            services = {k: dict(v) for k, v in SERVICES.items()}
            for key, cfg in (data.get("services") or {}).items():
                if key not in services:
                    raise ValueError(f"unknown service {key}")
                if "avg_minutes" in cfg:
                    minutes = int(cfg["avg_minutes"])
                    if not 1 <= minutes <= 180:
                        raise ValueError("minutes per patient must be between 1 and 180")
                    services[key]["avg_minutes"] = minutes
                if "enabled" in cfg:
                    services[key]["enabled"] = bool(cfg["enabled"])
            if not any(s.get("enabled", True) for s in services.values()):
                raise ValueError("at least one service must stay open")
            knowledge = []
            for topic, texts in (data.get("knowledge") or {}).items():
                if topic not in assistant.KB:
                    raise ValueError(f"unknown topic {topic}")
                for lang, text in texts.items():
                    if lang not in KB_LANGS:
                        raise ValueError(f"unknown language {lang}")
                    knowledge.append((topic, lang, str(text).strip()[:MAX_KB_CHARS]))

            self.clinic_name, self.desks = name, desks
            assistant.CLINIC["name"] = name
            for key, cfg in services.items():
                SERVICES[key].update(cfg)
            for topic, lang, text in knowledge:
                assistant.KB[topic][lang] = text
            self._save()
            return self.full()

    def reset(self) -> dict:
        with self._lock:
            self.clinic_name, self.desks = "", 6
            assistant.CLINIC["name"] = ""
            for key, cfg in DEFAULT_SERVICES.items():
                SERVICES[key].clear()
                SERVICES[key].update(copy.deepcopy(cfg))
            for topic, texts in DEFAULT_KB.items():
                assistant.KB[topic] = copy.deepcopy(texts)
            try:
                self.path.unlink(missing_ok=True)
            except OSError as exc:
                log.warning("Could not delete %s: %s", self.path, exc)
            return self.full()

    def load(self) -> None:
        if not self.path.exists():
            return
        try:
            self.update(json.loads(self.path.read_text(encoding="utf-8")))
            log.info("Loaded clinic settings from %s", self.path)
        except (ValueError, OSError, TypeError) as exc:
            log.warning("Ignoring %s: %s", self.path, exc)

    def _save(self) -> None:
        try:
            self.path.write_text(json.dumps(self.full(), ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as exc:  # read-only disk: settings still apply until restart
            log.warning("Could not save %s: %s", self.path, exc)
