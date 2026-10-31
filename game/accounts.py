"""Konten: Registrieren (mit Einladungscode), Anmelden, Abmelden.

Das Prüfen von Passwörtern ist absichtlich langsam (PBKDF2). Der Server ruft
deshalb die Einzelschritte auf (nachschauen -> Passwort prüfen -> Sitzung
anlegen) und hält seine Datenbank-Sperre nur für die schnellen Schritte, damit
falsche Anmeldungen nicht das ganze Spiel ausbremsen. `register()` und
`login()` fassen die Schritte für Werkzeuge und Tests zusammen.
"""
import hashlib
import hmac
import os
import re
import secrets

from . import settings
from .i18n import T

ITERATIONS = 200_000
NAME_RE = re.compile(r"^[A-Za-z0-9_\-äöüÄÖÜß]{3,20}$")
MIN_PASSWORD = 6
MAX_PASSWORD = 200
_DUMMY_SALT = "00" * 16


class AuthError(Exception):
    """Fehlermeldung für den Spieler."""


def _text(value):
    """Nur echte Texte zulassen (keine Zahlen, Listen ... aus dem Netz)."""
    return value.strip() if isinstance(value, str) else ""


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf8"), bytes.fromhex(salt),
                               ITERATIONS).hex()


def new_password_hash(password):
    """(hash, salt) für ein neues Passwort – langsam, also ohne Sperre aufrufen."""
    salt = secrets.token_hex(16)
    return _hash(password, salt), salt


def password_ok(user, password):
    """Passwort prüfen. Bei unbekanntem Namen wird trotzdem gerechnet, damit
    man an der Antwortzeit nicht erkennt, welche Namen es gibt."""
    password = password if isinstance(password, str) else ""
    if not user:
        _hash(password[:MAX_PASSWORD], _DUMMY_SALT)
        return False
    return hmac.compare_digest(user["pw_hash"], _hash(password[:MAX_PASSWORD], user["salt"]))


def invite_code(store):
    """Der aktuelle Einladungscode (wird beim ersten Mal erzeugt)."""
    code = store.get_meta("invite_code")
    if not code:
        code = new_invite_code(store)
    return code


def new_invite_code(store):
    code = "-".join(secrets.token_hex(2).upper() for _ in range(3))   # z. B. 4F2A-91BC-07DE
    store.set_meta("invite_code", code)
    return code


# ---------------------------------------------------------------- Registrieren

def register_check(store, name, password, invite):
    """Schneller Teil vor dem Registrieren. Liefert den bereinigten Namen."""
    name = _text(name)
    if not NAME_RE.match(name):
        raise AuthError(T("Name: 3–20 Zeichen, nur Buchstaben, Zahlen, - und _."))
    if not isinstance(password, str) or not MIN_PASSWORD <= len(password) <= MAX_PASSWORD:
        raise AuthError(T("Passwort: mindestens {n} Zeichen.", n=MIN_PASSWORD))
    first = store.user_count() == 0
    if first and os.environ.get("VPET_PUBLIC"):
        # online soll nicht der erste Besucher automatisch Admin werden
        raise AuthError(T("Das erste Admin-Konto bitte mit tools/admin_account.py anlegen."))
    mode = settings.CURRENT["registration"]
    if not first and settings.CURRENT["maintenance"]:
        raise AuthError(T("Wartungsarbeiten – bitte später wieder versuchen."))
    if not first and mode == "closed":
        raise AuthError(T("Neue Konten sind gerade nicht möglich."))
    if not first and mode == "invite" and _text(invite).upper() != invite_code(store):
        raise AuthError(T("Der Einladungscode stimmt nicht."))
    if store.user_by_name(name):
        raise AuthError(T("Diesen Namen gibt es schon."))
    return name


def register_finish(store, name, pw_hash, salt):
    """Konto anlegen (nach register_check und new_password_hash)."""
    if store.user_by_name(name):                    # inzwischen vergeben?
        raise AuthError(T("Diesen Namen gibt es schon."))
    first = store.user_count() == 0
    user_id = store.add_user(name, pw_hash, salt, is_admin=first)
    if first:
        store.adopt_local_pets(user_id)
    return start_session(store, user_id)


def register(store, name, password, invite):
    name = register_check(store, name, password, invite)
    return register_finish(store, name, *new_password_hash(password))


# ---------------------------------------------------------------- Anmelden

def login_lookup(store, name):
    return store.user_by_name(_text(name)) if _text(name) else None


def login_finish(store, user):
    if user.get("banned"):
        raise AuthError(T("Dieses Konto ist gesperrt."))
    if settings.CURRENT["maintenance"] and not user["is_admin"]:
        raise AuthError(T("Wartungsarbeiten – bitte später wieder versuchen."))
    return start_session(store, user["id"])


def login(store, name, password):
    user = login_lookup(store, name)
    if not password_ok(user, password):
        raise AuthError(T("Name oder Passwort falsch."))
    return login_finish(store, user)


# ---------------------------------------------------------------- Passwörter

def change_password(store, user_id, old, new, token=None):
    """Eigenes Passwort ändern. Andere Geräte werden abgemeldet."""
    user = store.user_by_id(user_id)
    if not password_ok(user, old):
        raise AuthError(T("Das alte Passwort stimmt nicht."))
    if not isinstance(new, str) or not MIN_PASSWORD <= len(new) <= MAX_PASSWORD:
        raise AuthError(T("Neues Passwort: mindestens {n} Zeichen.", n=MIN_PASSWORD))
    store.set_password(user_id, *new_password_hash(new))
    store.delete_user_sessions(user_id, keep=token)


def reset_password(store, name):
    """Admin: setzt ein Ersatz-Passwort und meldet den Spieler überall ab.
    Liefert das neue Passwort (zum Weitergeben)."""
    user = store.user_by_name(_text(name))
    if not user:
        raise AuthError("Diesen Spieler gibt es nicht.")
    # gut vorlesbar: keine 0/O, 1/l
    alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
    temp = "".join(secrets.choice(alphabet) for _ in range(8))
    store.set_password(user["id"], *new_password_hash(temp))
    store.delete_user_sessions(user["id"])
    return temp


def start_session(store, user_id):
    token = secrets.token_urlsafe(32)
    store.add_session(token, user_id)
    return token
