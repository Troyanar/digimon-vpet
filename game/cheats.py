"""Cheat-Menü zum Testen (nur für den Admin).

Jede Cheat-Aktion markiert das Digimon als ``cheated`` – so sieht man z. B. im
Admin-Bereich, wer nachgeholfen hat.
"""
from . import data
from . import pet as P

# Werte, die man direkt setzen darf: (kleinster, größter Wert)
SETTABLE = {
    "hunger": (0, P.MAX_HEARTS), "strength": (0, P.MAX_HEARTS), "weight": (0, 99),
    "poop": (0, P.MAX_POOP), "mistakes": (0, 99), "mistakes_total": (0, P.MAX_MISTAKES - 1),
    "trainings": (0, 99), "overfeeds": (0, 99), "battles_stage": (0, 99), "wins_stage": (0, 99),
}


def _reset_stage(pet, now):
    pet["stage_since"] = now
    pet["mistakes"] = pet["trainings"] = pet["overfeeds"] = 0
    pet["battles_stage"] = pet["wins_stage"] = 0
    pet["skills"] = {s: 0 for s in P.SKILLS}
    pet["hunger_tick"] = pet["strength_tick"] = pet["poop_tick"] = 0
    for key in ("call_hunger", "call_strength", "call_light"):
        pet[key] = None


def _bring_back(pet, now):
    """Lebendig und ohne tödliche Uhren (sonst stirbt es gleich wieder)."""
    pet["alive"], pet["death_cause"] = True, None
    pet.pop("died", None)
    pet["hunger"] = max(pet["hunger"], 2)
    pet["strength"] = max(pet["strength"], 2)
    pet["sick"] = pet["injured"] = False
    pet["sick_since"] = pet["injured_since"] = pet["starving_since"] = None
    pet["mistakes_total"] = min(pet["mistakes_total"], P.MAX_MISTAKES - 5)
    pet["last"] = now
    for key in ("call_hunger", "call_strength", "call_light"):
        pet[key] = None


def _int(value, lo, hi):
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError, OverflowError):
        raise P.Refused("Bitte eine Zahl eingeben.")


def amount(value):
    """Wie viele Items auf einmal (Cheat)."""
    return _int(value, 1, 99)


def set_day(pet, on):
    """Konto-Schalter "Immer Tag": das Digimon schläft nicht (schläft es gerade, wacht es auf).
    Liefert True, wenn sich etwas geändert hat."""
    if bool(pet.get("no_sleep")) == on:
        return False
    pet["no_sleep"] = on
    if on:
        pet["cheated"] = True
        if pet["asleep"]:
            pet["asleep"], pet["light"], pet["nap"] = False, True, False
            pet["call_light"] = None
    return True


def apply(pet, op, body, now):
    """Führt einen Cheat aus und liefert eine Meldung."""
    if op == "warp":
        minutes = _int(body.get("minutes"), 1, 7 * 24 * 60)
        if not pet["alive"]:
            raise P.Refused("Ein totes Digimon kann nicht vorspulen. Erst wiederbeleben.")
        if pet.get("frozen"):
            raise P.Refused("Im Kühlschrank steht die Zeit still – erst auftauen.")
        # alle Zeitpunkte zurückschieben = so tun, als wäre man so lange weg gewesen
        P.shift_times(pet, -minutes, logs=True)
        P.advance(pet, now)
        msg = f"{minutes} Minuten vorgespult."
    elif op == "evolve_now":
        if not pet["alive"]:
            raise P.Refused("Erst wiederbeleben.")
        if pet["stage"] == "Egg":
            pet["stage_since"] = now - P.STAGE_TIME["Egg"]
            P._step(pet, now)          # Ei-Schritt: schlüpft sofort
            msg = f"Geschlüpft: {P.display_name(pet)}."
        else:
            evo = P.next_form(pet)
            if not evo:
                raise P.Refused("Keine nächste Form passt. Setz die Werte (z. B. Kämpfe/Siege) passend.")
            P._evolve(pet, evo, now)
            msg = f"Digitiert zu {P.display_name(pet)}."
    elif op == "set":
        values = body.get("values") or {}
        if not isinstance(values, dict):
            raise P.Refused("Ungültige Werte.")
        for key, val in values.items():
            if key in SETTABLE:
                pet[key] = _int(val, *SETTABLE[key])
            elif key in P.SKILLS:                       # Kraft / Tempo / Verteidigung
                P.skills(pet)[key] = _int(val, 0, P.SKILL_CAP)
        pet["mistakes_total"] = min(P.MAX_MISTAKES - 1, max(pet["mistakes_total"], pet["mistakes"]))
        msg = "Werte gesetzt."
    elif op == "status":
        what = body.get("what")
        if what == "sick":
            pet["sick"], pet["sick_since"] = True, now
        elif what == "injured":
            pet["injured"], pet["injured_since"] = True, now
        elif what == "heal":
            pet["sick"] = pet["injured"] = False
            pet["sick_since"] = pet["injured_since"] = None
        elif what == "poop":
            pet["poop"] = min(P.MAX_POOP, pet["poop"] + 1)
        elif what == "calls":
            for key in ("call_hunger", "call_strength", "call_light"):
                pet[key] = None
            pet["hunger"] = max(pet["hunger"], 1)
            pet["strength"] = max(pet["strength"], 1)
            pet["light"] = not pet["asleep"]
        elif what == "full":
            pet["hunger"] = pet["strength"] = P.MAX_HEARTS
        else:
            raise P.Refused("Unbekannter Zustand.")
        msg = "Zustand geändert."
    elif op == "flags":
        for key in ("immortal", "no_sleep"):
            if key in body:
                pet[key] = bool(body[key])
        if pet.get("no_sleep") and pet["asleep"]:
            pet["asleep"], pet["light"] = False, True
        msg = "Schalter gesetzt."
    elif op == "become":
        line, dex = body.get("line"), body.get("dex")
        if line not in data.LINES:
            raise P.Refused("Diese Ei-Sorte gibt es nicht.")
        try:
            dex = int(dex)
        except (TypeError, ValueError, OverflowError):
            raise P.Refused("Bitte ein Digimon wählen.")
        if not any(e["line"] == line and e["to"] == dex for e in data.EVOLUTIONS):
            raise P.Refused("Dieses Digimon gehört nicht zu dieser Linie.")
        pet["line"], pet["dex"] = line, dex
        pet["stage"] = data.DIGIMON[dex]["stage"]
        if not pet["alive"]:
            _bring_back(pet, now)
        for key in ("battle", "scout", "expedition", "nap"):   # laufende Sachen beenden
            pet.pop(key, None)
        pet["asleep"] = False
        pet["light"] = True
        pet["weight"] = max(pet["weight"], P.BASE_WEIGHT[pet["stage"]])
        _reset_stage(pet, now)
        msg = f"Verwandelt in {P.display_name(pet)}."
    elif op == "revive":
        _bring_back(pet, now)
        msg = f"{P.display_name(pet)} lebt wieder!"
    else:
        raise P.Refused("Unbekannter Cheat.")

    pet["cheated"] = True
    P._log(pet, now, f"Cheat: {msg}")
    return msg
