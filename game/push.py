"""Web-Push für geschlossene Apps; Geräte bleiben an ihre Anmeldung gebunden."""
import base64
import copy
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

from . import i18n
from .i18n import T
from .store import token_hash, SESSION_DAYS

try:
    from pywebpush import webpush, WebPushException
    from py_vapid import Vapid02
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
except ImportError:
    webpush = None

log = logging.getLogger(__name__)
HOSTS = ("push.apple.com", "fcm.googleapis.com", "push.services.mozilla.com", "notify.windows.com")


def validate(sub):
    """Nur bekannte Push-Dienste und echte Browser-Schlüssel annehmen."""
    try:
        endpoint = sub["endpoint"]
        u = urlsplit(endpoint)
        host = (u.hostname or "").lower()
        if (len(endpoint) > 2048 or u.scheme != "https" or u.port not in (None, 443)
                or u.username or u.password or u.fragment
                or not any(host == h or host.endswith("." + h) for h in HOSTS)):
            raise ValueError
        keys = {k: sub["keys"][k] for k in ("p256dh", "auth")}
        raw = [base64.b64decode(keys[k] + "=" * (-len(keys[k]) % 4), altchars=b"-_", validate=True)
               for k in ("p256dh", "auth")]
        if len(raw[0]) != 65 or raw[0][0] != 4 or len(raw[1]) != 16:
            raise ValueError
        if webpush:
            ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), raw[0])
        return {"endpoint": endpoint, "keys": keys}
    except (KeyError, TypeError, ValueError, AttributeError):
        raise ValueError(T("Ungültige Push-Anmeldung.")) from None


def messages(before, now):
    """Neue Ereignisse statt wiederholter Erinnerungen; Partnerwechsel ist keine Digitation."""
    out = []

    def note(title, body, tag):
        out.append({"title": title, "body": body, "tag": tag, "url": "/"})

    old, pet = before.get("pet"), now.get("pet")
    if old and pet and old["id"] == pet["id"]:
        name = pet["name"]
        if old["alive"] and not pet["alive"]:
            note(T("{name} ist gestorben", name=name), pet.get("death_cause") or "", "death")
        elif old.get("totem") and not pet.get("totem") and pet["frozen"]:
            note(T("Das Schutz-Totem hat dein Digimon gerettet!"),
                 T("{name} wartet im Kühlschrank auf dich.", name=name), "totem")
        elif pet["alive"]:
            if old["stage"] == "Egg" and pet["stage"] != "Egg":
                note(T("Das Ei ist geschlüpft!"), T("Es ist ein {name}!", name=name), "evolve")
            elif old["dex"] != pet["dex"] and pet["stage"] != "Egg":
                note(T("Digitation!"), T("Dein Digimon ist jetzt {name}.", name=name), "evolve")
            if not pet["frozen"]:
                if pet["sick"] and not old["sick"]:
                    note(T("{name} ist krank!", name=name), T("Gib ihm schnell Medizin."), "sick")
                previous = {c["what"] for c in old["calls"]}
                fresh = {c["what"] for c in pet["calls"]} - previous
                if fresh:
                    note(T("{name} ruft dich!", name=name), T("Schau nach deinem Digimon."), "call")
            if pet.get("returned") and not old.get("returned"):
                note(T("{name} ist zurück vom Erkunden!", name=name), T("Deine Funde warten im Spiel."), "return")
    previous = set(before.get("trips", []))
    if set(now.get("trips", [])) - previous:
        note(T("Ein Sammlungs-Digimon ist zurück!"), T("Deine Funde warten im Spiel."), "box-return")
    return out


class Service:
    def __init__(self, store, snapshot):
        self.store, self.snapshot = store, snapshot
        self.key = None
        self.path = Path(store.db_path).parent / "vapid.pem"

    @property
    def available(self):
        return webpush is not None and os.environ.get("VPET_PUSH", "1") != "0"

    def public_key(self):
        if not self.available:
            return None
        if self.key is None:
            if self.path.exists():
                self.key = Vapid02.from_file(str(self.path))
            else:
                self.key = Vapid02()
                self.key.generate_keys()
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.key.save_key(str(self.path))
                self.path.chmod(0o600)
        raw = self.key.public_key.public_bytes(serialization.Encoding.X962,
                                               serialization.PublicFormat.UncompressedPoint)
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    def devices(self):
        return self.store.get_meta("push:devices", {})

    def valid_session(self, device):
        row = self.store.db.execute(
            "SELECT 1 FROM sessions s JOIN users u ON u.id=s.user_id "
            "WHERE s.token=? AND u.id=? AND u.banned=0 AND s.created>?",
            (device["session"], device["owner"], int(time.time()) - SESSION_DAYS * 86400)).fetchone()
        return bool(row)

    def subscribe(self, user, token, sub):
        sub = validate(sub)
        devices = self.devices()
        ident = hashlib.sha256(sub["endpoint"].encode()).hexdigest()
        if ident not in devices and sum(d["owner"] == user["id"] for d in devices.values()) >= 8:
            raise ValueError(T("Du kannst höchstens 8 Geräte für Mitteilungen anmelden."))
        devices[ident] = {"owner": user["id"], "session": token_hash(token), "sub": sub,
                          "memo": self.snapshot(user), "last_test": 0}
        self.store.set_meta("push:devices", devices)

    def remove(self, user, endpoint):
        devices = self.devices()
        devices = {k: d for k, d in devices.items()
                   if not (d["owner"] == user["id"] and d["sub"]["endpoint"] == endpoint)}
        self.store.set_meta("push:devices", devices)

    def send(self, device, notes, lang):
        self.public_key()
        for note in notes:
            try:
                webpush(device["sub"], json.dumps(i18n.localize(note, lang)),
                        vapid_private_key=self.key,
                        vapid_claims={"sub": os.environ.get("VPET_PUSH_CONTACT",
                                      "https://github.com")}, ttl=600, timeout=10)
            except WebPushException as exc:
                status = getattr(exc, "status_code", None)
                if status is None and getattr(exc, "response", None) is not None:
                    status = exc.response.status_code
                if status in (404, 410):
                    return False
                log.warning("Push-Dienst meldet Fehler %s", status)
                return None
            except Exception:
                log.warning("Push-Dienst ist nicht erreichbar.")
                return None
        return True

    def tick(self):
        """Netzwerk außerhalb der Spielstand-Sperre; abgemeldete Geräte entfernen."""
        if not self.available:
            return
        with self.store.lock:
            ids = list(self.devices())
        snapshots = {}
        for ident in ids:
            with self.store.lock:
                devices = self.devices()
                d = devices.get(ident)
                if not d:
                    continue
                if not self.valid_session(d):
                    devices.pop(ident)
                    self.store.set_meta("push:devices", devices)
                    continue
                user = self.store.user_by_id(d["owner"])
                if d["owner"] not in snapshots:
                    snapshots[d["owner"]] = self.snapshot(user)
                snap = snapshots[d["owner"]]
                if snap is None:
                    continue
                notes = messages(d["memo"] or {}, snap)
                lang = self.store.get_meta(f"lang:{d['owner']}", "de")
            result = self.send(d, notes, lang) if notes else True
            with self.store.lock:
                devices = self.devices()
                # Während des Sendens ausgeschaltet oder Konto gewechselt?
                if devices.get(ident) != d:
                    continue
                if result is False:
                    devices.pop(ident)
                elif result is True:
                    devices[ident]["memo"] = copy.deepcopy(snap)
                self.store.set_meta("push:devices", devices)

    def run(self, stop):
        while not stop.wait(20):
            try:
                self.tick()
            except Exception:
                log.exception("Push-Prüfung fehlgeschlagen.")
