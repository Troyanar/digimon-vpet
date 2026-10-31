"""Kämpfe gegen wilde Digimon im Stil des Original-V-Pets.

Ablauf: ``scout`` (Gegner ansehen) -> ``fight`` (kostet 1 Herz Hunger + Kraft)
-> pro Runde ``shot`` (dein Angriff) und ``evade`` (Ausweichen vor dem
Gegner), bis einer keine Leben mehr hat.

Dein Angriff: oben oder unten (``aim``), gedrückt halten = laden (``charge``
0..2, über 1 = Überladen mit Risiko, ab 1,95 Mega-Schuss) – oder bei voller
Spezial-Leiste die Spezialattacke (``mash`` 0..1 = wie schnell gedrückt).
Der Browser spielt das Geschicklichkeitsspiel und meldet nur das Ergebnis.
"""
import math
import random

from . import data, settings
from . import pet as P
from .i18n import T

MAX_HP = 3                 # Treffer, die ein Digimon aushält
MAX_ROUNDS = 25           # danach entscheiden die Leben (gleich viele = unentschieden)
BATTLE_STAGES = ("Rookie", "Champion", "Armor", "Ultimate", "Mega")
STAGE_POWER = {"Rookie": 30, "Champion": 50, "Armor": 60, "Ultimate": 70, "Mega": 90}
BEATS = {("Vaccine", "Virus"), ("Virus", "Data"), ("Data", "Vaccine")}
INJURY_CHANCE = 0.35       # nach einer Niederlage
EGG_CHANCE = 0.12          # nach einem Sieg
TIMEOUT = 15               # Minuten, dann verfällt ein angefangener Kampf

SIDES = ("high", "low")    # oben / unten angreifen (und ausweichen)
POWER_AT = 0.85            # ab dieser Ladung ist es ein Power-Schuss
MEGA_AT = 1.95             # ab hier Mega-Schuss: 2 Schaden
GAP_BONUS = 0.20           # offene Seite ("Lücke!") +, gedeckte Seite -
OVERCHARGE_BONUS = 0.30    # Trefferchance pro Stufe Überladen
OVERCHARGE_RISK = 0.6      # Risiko unterbrochen zu werden pro Stufe Überladen
SPECIAL_MAX = 3            # Spezial-Leiste: so viele Treffer (ausgeteilt/eingesteckt)
SPECIAL_BASE, SPECIAL_MASH = 0.50, 0.45   # Trefferchance der Spezialattacke

# Persönlichkeiten wilder Digimon (Name: personality_name)
#   strong = Chance auf einen angekündigten starken Angriff (2 Schaden)
#   double = Chance auf einen zweiten Schuss, hp = Leben, evade = deine Trefferchance -,
#   risk = Überlade-Risiko +, sly = deckt so oft die Seite deines letzten Angriffs
PERSONALITIES = {
    "normal": {"strong": 0.15},                # erster Eintrag: rng.choice in Tests
    "aggressive": {"strong": 0.25, "double": 0.35},
    "armored": {"strong": 0.10, "hp": 4},
    "nimble": {"strong": 0.10, "evade": 0.08, "risk": 0.20},
    "sly": {"strong": 0.15, "sly": 0.70},
}

ATTR_DE = {"Vaccine": "Serum", "Data": "Daten", "Virus": "Virus", "Free": "Frei"}


def personality_name(key):
    names = {"normal": T("ruhig"), "aggressive": T("aggressiv"), "armored": T("gepanzert"),
             "nimble": T("flink"), "sly": T("listig")}
    return names.get(key, names["normal"])


def _personality_hint(key):
    """Satz für ``scout``: woran man den Gegner erkennt."""
    if key == "aggressive":
        return T("Es wirkt aggressiv – oft greift es zweimal an!")
    if key == "armored":
        return T("Es wirkt gepanzert – es hält 4 Treffer aus.")
    if key == "nimble":
        return T("Es wirkt flink – schwer zu treffen, nicht zu lange laden!")
    if key == "sly":
        return T("Es wirkt listig – es merkt sich, wo du angreifst.")
    return T("Es wirkt ruhig.")


def special_name(dex):
    """Name der Spezialattacke (aus dem Digidex) – oder einfach "Spezialattacke"."""
    return data.special_name(dex) or T("Spezialattacke")


def attribute(dex):
    return data.DIGIMON[dex]["attribute"]


def attr_bonus(mine, theirs):
    """+10 bei Vorteil, -10 bei Nachteil (Serum > Virus > Daten > Serum)."""
    if (mine, theirs) in BEATS:
        return 10
    if (theirs, mine) in BEATS:
        return -10
    return 0


def power(pet):
    """Kampfkraft: Stufe + Kraft-Herzen + Training (vor allem Kraft-Training),
    Übergewicht bremst."""
    value = (STAGE_POWER[pet["stage"]] + 5 * pet["strength"] + min(pet["trainings"], 20) // 4
             + P.skills(pet)["power"])
    if pet["weight"] > P.BASE_WEIGHT[pet["stage"]] + 15:
        value -= 5
    if pet.get("charm"):          # Glücksbringer aus dem Rucksack
        value += 15
    return value


def hit_chances(my_power, opp_power, bonus, quality, dodge=0.0, extra=0.0):
    """Trefferchancen (deine, gegnerische). `dodge` = Ausweichen durch Tempo-Training,
    `extra` = Zuschlag auf deine Chance (Lücke, Überladen ...)."""
    mine = 0.40 + 0.30 * quality + (my_power - opp_power + bonus) / 100 + extra
    theirs = 0.45 + (opp_power - my_power - bonus) / 100 - dodge
    return min(0.95, max(0.10, mine)), min(0.90, max(0.10, theirs))


def _number(value, low, high):
    """Zahl aus einer Anfrage, begrenzt auf low..high (Unsinn = low)."""
    try:
        x = float(value)
    except (TypeError, ValueError):
        return float(low)
    if not math.isfinite(x):
        return float(low)
    return min(float(high), max(float(low), x))


def parse_shot(value):
    """Eingabe eines Angriffs lesen (wild und gegen Freunde, nie ein Fehler):
    {"aim": "high"|"low", "charge": 0..2} oder {"special": true, "mash": 0..1}.
    Alte Form (Zahl oder {"quality": x}) = Schuss oben mit charge x (0..1)."""
    shot = {"aim": "high", "charge": 0.0, "special": False, "mash": 0.0}
    if isinstance(value, dict):
        if value.get("aim") in SIDES:
            shot["aim"] = value["aim"]
        if value.get("special") is True:
            shot.update(special=True, mash=_number(value.get("mash"), 0, 1))
        elif "charge" in value or "aim" in value:
            shot["charge"] = _number(value.get("charge"), 0, 2)
        else:
            shot["charge"] = _number(value.get("quality"), 0, 1)
    else:
        shot["charge"] = _number(value, 0, 1)
    return shot


def roll_attack(shot, my_power, opp_power, bonus, rng, guard=None, evade=0.0, risk=0.0):
    """Einen Angriff auswerten, ohne Schaden abzuziehen (wild und gegen Freunde).
    `shot` aus parse_shot, `guard` = gedeckte Seite (nur wilde Gegner),
    `evade`/`risk` = Persönlichkeit "flink"."""
    out = {"aim": shot["aim"], "special": shot["special"], "guard": None, "gap": False,
           "interrupted": False, "power": False, "mega": False, "hit": False, "damage": 0}
    if shot["special"]:
        # nicht ausweichbar, nicht zu decken
        chance = SPECIAL_BASE + SPECIAL_MASH * shot["mash"] + (my_power - opp_power + bonus) / 100
        chance = min(0.95, max(0.10, chance))
    else:
        charge = shot["charge"]
        over = max(0.0, charge - 1)                      # Überladen
        out["guard"] = guard
        if over > 0 and rng.random() < OVERCHARGE_RISK * over + risk:
            out["interrupted"] = True                    # Schuss fällt aus
            return out
        extra = OVERCHARGE_BONUS * over - evade
        if guard:
            out["gap"] = shot["aim"] != guard
            extra += GAP_BONUS if out["gap"] else -GAP_BONUS
        chance, _ = hit_chances(my_power, opp_power, bonus, min(charge, 1.0), extra=extra)
        out["power"], out["mega"] = charge >= POWER_AT, charge >= MEGA_AT
    out["hit"] = rng.random() < chance
    if out["hit"]:
        out["damage"] = 2 if out["mega"] or out["special"] else 1
    return out


def fill(gauge):
    """Spezial-Leiste +1 (für einen Treffer, ausgeteilt oder eingesteckt)."""
    return min(SPECIAL_MAX, gauge + 1)


def dodge(pet):
    return 0.012 * P.skills(pet)["speed"]                # bis -12 % Treffer für den Gegner


def max_hp(pet):
    d = P.skills(pet)["defense"]
    return MAX_HP + (d >= 8)                             # Verteidigung: ab 8 ein Leben mehr


def injury_chance(pet):
    return max(0.05, INJURY_CHANCE - 0.03 * P.skills(pet)["defense"])


def _can_battle(pet):
    name = P.display_name(pet)
    P._usable(pet)
    if pet["stage"] not in BATTLE_STAGES:
        raise P.Refused(T("{name} ist noch zu klein zum Kämpfen – ab Rookie geht's los.", name=name))
    if pet["asleep"]:
        raise P.Refused(T("{name} schläft gerade.", name=name))
    if pet["sick"] or pet["injured"]:
        raise P.Refused(T("{name} ist nicht fit genug zum Kämpfen. Erst Medizin!", name=name))
    if pet["hunger"] == 0 or pet["strength"] == 0:
        raise P.Refused(T("{name} ist zu hungrig oder zu schlapp zum Kämpfen.", name=name))


def _strength_word(diff):
    if diff >= 15:
        return T("viel stärker als deins")
    if diff >= 6:
        return T("etwas stärker als deins")
    if diff <= -15:
        return T("viel schwächer als deins")
    if diff <= -6:
        return T("etwas schwächer als deins")
    return T("ungefähr gleich stark")


def scout(pet, minute, rng=random, event=None):
    """Ein wildes Digimon derselben Stufe taucht auf. Läuft ein Event mit Geistern
    (game/events.py), ist der Gegner oft einer davon."""
    _can_battle(pet)
    if pet.get("battle"):
        raise P.Refused(T("Du bist schon in einem Kampf."))
    from . import events
    ghosts = events.ghosts(event, pet["stage"])
    ghost = bool(ghosts) and rng.random() < events.GHOST_CHANCE
    pool = ghosts if ghost else [dex for dex, d in data.WILD.items() if d["stage"] == pet["stage"]]
    opp = rng.choice(pool)
    opp_power = STAGE_POWER[pet["stage"]] + 5 * rng.randint(1, 4) + rng.randint(0, 10)
    trait = rng.choice(list(PERSONALITIES))
    pet["scout"] = {"dex": opp, "power": opp_power, "time": minute, "personality": trait}
    if ghost:
        pet["scout"]["ghost"] = event              # Event-Key

    bonus = attr_bonus(attribute(pet["dex"]), attribute(opp))
    name = data.DIGIMON[opp]["name"]
    attr = T(ATTR_DE[attribute(opp)]) if attribute(opp) in ATTR_DE else "–"
    hint = _strength_word(opp_power - power(pet) - bonus)
    text = T("Ein wildes {name} ({attr}) taucht auf! Es wirkt {hint}.", name=name, attr=attr, hint=hint)
    text += " " + _personality_hint(trait)
    if bonus > 0:
        text += " " + T("Dein Attribut hat Vorteil!")
    elif bonus < 0:
        text += " " + T("Achtung, Attribut-Nachteil!")
    if ghost:
        text += " " + T("Ein Geist! Besiegst du ihn, gibt es doppelte Bits.")
    return text


def flee(pet, minute):
    if pet.get("battle"):
        raise P.Refused(T("Mitten im Kampf kannst du nicht mehr fliehen!"))
    pet.pop("scout", None)
    return T("Du bist geflohen.")


def fight(pet, minute):
    _can_battle(pet)
    scouted = pet.get("scout")
    if not scouted or minute - scouted["time"] > TIMEOUT:
        pet.pop("scout", None)
        raise P.Refused(T("Der Gegner ist weg. Such einen neuen."))
    pet["hunger"] -= 1
    pet["strength"] -= 1
    hp = max_hp(pet)
    trait = scouted.get("personality", "normal")
    opp_hp = PERSONALITIES.get(trait, {}).get("hp", MAX_HP)
    pet["battle"] = {"dex": scouted["dex"], "power": scouted["power"], "my_hp": hp, "my_max": hp,
                     "opp_hp": opp_hp, "opp_max": opp_hp, "round": 0, "time": minute,
                     "ghost": scouted.get("ghost"), "personality": trait, "my_gauge": 0, "opp_gauge": 0}
    pet.pop("scout")
    return T("Kampf gegen {name}! Lade deinen Schuss!", name=data.DIGIMON[scouted["dex"]]["name"])


def _running(pet, minute):
    """Der laufende Kampf (oder Refused, wenn er vorbei/verfallen ist)."""
    b = pet.get("battle")
    if not b:
        raise P.Refused(T("Gerade läuft kein Kampf."))
    if not pet["alive"] or pet.get("frozen") or pet["stage"] not in BATTLE_STAGES:
        pet.pop("battle")
        raise P.Refused(T("Der Kampf ist vorbei."))
    if minute - b["time"] > TIMEOUT:
        pet.pop("battle")
        raise P.Refused(T("Der Gegner ist abgehauen – du warst zu lange weg."))
    b["time"] = minute
    return b


def _trait(b):
    return PERSONALITIES.get(b.get("personality"), PERSONALITIES["normal"])


def _guard(b, rng):
    """Welche Seite deckt der Gegner diese Runde? "listig" merkt sich deinen letzten Angriff."""
    sly = _trait(b).get("sly", 0)
    if sly and b.get("last_aim") in SIDES and rng.random() < sly:
        return b["last_aim"]
    return rng.choice(SIDES)


def _plan(b, rng):
    """Die Angriffe des Gegners für diese Runde (Liste, 1 oder 2): Höhe, stark, Spezial."""
    trait = _trait(b)
    attacks = []
    for _ in range(2 if rng.random() < trait.get("double", 0) else 1):
        if b.get("opp_gauge", 0) >= SPECIAL_MAX:          # Leiste voll: Spezialattacke
            b["opp_gauge"] = 0
            attacks.append({"side": rng.choice(SIDES), "strong": False, "special": True})
        else:
            attacks.append({"side": rng.choice(SIDES), "strong": rng.random() < trait["strong"],
                            "special": False})
    return attacks


def _take_hits(pet, b, dodged, rng):
    """Die offenen gegnerischen Angriffe auswerten. `dodged`: eine Angabe pro Angriff
    (fehlend = nicht ausgewichen). Spezialattacken kann man nicht ausweichen."""
    incoming = b.pop("incoming", None) or []
    if not isinstance(dodged, list):
        dodged = [dodged]
    bonus = attr_bonus(attribute(pet["dex"]), attribute(b["dex"]))
    _, theirs = hit_chances(power(pet), b["power"], bonus, 0.0, dodge(pet))   # inkl. passivem Ausweichen
    out = {"opp_hits": [], "dodged": [], "damage_taken": 0}
    for i, attack in enumerate(incoming):
        evaded = i < len(dodged) and dodged[i] is True and not attack.get("special")
        hit = rng.random() < theirs and not evaded
        out["opp_hits"].append(hit)
        out["dodged"].append(evaded)
        if hit:
            damage = 2 if attack.get("strong") or attack.get("special") else 1
            b["my_hp"] = max(0, b["my_hp"] - damage)
            out["damage_taken"] += damage
            b["my_gauge"] = fill(b.get("my_gauge", 0))
            if not attack.get("special"):
                b["opp_gauge"] = fill(b.get("opp_gauge", 0))
    out["opp_hit"] = any(out["opp_hits"])                 # wie früher (alte Browser-Tabs)
    return out


def _status(b):
    return {"my_hp": b["my_hp"], "opp_hp": b["opp_hp"],
            "my_gauge": b.get("my_gauge", 0), "opp_gauge": b.get("opp_gauge", 0)}


def _over(b):
    return b["opp_hp"] <= 0 or b["my_hp"] <= 0 or b["round"] >= MAX_ROUNDS


def _end(pet, b, result, minute, rng):
    result.update(_status(b), phase="done", incoming=[], over=True)
    # nach MAX_ROUNDS Runden (beide leben noch) zählen die Leben – gleich viele = unentschieden
    timeout = b["my_hp"] > 0 and b["opp_hp"] > 0
    draw = timeout and b["my_hp"] == b["opp_hp"]
    result.update(_finish(pet, b["my_hp"] > b["opp_hp"], minute, rng, draw=draw, timeout=timeout))
    return result


def shot(pet, attack, minute, rng=random):
    """Dein Angriff in einer Runde. Lebt der Gegner danach noch, legt er seine
    Angriffe fest (``incoming``); ausgewichen wird danach mit ``evade``.
    `attack`: siehe parse_shot (auch die alte Zahl "quality")."""
    b = _running(pet, minute)
    result = {}
    if b.get("incoming"):            # nicht beantwortet (z. B. Seite neu geladen) = nicht ausgewichen
        result["late"] = _take_hits(pet, b, [], rng)
        if _over(b):
            return _end(pet, b, result, minute, rng)
    attack = parse_shot(attack)
    if attack["special"] and b.get("my_gauge", 0) < SPECIAL_MAX:
        raise P.Refused(T("Deine Spezial-Leiste ist noch nicht voll."))
    b["round"] += 1
    trait = _trait(b)
    guard = None if attack["special"] else _guard(b, rng)
    bonus = attr_bonus(attribute(pet["dex"]), attribute(b["dex"]))
    roll = roll_attack(attack, power(pet), b["power"], bonus, rng, guard,
                       evade=trait.get("evade", 0.0), risk=trait.get("risk", 0.0))
    if attack["special"]:
        b["my_gauge"] = 0
    else:
        b["last_aim"] = attack["aim"]
    if roll["hit"]:
        b["opp_hp"] = max(0, b["opp_hp"] - roll["damage"])
        b["opp_gauge"] = fill(b.get("opp_gauge", 0))
        if not attack["special"]:
            b["my_gauge"] = fill(b.get("my_gauge", 0))
    result.update(aim=roll["aim"], guard=roll["guard"], gap=roll["gap"], interrupted=roll["interrupted"],
                  mega=roll["mega"], special=roll["special"], damage=roll["damage"],
                  my_hit=roll["hit"], power_shot=roll["power"], opp_hit=False)
    if b["opp_hp"] <= 0:
        return _end(pet, b, result, minute, rng)
    b["incoming"] = _plan(b, rng)
    result.update(_status(b), phase="dodge", incoming=[dict(a) for a in b["incoming"]], over=False)
    return result


def evade(pet, dodged, minute, rng=random):
    """Ausweichen vor den Angriffen des Gegners (HTTP: /api/battle/dodge).
    `dodged`: Liste mit True/False pro Angriff in ``incoming``."""
    b = _running(pet, minute)
    if not b.get("incoming"):
        raise P.Refused(T("Gerade fliegt kein Angriff auf dich zu."))
    result = _take_hits(pet, b, dodged, rng)
    if _over(b):
        return _end(pet, b, result, minute, rng)
    result.update(_status(b), phase="done", incoming=[], over=False)
    return result


def _finish(pet, won, minute, rng, draw=False, timeout=False):
    """Kampf auswerten. `timeout`: nach MAX_ROUNDS Runden vorbei (die Leben entscheiden),
    `draw`: dabei gleich viele Leben – unentschieden, keine Verletzung."""
    b = pet.pop("battle")
    pet.pop("charm", None)        # Glücksbringer ist verbraucht
    opp = data.DIGIMON[b["dex"]]["name"]
    name = P.display_name(pet)
    pet["battles"] += 1
    pet["battles_stage"] += 1
    out = {"won": won, "draw": draw, "egg_line": None, "injured": False}
    # nach der letzten Runde sagen, warum es vorbei ist
    head = T("Nach {n} Runden ist Schluss:", n=MAX_ROUNDS) + " " if timeout else ""
    if draw:
        text = head + T("{name} und {opp} haben gleich viele Leben – unentschieden! {opp} zieht sich zurück.",
                        name=name, opp=opp)
    elif won:
        pet["wins"] += 1
        pet["wins_stage"] += 1
        pet["weight"] = max(P.BASE_WEIGHT[pet["stage"]], pet["weight"] - rng.randint(1, 2))
        text = head + (T("{name} hat mehr Leben übrig und gewinnt gegen {opp}!", name=name, opp=opp) if timeout
                       else T("{name} hat {opp} besiegt!", name=name, opp=opp))
        if rng.random() < settings.CURRENT["battle_egg_chance"]:
            lines = sorted({e["line"] for e in data.EVOLUTIONS if e["to"] == b["dex"]} - set(data.EVENT_LINES)) \
                or sorted(data.NORMAL_LINES)
            out["egg_line"] = rng.choice(lines)
            text += " " + T("{opp} hat ein Digi-Ei fallen lassen!", opp=opp)
    else:
        text = head + (T("{opp} hat mehr Leben übrig – {name} verliert.", name=name, opp=opp) if timeout
                       else T("{name} hat gegen {opp} verloren.", name=name, opp=opp))
        if rng.random() < injury_chance(pet):
            pet["injured"], pet["injured_since"] = True, minute
            out["injured"] = True
            text += " " + T("Es ist verletzt – gib ihm Medizin!")
    # Bits für den Shop (gutgeschrieben vom Server, game/shop.py)
    from . import events, shop
    out["bits"] = shop.wild_reward(pet["stage"], won, rng)
    if won and b.get("ghost"):                 # Event-Geist besiegt: doppelte Bits, evtl. Event-Item / -Ei
        out["bits"] *= 2
        out["ghost"] = True
        out["candy"] = rng.random() < events.GHOST_ITEM_CHANCE
        egg = events.event_egg(b["ghost"])
        if egg and not out["egg_line"] and rng.random() < events.GHOST_EGG_CHANCE:
            out["egg_line"] = egg
            text += " " + T("Der Geist hat ein {egg} fallen lassen!", egg=data.egg_name(egg))   # Event-Ei: mit Namen
    text += " " + shop.bits_text(out["bits"])
    if out.get("candy"):
        text += " " + T("Der Geist hat ein Gruselbonbon fallen lassen!")
    P._log(pet, minute, text)
    out["message"] = text
    return out


def view(pet):
    """Kampfinfos für den Browser."""
    out = {}
    if pet.get("scout"):
        s = pet["scout"]
        trait = s.get("personality", "normal")
        out["scout"] = {"dex": s["dex"], "name": data.DIGIMON[s["dex"]]["name"],
                        "attribute": attribute(s["dex"]), "ghost": bool(s.get("ghost")),
                        "personality": {"key": trait, "name": personality_name(trait)}}
    if pet.get("battle"):
        b = pet["battle"]
        trait = b.get("personality", "normal")
        out["battle"] = {"dex": b["dex"], "name": data.DIGIMON[b["dex"]]["name"],
                         "my_hp": b["my_hp"], "opp_hp": b["opp_hp"],
                         "my_max": b.get("my_max", MAX_HP), "opp_max": b.get("opp_max", MAX_HP),
                         "round": b["round"], "max_rounds": MAX_ROUNDS,
                         "my_gauge": b.get("my_gauge", 0), "opp_gauge": b.get("opp_gauge", 0),
                         "special_max": SPECIAL_MAX,
                         "personality": {"key": trait, "name": personality_name(trait)},
                         "special_name": special_name(pet["dex"]), "opp_special_name": special_name(b["dex"]),
                         # offene gegnerische Angriffe (nach Neuladen weiter ausweichen)
                         "incoming": [dict(a) for a in b["incoming"]] if b.get("incoming") else None}
    return out
