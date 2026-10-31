"""Freunde per Freundescode.

Jedes Konto hat einen eigenen Freundescode (meta "friendcode:<owner>", rückwärts
"friendcode_owner:<CODE>"). Wer den Code eines anderen eingibt, ist mit ihm befreundet –
in beide Richtungen (meta "friends:<owner>" = Liste von Konto-IDs). Den Code gibt man nur
Leuten, mit denen man spielen will; wer ihn nicht mehr weitergeben will, holt sich einen
neuen. Herausfordern, Tauschen und Jogress gehen nur mit Freunden – und nur Freunde
sehen, welche Digimon man hat (``profile``).
"""
import secrets

from . import pet as P
from .i18n import T

ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # ohne 0/O, 1/I/L – gut abzutippen
MAX_FRIENDS = 100


def _new_code():
    raw = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return f"{raw[:4]}-{raw[4:]}"


def _norm(code):
    raw = "".join(ch for ch in str(code or "").upper() if ch.isalnum())
    return f"{raw[:4]}-{raw[4:]}" if len(raw) == 8 else None


def code(store, owner):
    """Freundescode des Kontos (wird beim ersten Mal angelegt)."""
    owner = str(owner)
    value = store.get_meta(f"friendcode:{owner}", None)
    if not value:
        value = new_code(store, owner)
    return value


def new_code(store, owner):
    """Neuen Code ausstellen – der alte gilt dann nicht mehr. Freunde bleiben Freunde."""
    owner = str(owner)
    old = store.get_meta(f"friendcode:{owner}", None)
    value = _new_code()
    while store.get_meta(f"friendcode_owner:{value}", None):
        value = _new_code()
    if old:
        store.set_meta(f"friendcode_owner:{old}", None)
    store.set_meta(f"friendcode:{owner}", value)
    store.set_meta(f"friendcode_owner:{value}", owner)
    return value


def ids(store, owner):
    return {str(i) for i in (store.get_meta(f"friends:{owner}", []) or [])}


def are_friends(store, a, b):
    return str(b) in ids(store, str(a))


def _save(store, owner, values):
    store.set_meta(f"friends:{owner}", sorted(values, key=int))


def add(store, me, friend_code):
    """Freund per Code hinzufügen (beidseitig). Liefert die Meldung."""
    value = _norm(friend_code)
    other = store.get_meta(f"friendcode_owner:{value}", None) if value else None
    me_id = str(me["id"])
    target = next((u for u in store.all_users() if str(u["id"]) == other), None) if other else None
    if not target:
        raise P.Refused(T("Diesen Freundescode gibt es nicht."))
    if other == me_id:
        raise P.Refused(T("Das ist dein eigener Freundescode."))
    mine = ids(store, me_id)
    if other in mine:
        raise P.Refused(T("{name} ist schon dein Freund.", name=target["name"]))
    if len(mine) >= MAX_FRIENDS:
        raise P.Refused(T("Mehr als {n} Freunde gehen nicht.", n=MAX_FRIENDS))
    _save(store, me_id, mine | {other})
    _save(store, other, ids(store, other) | {me_id})
    return T("{name} ist jetzt dein Freund!", name=target["name"])


def remove(store, me, name):
    """Freundschaft beenden (beidseitig)."""
    me_id = str(me["id"])
    target = store.user_by_name(str(name or ""))
    if not target or str(target["id"]) not in ids(store, me_id):
        raise P.Refused(T("{name} ist nicht dein Freund.", name=str(name or "?")))
    other = str(target["id"])
    _save(store, me_id, ids(store, me_id) - {other})
    _save(store, other, ids(store, other) - {me_id})
    return T("{name} ist nicht mehr dein Freund.", name=target["name"])


def users(store, owner):
    """Die Freunde als Konten (gelöschte Konten fallen raus)."""
    mine = ids(store, str(owner))
    return [u for u in store.all_users() if str(u["id"]) in mine]


def check(store, me, target):
    """Refused, wenn `target` nicht befreundet ist (oder es ihn nicht gibt)."""
    if not target or not are_friends(store, me["id"], target["id"]):
        raise P.Refused(T("Das geht nur mit Freunden. Tauscht eure Freundescodes aus (Einstellungen → Freunde)."))


def _card(pet):
    """Ein Digimon/Ei zum Anschauen – bewusst ohne Werte, Reisen oder Rückkehrzeiten."""
    egg = pet["stage"] == "Egg"
    return {"name": P.display_name(pet), "nickname": None if egg else pet.get("name"),
            "dex": None if egg else pet["dex"], "stage": pet["stage"], "stage_de": P.stage_name(pet["stage"])}


def profile(store, me, name):
    """Was ein Freund hat: Partner, Sammlung, Digidex, Erfolge, Siege – nur für Freunde."""
    from . import progress
    target = store.user_by_name(str(name or ""))
    check(store, me, target)
    owner = str(target["id"])
    pets = store.all_pets(owner)
    active = next((p for p in pets if p["active"] and p.get("alive")), None)
    box = sorted((p for p in pets if not p["active"] and p.get("in_box") and p.get("alive")), key=lambda p: p["id"])
    stats = progress.stats(store, owner)
    return {
        "name": target["name"],
        "partner": {**_card(active), "wins": active.get("wins", 0), "battles": active.get("battles", 0)} if active else None,
        "box": [_card(p) for p in box if p["stage"] != "Egg"],
        "eggs": [_card(p) for p in box if p["stage"] == "Egg"],
        "dex": len(progress.sync(store, owner, pets)), "dex_total": len(progress.COLLECTABLE),
        "achievements": len(store.get_meta(f"ach:{owner}", []) or []), "achievements_total": len(progress.ACHIEVEMENTS),
        "wins": stats["wins"], "pvp_wins": stats["pvp_wins"],
    }
