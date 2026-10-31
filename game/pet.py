"""Die Pflege-Simulation eines Digimon.

Ein Digimon ist ein einfaches dict (wird als JSON gespeichert). Die Zeit läuft in
Spielminuten; ``advance`` rechnet Minute für Minute nach, was seit dem letzten
Besuch passiert ist -- so läuft alles weiter, auch wenn das Spiel zu ist.
"""
import os
import re
from datetime import datetime

from . import data, settings
from .i18n import T, Text, join, stored

# Feste Zeitzone fürs Spiel (Schlafenszeiten!), damit es auf einem Server in
# einer anderen Zeitzone genauso läuft. Fehlt die Zeitzonen-Datenbank (Windows
# ohne "tzdata"), wird die Uhrzeit des Rechners benutzt.
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo(os.environ.get("VPET_TZ", "Europe/Berlin"))
except Exception:           # noqa: BLE001 – dann eben Ortszeit des Rechners
    TZ = None


def local_time(minute):
    return datetime.fromtimestamp(minute * 60, TZ)

# "Armor" = Armor-Formen (per Armor-Ei aus dem Rucksack): eigene Endstufe neben Champion
STAGES = ["Egg", "Fresh", "InTraining", "Rookie", "Champion", "Armor", "Ultimate", "Mega"]
STAGE_DE = {
    "Egg": "Ei", "Fresh": "Baby I", "InTraining": "Baby II", "Rookie": "Rookie",
    "Champion": "Champion", "Armor": "Armor", "Ultimate": "Ultra", "Mega": "Mega",
}


def stage_name(stage):
    """Stufe zum Anzeigen (zweisprachig), z. B. "Ultra" / "Ultimate"."""
    return T(STAGE_DE[stage])

# Minuten in einer Stufe, bis die Entwicklung fällig ist (wie beim V-Pet)
STAGE_TIME = {"Egg": 1, "Fresh": 10, "InTraining": 12 * 60, "Rookie": 24 * 60,
              "Champion": 36 * 60, "Ultimate": 48 * 60}
# alle wie viele Minuten ein Herz Hunger / Kraft verloren geht
HUNGER_EVERY = {"Fresh": 3, "InTraining": 30, "Rookie": 48, "Champion": 59, "Armor": 59,
                "Ultimate": 79, "Mega": 99}
STRENGTH_EVERY = {"Fresh": 3, "InTraining": 30, "Rookie": 38, "Champion": 48, "Armor": 48,
                  "Ultimate": 59, "Mega": 79}
POOP_EVERY = {"Fresh": 3, "InTraining": 60, "Rookie": 120, "Champion": 120, "Armor": 120,
              "Ultimate": 180, "Mega": 180}
BASE_WEIGHT = {"Egg": 0, "Fresh": 5, "InTraining": 10, "Rookie": 20, "Champion": 30, "Armor": 30,
               "Ultimate": 40, "Mega": 50}

MAX_HEARTS = 4
MAX_POOP = 4               # bei 4 Haufen wird es krank
CALL_GRACE = 10            # Minuten, bis ein ignorierter Ruf zum Pflegefehler wird
STARVE_DEATH = 12 * 60     # 12 h ohne Essen -> Tod
SICK_DEATH = 12 * 60       # 12 h krank/verletzt ohne Medizin -> Tod
MAX_MISTAKES = 20          # 20 Pflegefehler im Leben -> Tod
WAKE_UP = 8 * 60           # alle wachen um 8:00 auf
MAX_LOG = 30


def minute_of_day(minute):
    t = local_time(minute)
    return t.hour * 60 + t.minute


def new_egg(line, now, name=None):
    return {
        "line": line, "dex": None, "stage": "Egg", "name": name,
        "born": now, "last": now, "stage_since": now, "alive": True,
        "hunger": 0, "strength": 0, "weight": 0, "poop": 0,
        "sick": False, "sick_since": None, "injured": False, "injured_since": None,
        "light": True, "asleep": False,
        "mistakes": 0, "mistakes_total": 0, "trainings": 0, "overfeeds": 0,
        "overfed": False, "battles": 0, "wins": 0,
        "battles_stage": 0, "wins_stage": 0,
        # Zeitpunkte, seit wann ein Ruf offen ist (None = kein Ruf)
        "call_hunger": None, "call_strength": None, "call_light": None,
        "hunger_tick": 0, "strength_tick": 0, "poop_tick": 0,
        "starving_since": None, "death_cause": None,
        "log": [], "forms": [],
    }


def _log(pet, minute, text):
    """Tagebuch-Eintrag. Ein zweisprachiger Text (i18n.T) wird mit englischer Fassung gespeichert."""
    entry = {"t": minute, "text": str(text)}
    if isinstance(text, Text):
        entry["en"] = text.en
    pet["log"].append(entry)
    del pet["log"][:-MAX_LOG]


def display_name(pet):
    if pet["stage"] == "Egg":
        return data.egg_name(pet["line"])          # "Digi-Ei" – nur Event-Eier mit Sorte
    return data.DIGIMON[pet["dex"]]["name"]


NICK_MAX = 12


def set_nickname(pet, name, minute):
    """Spitzname geben (leer = entfernen). Bleibt bei jeder Digitation erhalten."""
    if pet["stage"] == "Egg":
        raise Refused(T("Ein Ei bekommt seinen Namen erst, wenn es geschlüpft ist."))
    if not pet["alive"]:
        raise Refused(T("Dein Digimon lebt nicht mehr."))
    name = "".join(ch for ch in str(name or "") if ch.isprintable())
    name = " ".join(name.split())[:NICK_MAX].strip()
    species = display_name(pet)
    if name.lower() == species.lower():
        name = ""
    pet["name"] = name or None
    if name:
        _log(pet, minute, T("{species} heißt jetzt {name}.", species=species, name=name))
        return T("{species} heißt jetzt {name}!", species=species, name=name)
    return T("{species} hat keinen Spitznamen mehr.", species=species)


def duration_text(minutes):
    """Dauer zum Anzeigen, z. B. "2 Std 15 Min" / "40 Min"."""
    h, m = divmod(max(0, int(minutes)), 60)
    if h and m:
        return T("{h} Std {m} Min", h=h, m=m)
    return T("{h} Std", h=h) if h else T("{m} Min", m=m)


def label(pet):
    """Spitzname mit Art, z. B. "Flammi (Agumon)" – ohne Spitzname nur die Art."""
    nick = pet.get("name")
    return f"{nick} ({display_name(pet)})" if nick and pet["stage"] != "Egg" else display_name(pet)


def should_sleep(pet, minute):
    if pet["stage"] in ("Egg", "Fresh") or pet.get("no_sleep"):
        return False
    m = minute_of_day(minute)
    bed = data.bedtime(pet["line"], pet["dex"]) % 1440
    if bed > WAKE_UP:
        return m >= bed or m < WAKE_UP
    return bed <= m < WAKE_UP


def _in_range(value, rng):
    lo, hi = rng
    return value >= lo and (hi is None or value <= hi)


def _rule_ok(pet, rule, ignore_trainings=False):
    if "any" in rule:                       # mehrere Möglichkeiten: eine reicht
        return any(_rule_ok(pet, r, ignore_trainings) for r in rule["any"])
    if "cm" in rule and not _in_range(pet["mistakes"], rule["cm"]):
        return False
    if "tr" in rule and not ignore_trainings and not _in_range(pet["trainings"], rule["tr"]):
        return False
    if "of" in rule and not _in_range(pet["overfeeds"], rule["of"]):
        return False
    if "btl" in rule and not _in_range(pet["battles_stage"], rule["btl"]):
        return False
    if "wins" in rule and not _in_range(pet["wins_stage"], rule["wins"]):
        return False
    if "win" in rule:
        w = rule["win"]
        if pet["battles_stage"] < w["battles"] or pet["wins_stage"] < w["wins"]:
            return False
    if "jogress" in rule:
        return False   # Fusionen laufen nur über jogress(), nie von allein
    if "item" in rule:
        return False   # Armor-Digitation nur mit dem Armor-Ei aus dem Rucksack (explore.use_item)
    return True


def needs_battles(rule):
    """Braucht diese Entwicklung Kämpfe (oder eine Fusion)?"""
    if "any" in rule:
        return all(needs_battles(r) for r in rule["any"])
    return any(k in rule for k in ("win", "btl", "wins", "jogress"))


# ---------------------------------------------------------------- Trainingsarten

SKILLS = ("power", "speed", "defense")
SKILL_DE = {"power": "Kraft", "speed": "Tempo", "defense": "Verteidigung"}
TRAINING_DE = {"power": "Krafttraining", "speed": "Tempotraining", "defense": "Verteidigungstraining"}
# Welches Element passt zu welcher Trainingsart?
ELEMENT_SKILL = {
    "Fire": "power", "Thunder": "power", "Metal": "power",
    "Wind": "speed", "Light": "speed", "Dark": "speed",
    "Earth": "defense", "Ice": "defense", "Wood": "defense", "Water": "defense",
}
STYLE_MIN = 5          # so viele Erfolge in einer Art braucht ein Trainingsstil
STYLE_SHARE = 0.6      # ... und so viel Anteil an allen Erfolgen


def skills(pet):
    return pet.setdefault("skills", {s: 0 for s in SKILLS})


def style(pet):
    """Die Trainingsart, die in dieser Stufe klar überwiegt (oder None)."""
    sk = skills(pet)
    total = sum(sk.values())
    best = max(SKILLS, key=lambda s: sk[s])
    if sk[best] >= STYLE_MIN and sk[best] >= STYLE_SHARE * total:
        return best
    return None


def skill_of(dex):
    return ELEMENT_SKILL.get(data.DIGIMON[dex].get("element"))


def next_form(pet):
    """Liefert die Entwicklung, die jetzt passt, oder None.

    Normal gewinnt die erste Form, deren Regel passt. Hat das Digimon einen
    klaren Trainingsstil, wird eine Form mit passendem Element bevorzugt – dafür
    darf die Trainingszahl abweichen, Pflegefehler & Co. müssen aber stimmen."""
    options = data.evolutions_from(pet["line"], pet["dex"])
    preferred = style(pet)
    if preferred:
        for evo in options:
            if skill_of(evo["to"]) == preferred and _rule_ok(pet, evo["rule"], ignore_trainings=True):
                return evo
    for evo in options:
        if _rule_ok(pet, evo["rule"]):
            return evo
    return None


# ---------------------------------------------------------------- Jogress (Fusion)

def jogress_options(pet):
    """Fusionen, die jetzt möglich wären – fehlt nur noch der passende Partner.
    Liefert [(Entwicklung, Bedingung an den Partner)]."""
    if not pet.get("dex") or not pet["alive"]:
        return []
    out = []
    for evo in data.evolutions_from(pet["line"], pet["dex"]):
        for alt in evo["rule"].get("any", [evo["rule"]]):
            if "jogress" in alt:
                need = alt["jogress"]
                if isinstance(need, int) and need not in data.PLAYABLE:
                    continue                 # Partner gibt es im Spiel nicht -> unmöglich
                rest = {k: v for k, v in alt.items() if k != "jogress"}
                if _rule_ok(pet, rest):
                    out.append((evo, alt["jogress"]))
    return out


def partner_fits(need, pet, partner):
    """Passt `partner` zur Bedingung `need` (Digimon-Nr. oder Attribute wie "Vaccine/Data")?"""
    if not partner or not partner.get("alive") or not partner.get("dex") or partner is pet:
        return False
    if isinstance(need, int):
        return partner["dex"] == need
    if partner["stage"] != pet["stage"]:
        return False
    wanted = set(need.split("/"))
    if "None" in wanted:
        wanted |= {"Free"}
    return data.DIGIMON[partner["dex"]]["attribute"] in wanted


def need_text(need):
    if isinstance(need, int):
        return data.DIGIMON[need]["name"] if need in data.DIGIMON else T("Digimon Nr. {n}", n=need)
    words = {"Vaccine": T("Serum"), "Data": T("Daten"), "Virus": T("Virus"), "None": T("ohne Attribut")}
    attrs = join(T(" oder "), (words.get(a, a) for a in need.split("/")))
    return T("ein {attrs}-Digimon", attrs=attrs)


def jogress(pet, to_dex, partner, partner_owner, minute):
    """Fusion zu `to_dex`: `pet` digitiert, der Partner bleibt wie er ist."""
    _awake_check(pet)
    if pet["sick"] or pet["injured"]:
        raise Refused(T("{name} ist nicht fit genug für eine Fusion.", name=display_name(pet)))
    evo = next((e for e, need in jogress_options(pet)
                if e["to"] == to_dex and partner_fits(need, pet, partner)), None)
    if not evo:
        raise Refused(T("Diese Fusion passt gerade nicht."))
    old, partner_name = display_name(pet), display_name(partner)
    _evolve(pet, evo, minute)
    who = T("{partner} von {owner}", partner=partner_name, owner=partner_owner) if partner_owner else partner_name
    _log(pet, minute, T("Jogress! {old} + {who} = {new}!", old=old, who=who, new=display_name(pet)))
    return T("Jogress! {old} und {who} verschmelzen zu {new}!", old=old, who=who, new=display_name(pet))


def _evolve(pet, evo, minute):
    old = display_name(pet)
    pet["dex"] = evo["to"]
    forms = pet.setdefault("forms", [])          # alle Formen, die es je hatte (Sammel-Fortschritt)
    if evo["to"] not in forms:
        forms.append(evo["to"])
    pet["stage"] = evo["stage"]
    pet["stage_since"] = minute
    pet["skills"] = {s: 0 for s in SKILLS}
    pet["mistakes"] = pet["trainings"] = pet["overfeeds"] = 0
    pet["battles_stage"] = pet["wins_stage"] = 0
    pet["weight"] = max(pet["weight"], BASE_WEIGHT[pet["stage"]])
    pet["hunger_tick"] = pet["strength_tick"] = pet["poop_tick"] = 0
    if old == "Digi-Ei":
        pet["hunger"], pet["strength"] = 0, 0
        _log(pet, minute, T("Das Ei ist geschlüpft: {name}!", name=display_name(pet)))
    else:
        _log(pet, minute, T("{old} hat sich zu {new} entwickelt!", old=old, new=display_name(pet)))


def _die(pet, minute, cause):
    """`cause` ist ein deutscher Text (so wird er gespeichert); übersetzt wird beim Anzeigen."""
    if pet.pop("totem", None):
        return _totem_saves(pet, minute, cause)
    pet["alive"] = False
    pet["death_cause"] = str(cause)
    pet["died"] = minute
    _log(pet, minute, T("{name} ist gestorben ({cause}).", name=display_name(pet), cause=T(str(cause))))


def _totem_saves(pet, minute, cause):
    """Schutz-Totem (wie das Totem of Undying): statt zu sterben wird das Digimon
    notdürftig aufgepäppelt und landet im Kühlschrank – dort wartet es, bis man
    sich wieder kümmern kann. Das Totem ist danach verbraucht."""
    name = display_name(pet)
    pet["hunger"] = max(pet["hunger"], 1)
    pet["strength"] = max(pet["strength"], 1)
    pet["poop"] = 0
    pet["sick"] = pet["injured"] = False
    pet["sick_since"] = pet["injured_since"] = pet["starving_since"] = None
    pet["mistakes_total"] = min(pet["mistakes_total"], MAX_MISTAKES - 5)
    for key in ("call_hunger", "call_strength", "call_light"):
        pet[key] = None
    pet.pop("scout", None)
    pet.pop("battle", None)
    pet["frozen"] = True
    _log(pet, minute, T("Das Schutz-Totem hat {name} vor dem Tod gerettet ({cause})! {name} wartet im Kühlschrank auf dich.",
                        name=name, cause=T(str(cause))))


def _check_call(pet, key, active, minute, what):
    """Offener Ruf -> nach CALL_GRACE Minuten ein Pflegefehler."""
    if not active:
        pet[key] = None
        return
    if pet[key] is None:
        pet[key] = minute
    elif pet[key] is not False and minute - pet[key] >= CALL_GRACE:
        pet["mistakes"] += 1
        pet["mistakes_total"] += 1
        pet[key] = False          # gezählt; erst nach Behebung wieder möglich
        _log(pet, minute, T("Pflegefehler: {what}", what=what))


def _every(table, stage):
    """Minuten bis zum nächsten Herz-Verlust/Haufen – mit dem Tempo aus den Admin-Regeln."""
    return max(1, round(table[stage] / settings.CURRENT["need_speed"]))


def _step(pet, minute):
    """Simuliert genau eine Spielminute."""
    stage = pet["stage"]
    in_stage = minute - pet["stage_since"]

    if stage == "Egg":
        if in_stage >= STAGE_TIME["Egg"]:
            first = data.LINES[pet["line"]]["first"]
            evo = next(e for e in data.evolutions_from(pet["line"], None) if e["to"] == first)
            _evolve(pet, evo, minute)
        return

    # Schlafen / Aufwachen. Ein Nickerchen (Licht aus am Tag) geht weiter, bis
    # das Licht wieder angeht; beginnt die Schlafenszeit, wird es echter Schlaf.
    sleep = should_sleep(pet, minute)
    if sleep and pet.get("nap"):
        pet["nap"] = False
    if sleep and not pet["asleep"]:
        pet["asleep"] = True
        _log(pet, minute, T("{name} ist eingeschlafen. Licht aus!", name=display_name(pet)))
    elif not sleep and pet["asleep"] and not pet.get("nap"):
        if not pet["light"]:
            # Morgen, aber das Licht ist noch aus: es döst als Nickerchen weiter, bis du das Licht
            # anmachst (halber Verbrauch, keine Kacke) – wer um 8 Uhr noch schläft, verpasst nichts
            pet["nap"] = True
            _log(pet, minute, T("Guten Morgen! {name} döst im Dunkeln weiter – Licht an weckt es.",
                                name=display_name(pet)))
        else:
            pet["asleep"] = False
            _log(pet, minute, T("{name} ist aufgewacht.", name=display_name(pet)))

    # Wach: normaler Verbrauch. Nickerchen: halb so schnell, keine Kacke.
    napping = pet["asleep"] and pet.get("nap")
    if not pet["asleep"] or (napping and minute % 2 == 0):
        pet["hunger_tick"] += 1
        if pet["hunger_tick"] >= _every(HUNGER_EVERY, stage):
            pet["hunger_tick"] = 0
            if pet["hunger"] > 0:
                pet["hunger"] -= 1
                pet["overfed"] = False
        pet["strength_tick"] += 1
        if pet["strength_tick"] >= _every(STRENGTH_EVERY, stage):
            pet["strength_tick"] = 0
            pet["strength"] = max(0, pet["strength"] - 1)
    if not pet["asleep"]:
        pet["poop_tick"] += 1
        if pet["poop_tick"] >= _every(POOP_EVERY, stage):
            pet["poop_tick"] = 0
            pet["poop"] = min(MAX_POOP, pet["poop"] + 1)
            if pet["poop"] >= MAX_POOP and not pet["sick"]:
                pet["sick"], pet["sick_since"] = True, minute
                _log(pet, minute, T("{name} ist vom Dreck krank geworden!", name=display_name(pet)))

    # Rufe -> Pflegefehler. Im Nachtschlaf kann man nicht füttern – dann ruhen
    # Hunger-/Kraft-Rufe und die Verhungern-Uhr bis zum Aufwachen.
    night = pet["asleep"] and not pet.get("nap")
    if night:
        for key in ("call_hunger", "call_strength"):
            if isinstance(pet[key], int) and not isinstance(pet[key], bool):
                pet[key] += 1                       # Ruf-Uhr anhalten
    else:
        _check_call(pet, "call_hunger", pet["hunger"] == 0, minute, T("Hunger ignoriert"))
        _check_call(pet, "call_strength", pet["strength"] == 0, minute, T("Kraft leer ignoriert"))
    _check_call(pet, "call_light", pet["asleep"] and pet["light"], minute,
                T("Licht beim Schlafen angelassen"))

    # Tod (außer mit Unsterblich-Cheat oder wenn der Admin Sterben abgeschaltet hat)
    immortal = pet.get("immortal") or not settings.CURRENT["death"]
    if immortal:
        pet["starving_since"] = None
    elif pet["hunger"] == 0:
        if pet["starving_since"] is None:
            pet["starving_since"] = minute
        elif night:
            pet["starving_since"] += 1              # nachts läuft die Uhr nicht weiter
        elif minute - pet["starving_since"] >= STARVE_DEATH:
            return _die(pet, minute, T("verhungert"))
    else:
        pet["starving_since"] = None
    if not immortal:
        if pet["sick"] and minute - pet["sick_since"] >= SICK_DEATH:
            return _die(pet, minute, T("Krankheit nicht behandelt"))
        if pet["injured"] and minute - pet["injured_since"] >= SICK_DEATH:
            return _die(pet, minute, T("Verletzung nicht behandelt"))
        if pet["mistakes_total"] >= MAX_MISTAKES:
            return _die(pet, minute, T("zu viele Pflegefehler"))

    # Entwicklung (nur wach, nicht mit Ewigstein)
    if not pet["asleep"] and stage in STAGE_TIME and in_stage >= STAGE_TIME[stage] and not pet.get("everstone"):
        evo = next_form(pet)
        if evo:
            _evolve(pet, evo, minute)


TIME_KEYS = ("born", "last", "stage_since", "sick_since", "injured_since",
             "starving_since", "died", "call_hunger", "call_strength", "call_light")


def shift_times(pet, minutes, logs=False):
    """Verschiebt alle Zeitpunkte des Digimon um `minutes` (negativ = in die Vergangenheit)."""
    for key in TIME_KEYS:
        value = pet.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            pet[key] = value + minutes
    # Expedition und Kampf haben eigene Zeitpunkte
    for key, fields in (("expedition", ("start", "end")), ("scout", ("time",)), ("battle", ("time",))):
        for field in fields:
            if pet.get(key) and field in pet[key]:
                pet[key][field] += minutes
    if logs:
        for entry in pet["log"]:
            entry["t"] += minutes


def advance(pet, now):
    """Rechnet die Zeit bis ``now`` (Spielminute) nach."""
    if pet.get("in_box") or pet.get("frozen") or pet.get("returned"):
        # Sammlung / Kühlschrank / Rückkehr vom Erkunden noch nicht bestätigt: die Zeit
        # steht still – alle Uhren laufen später einfach dort weiter, wo sie angehalten wurden
        if now > pet["last"]:
            shift_times(pet, now - pet["last"])
        return pet
    while pet["alive"] and pet["last"] < now and not pet.get("frozen") and not pet.get("returned"):
        pet["last"] += 1
        trip = pet.get("expedition")
        if trip:
            # unterwegs: kein Hunger, keine Rufe – nur die Zeit vergeht
            if pet["last"] >= trip["end"]:
                pet["expedition_return"] = pet.pop("expedition")
                # Fail-Safe: bis der Spieler die Rückkehr bestätigt (confirm_return), wartet das
                # Digimon – so entsteht kein Pflegefehler, nur weil man es nicht gleich gesehen hat
                pet["returned"] = True
                _log(pet, pet["last"], T("{name} ist vom Erkunden zurück.", name=display_name(pet)))
            continue
        _step(pet, pet["last"])
    if (pet.get("frozen") or pet.get("returned")) and now > pet["last"]:
        # vom Totem gerettet / zurück vom Erkunden: ab da steht die Zeit still
        shift_times(pet, now - pet["last"])
    pet["last"] = max(pet["last"], now)
    _expire_fights(pet, now)
    return pet


FIGHT_TIMEOUT = 15     # Minuten (wie battle.TIMEOUT)


def _expire_fights(pet, now):
    """Verfallene wilde Gegner aufräumen. Wer einen Kampf einfach liegen lässt,
    hat ihn verloren (sonst könnte man Niederlagen durch Warten vermeiden)."""
    scout = pet.get("scout")
    if scout and now - scout["time"] > FIGHT_TIMEOUT:
        pet.pop("scout")
    fight = pet.get("battle")
    if fight and now - fight["time"] > FIGHT_TIMEOUT:
        pet.pop("battle")
        pet.pop("charm", None)
        pet["battles"] += 1
        pet["battles_stage"] += 1
        _log(pet, now, T("{name} hat den Kampf liegen lassen – zählt als Niederlage.", name=display_name(pet)))


_HISTORY = [re.compile(p) for p in (
    r"^Das Ei ist geschlüpft: (?P<a>.+)!$",
    r"^(?P<a>.+) hat sich zu (?P<b>.+) entwickelt!$",
    r"^Jogress! (?P<a>.+?) \+ .+ = (?P<b>.+)!$",
    r"^Armor-Digitation mit „.+“: (?P<b>.+)!$",
)]


def _forms_from_history(pet):
    """Für Digimon von vor dem Sammel-Fortschritt: Formen aus dem Tagebuch (deutsche Texte)
    rekonstruieren – so gut es geht (das Tagebuch hat nur die letzten Einträge)."""
    by_name = {}
    for source in (data.PLAYABLE, data.DIGIMON):          # spielbare Digimon zuerst (gleiche Namen)
        for dex, d in source.items():
            by_name.setdefault(d["name"], dex)
    forms = []
    for entry in pet.get("log", []):
        for pattern in _HISTORY:
            m = pattern.match(entry.get("text", ""))
            if m:
                for name in m.groupdict().values():
                    dex = by_name.get(name)
                    if dex is not None and dex not in forms:
                        forms.append(dex)
    if pet.get("dex") is not None and pet["dex"] not in forms:
        forms.append(pet["dex"])
    return forms


def upgrade(pet):
    """Ältere Spielstände um Felder ergänzen, die erst später dazukamen."""
    if pet and "line" in pet:
        # zusammengelegte Eier / gleichnamige Digimon -> neue Namen bzw. Nummern
        pet["line"] = data.LINE_ALIASES.get(pet["line"], pet["line"])
        if "forms" not in pet:
            pet["forms"] = _forms_from_history(pet)
        for key, value in new_egg(pet["line"], pet.get("born", 0)).items():
            pet.setdefault(key, value)
        pet.setdefault("skills", {s: 0 for s in SKILLS})
        # gleichnamige Digimon wurden zusammengelegt -> neue Nummer
        if pet.get("dex") in data.ALIASES:
            pet["dex"] = data.ALIASES[pet["dex"]]
    return pet


# ---------------------------------------------------------------- Aktionen

class Refused(Exception):
    """Aktion nicht möglich -- die Nachricht wird dem Spieler gezeigt."""


def confirm_return(pet, minute):
    """Rückkehr vom Erkunden bestätigen – ab jetzt läuft die Zeit wieder."""
    if not pet.get("returned"):
        raise Refused(T("Dein Digimon ist gerade nicht vom Erkunden zurückgekommen."))
    pet.pop("returned")
    pet["last"] = max(pet["last"], minute)
    # ist gerade Schlafenszeit, geht es gleich ins dunkle Bett (es war ja weg)
    pet["light"] = not should_sleep(pet, minute)
    text = T("Willkommen zurück, {name}!", name=display_name(pet))
    if pet.get("scout"):
        # vom Erkunden ist ein wildes Digimon mitgekommen – jetzt kann man kämpfen
        text += " " + T("Ein wildes {name} ist mitgekommen – kämpfen oder fliehen?",
                        name=data.DIGIMON[pet["scout"]["dex"]]["name"])
    return text


def _away_check(pet):
    if pet.get("returned"):
        raise Refused(T("{name} ist vom Erkunden zurück – bestätige erst die Rückkehr (OK).",
                        name=display_name(pet)))
    if pet.get("expedition"):
        end = local_time(pet["expedition"]["end"]).strftime("%H:%M")
        raise Refused(T("{name} ist gerade unterwegs – zurück um {end} Uhr.", name=display_name(pet), end=end))


def _usable(pet):
    if not pet["alive"]:
        raise Refused(T("Dein Digimon lebt nicht mehr."))
    if pet.get("frozen"):
        raise Refused(T("{name} ist im Kühlschrank. Erst auftauen!", name=display_name(pet)))
    _away_check(pet)


def set_frozen(pet, on, minute):
    """Kühlschrank: friert das Digimon ein (die Zeit steht still) oder taut es auf."""
    if not pet["alive"]:
        raise Refused(T("Dein Digimon lebt nicht mehr."))
    _away_check(pet)
    if on and (pet.get("battle") or pet.get("scout")):
        raise Refused(T("Erst den Kampf beenden (oder fliehen)."))
    advance(pet, minute)          # bis jetzt nachrechnen (bzw. eingefroren halten)
    pet["frozen"] = bool(on)
    name = display_name(pet)
    _log(pet, minute, T("{name} ist im Kühlschrank.", name=name) if on else T("{name} ist aufgetaut.", name=name))
    return T("{name} ist im Kühlschrank. Die Zeit steht still, bis du es auftaust.", name=name) if on \
        else T("{name} ist aufgetaut und freut sich auf dich!", name=name)


def _awake_check(pet):
    if not pet["alive"]:
        raise Refused(T("Dein Digimon lebt nicht mehr."))
    if pet["stage"] == "Egg":
        raise Refused(T("Das Ei schlüpft gleich ..."))
    if pet.get("frozen"):
        raise Refused(T("{name} ist im Kühlschrank. Erst auftauen!", name=display_name(pet)))
    _away_check(pet)
    if pet["asleep"] and pet.get("nap"):
        raise Refused(T("{name} macht ein Nickerchen. Licht an weckt es.", name=display_name(pet)))
    if pet["asleep"]:
        raise Refused(T("{name} schläft gerade. Psst!", name=display_name(pet)))


def wake_for_food(pet, minute):
    """Im Nickerchen wird es weiter (langsam) hungrig – also weckt Futter es auf, statt
    dass man zusehen muss, wie es Pflegefehler sammelt. Nachts nicht: da wird es nicht hungrig."""
    if pet["alive"] and pet["asleep"] and pet.get("nap") and not pet.get("frozen") and not pet.get("expedition"):
        pet["asleep"], pet["nap"], pet["light"] = False, False, True
        _log(pet, minute, T("{name} riecht Futter und wacht aus dem Nickerchen auf.", name=display_name(pet)))


def feed(pet, food, minute):
    wake_for_food(pet, minute)
    _awake_check(pet)
    name = display_name(pet)
    if food == "meat":
        if pet["hunger"] >= MAX_HEARTS:
            if pet["overfed"]:
                raise Refused(T("{name} will nichts mehr essen.", name=name))
            pet["overfed"] = True
            pet["overfeeds"] += 1
            pet["weight"] += 1
            return "overfeed", T("{name} hat sich überfressen! (+1 g)", name=name)
        pet["hunger"] += 1
        pet["weight"] += 1
        return "eat", T("{name} isst Fleisch. Hunger +1", name=name)
    if food == "protein":
        pet["strength"] = min(MAX_HEARTS, pet["strength"] + 1)
        pet["weight"] += 2
        return "eat", T("{name} schluckt Protein. Kraft +1 (+2 g)", name=name)
    raise Refused(T("Unbekanntes Futter."))


SKILL_CAP = 10        # mehr Punkte pro Stufe bringen nichts


def train(pet, success, minute, kind="power"):
    """Ein Training. Jedes zählt für die Digitation; ein Erfolg gibt ein Kraft-Herz
    und einen Punkt in der Trainingsart (Kraft, Tempo oder Verteidigung)."""
    _awake_check(pet)
    if kind not in SKILLS:
        raise Refused(T("Diese Trainingsart gibt es nicht."))
    if pet["sick"] or pet["injured"]:
        raise Refused(T("{name} ist nicht fit genug zum Trainieren.", name=display_name(pet)))
    pet["trainings"] += 1
    pet["weight"] = max(BASE_WEIGHT[pet["stage"]], pet["weight"] - 2)
    training = T(TRAINING_DE[kind])
    if success:
        pet["strength"] = min(MAX_HEARTS, pet["strength"] + 1)
        sk = skills(pet)
        sk[kind] = min(SKILL_CAP, sk[kind] + 1)
        return "cheer", T("Super {training}! Kraft-Herz +1, {skill} {points} (-2 g)",
                          training=training, skill=T(SKILL_DE[kind]), points=sk[kind])
    return "angry", T("{training} daneben ... (-2 g)", training=training)


def clean(pet, minute):
    _usable(pet)
    if pet["poop"] == 0:
        raise Refused(T("Hier ist schon alles sauber."))
    pet["poop"] = 0
    return "clean", T("Alles sauber geputzt!")


def toggle_light(pet, minute):
    """Licht aus schickt es schlafen (tagsüber als Nickerchen), Licht an weckt
    es aus dem Nickerchen. Zur Schlafenszeit bleibt es auch bei Licht im Bett."""
    _usable(pet)
    name = display_name(pet)
    pet["light"] = not pet["light"]
    if not pet["light"]:
        if pet["asleep"]:
            return None, T("Licht aus. Gute Nacht!")
        if pet["stage"] == "Egg":
            return None, T("Licht aus.")
        pet["asleep"], pet["nap"] = True, True
        _log(pet, minute, T("{name} macht ein Nickerchen.", name=name))
        return None, T("Licht aus – {name} macht ein Nickerchen. Licht an weckt es wieder.", name=name)
    if pet.get("nap"):
        pet["asleep"], pet["nap"] = False, False
        _log(pet, minute, T("{name} ist vom Nickerchen aufgewacht.", name=name))
        return "wake", T("Licht an – {name} ist ausgeschlafen!", name=name)
    if pet["asleep"]:
        return None, T("Licht an – aber {name} muss jetzt schlafen. Mach das Licht wieder aus!", name=name)
    return None, T("Licht an.")


def medicine(pet, minute):
    _usable(pet)
    if not (pet["sick"] or pet["injured"]):
        raise Refused(T("{name} ist gesund und braucht keine Medizin.", name=display_name(pet)))
    pet["sick"] = pet["injured"] = False
    pet["sick_since"] = pet["injured_since"] = None
    return "medicine", T("{name} ist wieder gesund!", name=display_name(pet))


# ---------------------------------------------------------------- Anzeige

BATTLE_KEYS = ("win", "btl", "wins")


def _alternatives(pet):
    """Alle Einzel-Bedingungen der möglichen nächsten Formen (ohne Fusionen und Armor-Eier)."""
    for evo in data.evolutions_from(pet["line"], pet["dex"]):
        for alt in evo["rule"].get("any", [evo["rule"]]):
            if "jogress" not in alt and "item" not in alt:
                yield alt


def _battle_routes(pet):
    """Bedingungen, die nur noch Kämpfe brauchen (Pflege & Co. passen schon)."""
    return [alt for alt in _alternatives(pet) if any(k in alt for k in BATTLE_KEYS)
            and _rule_ok(pet, {k: v for k, v in alt.items() if k not in BATTLE_KEYS})]


def _battle_goal(pet):
    """Wie viele Kämpfe/Siege braucht die nächste Digitation? (die leichteste Variante)"""
    goals = []
    for alt in _battle_routes(pet):
        wins = max(alt.get("win", {}).get("wins", 0), (alt.get("wins") or [0])[0])
        battles = max(alt.get("win", {}).get("battles", 0), (alt.get("btl") or [0])[0], wins)
        goals.append((battles, wins))
    if not goals:
        return None
    battles, wins = min(goals)
    return {"battles": battles, "wins": wins}


def _blocked_by_battles(pet):
    """Geht es nur noch über Kämpfe weiter? (keine kampflose Form, deren Regeln passen)"""
    free = [alt for alt in _alternatives(pet) if not any(k in alt for k in BATTLE_KEYS)]
    return bool(_battle_routes(pet)) and not any(_rule_ok(pet, alt, ignore_trainings=True) for alt in free)


def view(pet, now):
    """Was der Browser über das Digimon wissen muss."""
    d = data.DIGIMON.get(pet["dex"]) if pet["dex"] else None
    # offene Rufe mit Grund und Restzeit bis zum Pflegefehler (None = schon gezählt)
    calls = [{"what": k[5:],
              "left": None if pet[k] is False else max(0, CALL_GRACE - (now - pet[k]))}
             for k in ("call_hunger", "call_strength", "call_light") if pet[k] is not None]
    age_days = (now - pet["born"]) // 1440
    return {
        "id": pet.get("id"), "line": pet["line"],
        "name": display_name(pet), "nickname": pet.get("name"),
        "dex": pet["dex"], "stage": pet["stage"], "stage_de": stage_name(pet["stage"]),
        "attribute": d["attribute"] if d else None,
        "alive": pet["alive"], "death_cause": T(pet["death_cause"]) if pet["death_cause"] else None,
        "hunger": pet["hunger"], "strength": pet["strength"], "weight": pet["weight"],
        "poop": pet["poop"], "sick": pet["sick"], "injured": pet["injured"],
        "light": pet["light"], "asleep": pet["asleep"], "nap": bool(pet.get("nap")),
        "frozen": bool(pet.get("frozen")), "in_box": bool(pet.get("in_box")),
        "call": bool(calls) and not pet.get("frozen"), "calls": [] if pet.get("frozen") else calls,
        "age_days": age_days, "mistakes": pet["mistakes"],
        "mistakes_total": pet["mistakes_total"], "trainings": pet["trainings"],
        "overfeeds": pet["overfeeds"], "battles": pet["battles"], "wins": pet["wins"],
        "battles_stage": pet["battles_stage"], "wins_stage": pet["wins_stage"],
        "skills": dict(skills(pet)), "style": style(pet),
        "cheated": bool(pet.get("cheated")), "immortal": bool(pet.get("immortal")),
        "charm": bool(pet.get("charm")), "totem": bool(pet.get("totem")),
        "no_sleep": bool(pet.get("no_sleep")),
        "everstone": bool(pet.get("everstone")),
        # zurück vom Erkunden, wartet auf "OK" (Bericht der Funde)
        "returned": (stored(pet["returned"]["text"], pet["returned"].get("en"))
                     if isinstance(pet.get("returned"), dict) else bool(pet.get("returned"))),
        "goal": pet.get("goal"),                       # Wunsch-Ziel dieses Digimon (Merkliste)
        "stage_minutes": now - pet["stage_since"],
        "evolve_in": (max(0, STAGE_TIME[pet["stage"]] - (now - pet["stage_since"]))
                      if pet["stage"] in STAGE_TIME and data.evolutions_from(pet["line"], pet["dex"])
                      else None),
        "evolve_total": STAGE_TIME.get(pet["stage"]),
        "battle_goal": _battle_goal(pet),
        # nur wenn ALLE nächsten Formen Kämpfe brauchen, ist die Entwicklung blockiert
        "needs_battles": bool(pet["dex"]) and _blocked_by_battles(pet),
        "log": [{"t": e["t"], "text": stored(e["text"], e.get("en"))} for e in pet["log"][-8:]],
    }
