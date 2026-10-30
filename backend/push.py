"""Phone alerts with Web Push: "almost your turn" and "your turn, desk 2", even with the phone locked.

Free and standard: the browser gives us a subscription, we send an encrypted message through the
browser vendor's push service (Google, Mozilla, Apple). Works on Android in any browser and on
iPhone once Dawrek is added to the home screen (iOS 16.4+).

The keys come from VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY. Without them a fresh pair is made at
startup, which is fine because subscriptions, like tickets, only live as long as the process.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import threading

log = logging.getLogger("dawrek.push")

SOON_AHEAD = 2  # "almost your turn" when this many people or fewer are ahead
# Contact for the push services: a mailto: or a bare https:// origin (no path). Render sets RENDER_EXTERNAL_URL.
SUBJECT = os.getenv("VAPID_SUBJECT") or os.getenv("RENDER_EXTERNAL_URL") or "https://github.com"

MESSAGES = {
    "called": {
        "tn": ("🔔 دورك توا! {number}", "امشي للشباك {desk}"),
        "ar": ("🔔 حان دورك! {number}", "تفضّل إلى الشباك {desk}"),
        "fr": ("🔔 C'est votre tour ! {number}", "Présentez-vous au guichet {desk}"),
        "en": ("🔔 It's your turn! {number}", "Please go to desk {desk}"),
    },
    "soon": {
        "tn": ("⏳ قرب دورك ({number})", "قدامك {ahead}. ارجع للبلاصة توا."),
        "ar": ("⏳ اقترب دورك ({number})", "أمامك {ahead}. يرجى العودة إلى قاعة الانتظار."),
        "fr": ("⏳ Bientôt votre tour ({number})", "{ahead} personne(s) avant vous. Revenez en salle d'attente."),
        "en": ("⏳ Almost your turn ({number})", "{ahead} ahead of you. Please head back to the waiting room."),
    },
}


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class PushNotifier:
    def __init__(self) -> None:
        self.subscriptions: dict[str, dict] = {}  # ticket id -> {"sub": ..., "lang": ...}
        self.sent: set[tuple[str, str]] = set()  # (ticket id, event key) already delivered
        self._lock = threading.Lock()
        self.public_key, self._private_key = self._keys()

    @property
    def enabled(self) -> bool:
        return bool(self.public_key)

    def _keys(self) -> tuple[str, object]:
        public, private = os.getenv("VAPID_PUBLIC_KEY", "").strip(), os.getenv("VAPID_PRIVATE_KEY", "").strip()
        if public and private:
            return public, private
        try:
            from cryptography.hazmat.primitives import serialization
            from py_vapid import Vapid01
        except ImportError:  # pywebpush not installed: alerts off, the rest of the app works
            log.warning("pywebpush is not installed: phone alerts are off")
            return "", None
        vapid = Vapid01()
        vapid.generate_keys()
        raw = vapid.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        return _b64(raw), vapid

    def subscribe(self, ticket_id: str, subscription: dict, lang: str) -> None:
        with self._lock:
            self.subscriptions[ticket_id] = {"sub": subscription, "lang": lang if lang in MESSAGES["called"] else "tn"}

    def unsubscribe(self, ticket_id: str) -> None:
        with self._lock:
            self.subscriptions.pop(ticket_id, None)

    def notify_queue(self, queue, service: str) -> None:
        """After the line moved: alert the called patients and the ones who are next."""
        for t in queue.snapshot_service(service):
            if t["id"] not in self.subscriptions:
                continue
            if t["status"] == "called":
                self.send(t["id"], "called", f"called:{t['desk']}:{t['no_shows']}", number=t["number"], desk=t["desk"])
            elif t["status"] == "waiting" and t["people_ahead"] <= SOON_AHEAD:
                self.send(t["id"], "soon", f"soon:{t['no_shows']}", number=t["number"], ahead=t["people_ahead"])

    def send(self, ticket_id: str, kind: str, event: str, force: bool = False, **fields) -> bool:
        """Deliver one alert, once per event unless forced (a staff recall)."""
        with self._lock:
            entry = self.subscriptions.get(ticket_id)
            if not entry or (not force and (ticket_id, event) in self.sent):
                return False
            self.sent.add((ticket_id, event))
        title, body = MESSAGES[kind][entry["lang"]]
        payload = {"title": title.format(**fields), "body": body.format(**fields), "tag": f"dawrek-{ticket_id}",
                   "urgent": kind == "called"}
        try:
            from pywebpush import WebPushException, webpush
        except ImportError:
            return False
        try:
            webpush(entry["sub"], json.dumps(payload, ensure_ascii=False), vapid_private_key=self._private_key,
                    vapid_claims={"sub": SUBJECT}, ttl=600, timeout=10)
            return True
        except WebPushException as exc:
            status = getattr(exc.response, "status_code", None)
            if status in (404, 410):  # the phone unsubscribed or the browser data was cleared
                self.unsubscribe(ticket_id)
            log.warning("Push to %s failed: %s", ticket_id[:8], exc)
        except Exception as exc:  # network trouble must never break a staff action
            log.warning("Push to %s failed: %s", ticket_id[:8], exc)
        return False
