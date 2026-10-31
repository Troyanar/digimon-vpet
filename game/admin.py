"""Admin-Bereich: Spieler verwalten und Übersichten.

Alle Funktionen werfen P.Refused mit einer verständlichen Meldung, wenn etwas
nicht geht (z. B. sich selbst löschen oder den letzten Admin entfernen).
"""
import time

from . import accounts, cheats, collection, data, explore
from . import pet as P
from .i18n import T

ACTIONS = ("reset_pw", "make_admin", "remove_admin", "kick", "ban", "unban", "delete",
           "heal", "revive", "feed", "gift_item", "gift_egg")


def _pet_info(pet):
    if not pet:
        return None
    return {"name": P.display_name(pet), "stage_de": P.STAGE_DE[pet["stage"]], "alive": pet["alive"],
            "sick": pet.get("sick") or pet.get("injured"), "hunger": pet["hunger"], "strength": pet["strength"],
            "frozen": bool(pet.get("frozen")), "away": bool(pet.get("expedition")),
            "death_cause": pet.get("death_cause")}


def users(store, now, online):
    """Alle Spieler mit Details für die Admin-Liste. `online(user_id)` -> bool."""
    out = []
    for u in store.users_detail():
        pets = store.all_pets(str(u["id"]))
        active = next((p for p in pets if p["active"]), None)
        if active:
            P.advance(active, now)
            store.save_pet(active)
        out.append({
            "name": u["name"], "admin": bool(u["is_admin"]), "banned": bool(u["banned"]),
            "online": online(u["id"]), "created": u["created"], "last_seen": u["last_seen"],
            "partner": _pet_info(active),
            "box": sum(1 for p in pets if p.get("in_box")),
            "wins": sum(p.get("wins", 0) for p in pets), "battles": sum(p.get("battles", 0) for p in pets),
            "cheated": any(p.get("cheated") for p in pets),
        })
    return out


def user_action(store, me, name, action, params, now, add_item):
    """Führt eine Admin-Aktion an einem Spieler aus und liefert eine Meldung."""
    target = store.user_by_name(accounts._text(name))
    if not target:
        raise P.Refused("Diesen Spieler gibt es nicht.")
    if action not in ACTIONS:
        raise P.Refused("Unbekannte Aktion.")
    self_ = target["id"] == me["id"]
    who = target["name"]
    if action in ("remove_admin", "ban", "delete", "kick") and self_:
        raise P.Refused("Das kannst du nicht mit deinem eigenen Konto machen.")
    if action in ("remove_admin", "ban", "delete") and target["is_admin"] and store.admin_count() <= 1:
        raise P.Refused("Es muss mindestens ein Admin übrig bleiben.")

    if action == "reset_pw":
        temp = accounts.reset_password(store, who)
        return f"Neues Passwort für {who}: {temp}", {"password": temp}
    if action == "make_admin":
        store.set_flag(target["id"], "is_admin", True)
        return f"{who} ist jetzt Admin.", {}
    if action == "remove_admin":
        store.set_flag(target["id"], "is_admin", False)
        return f"{who} ist kein Admin mehr.", {}
    if action == "kick":
        store.delete_user_sessions(target["id"])
        return f"{who} wurde überall abgemeldet.", {}
    if action == "ban":
        store.set_flag(target["id"], "banned", True)
        store.delete_user_sessions(target["id"])
        return f"{who} ist gesperrt und wurde abgemeldet.", {}
    if action == "unban":
        store.set_flag(target["id"], "banned", False)
        return f"{who} ist wieder freigeschaltet.", {}
    if action == "delete":
        store.delete_user(target["id"])
        return f"Das Konto {who} wurde mit allen Digimon gelöscht.", {}

    owner = str(target["id"])
    if action == "gift_item":
        item = params.get("item")
        try:
            count = max(1, min(20, int(params.get("count") or 1)))
        except (TypeError, ValueError, OverflowError):
            raise P.Refused("Bitte eine Anzahl von 1 bis 20 angeben.")
        if item not in explore.ITEMS:
            raise P.Refused("Dieses Item gibt es nicht.")
        add_item(owner, item, count)
        return f"{who} hat {count}× {explore.ITEMS[item]['name']} bekommen.", {}
    if action == "gift_egg":
        line = params.get("line") or ""
        if line not in data.LINES:
            raise P.Refused("Diese Ei-Sorte gibt es nicht.")
        if not collection.store_egg(store, owner, line, now):
            raise P.Refused(f"Die Sammlung von {who} ist voll.")
        return f"{who} hat ein {data.LINES[line]['name']} in die Sammlung bekommen.", {}

    pet = store.active_pet(owner)
    if not pet:
        raise P.Refused(f"{who} hat gerade kein Digimon.")
    P.advance(pet, now)
    name_pet = P.display_name(pet)
    if action == "heal":
        pet["sick"] = pet["injured"] = False
        pet["sick_since"] = pet["injured_since"] = None
        message = T("{name} von {who} ist wieder gesund.", name=name_pet, who=who)
    elif action == "feed":
        pet["hunger"] = pet["strength"] = P.MAX_HEARTS
        message = T("{name} von {who} ist satt und stark.", name=name_pet, who=who)
    else:   # revive
        if pet["alive"]:
            raise P.Refused(f"{name_pet} lebt doch noch.")
        cheats._bring_back(pet, now)
        message = T("{name} von {who} lebt wieder!", name=name_pet, who=who)
    # das Tagebuch sehen auch die Spieler – deshalb zweisprachig
    P._log(pet, now, T("Der Admin hat geholfen: {message}", message=message))
    store.save_pet(pet)
    return message, {}


def overview(store, online_count, started, db_size_kb, backups):
    counts = store.counts()
    alive = eggs = dead = 0
    for (body,) in store.db.execute("SELECT data FROM pets"):
        if '"alive": false' in body:
            dead += 1
        elif '"stage": "Egg"' in body:
            eggs += 1
        else:
            alive += 1
    return {**counts, "online": online_count, "alive": alive, "eggs": eggs, "dead": dead,
            "uptime_min": int((time.time() - started) / 60), "db_kb": db_size_kb,
            "backups": len(backups), "last_backup": backups[0]["time"] if backups else None,
            "digimon_total": len(data.DIGIMON), "lines_total": len(data.LINES)}


def recent_diary(store, limit=60):
    """Die neuesten Tagebucheinträge aller Spieler (aktive Digimon)."""
    names = {str(u["id"]): u["name"] for u in store.users_detail()}
    entries = []
    for owner, name in names.items():
        pet = store.active_pet(owner)
        if pet:
            for e in pet.get("log", []):
                entries.append({"t": e["t"], "who": name, "text": e["text"]})
    entries.sort(key=lambda e: -e["t"])
    return entries[:limit]
