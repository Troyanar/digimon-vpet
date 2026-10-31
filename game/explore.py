"""Erkunden: Expeditionen in Gebiete der Digital World.

Das Digimon ist für 30 Min / 2 Std / 8 Std unterwegs (ohne Hunger und Rufe) und
bringt Ei-Scherben aus dem Gebiet, Items oder nichts mit. Manchmal folgt ihm ein wildes
Digimon nach Hause. Items und Scherben landen im Rucksack des Spielers; 4 Scherben
aus demselben Gebiet ergeben ein Digi-Ei (collection.combine_shards).
"""
import random
from collections import Counter

from . import data, settings
from . import pet as P
from .i18n import T, en_of, join

STAGE_ORDER = ["Fresh", "InTraining", "Rookie", "Champion", "Armor", "Ultimate", "Mega"]

AREAS = {
    "wald": {"name": T("Urwald"), "fields": {"NatureSpirit", "JungleTrooper"}, "min": "Rookie"},
    "kueste": {"name": T("Küste"), "fields": {"DeepSaver"}, "min": "Rookie"},
    "berge": {"name": T("Wolkenberge"), "fields": {"WindGuardian", "VirusBuster"}, "min": "Champion"},
    "stadt": {"name": T("Metallstadt"), "fields": {"MetalEmpire"}, "min": "Champion"},
    "vulkan": {"name": T("Drachenvulkan"), "fields": {"DragonsRoar"}, "min": "Ultimate"},
    "dunkel": {"name": T("Dunkle Zone"), "fields": {"NightmareSoldier", "DarkArea"}, "min": "Ultimate"},
}
# Dauer in Minuten -> Anzahl Fundversuche
TRIPS = {30: 1, 120: 3, 480: 6}
SHARD_CHANCE = 0.10        # pro Fundversuch: eine Ei-Scherbe aus dem Gebiet (so oft wie früher ganze Eier)
SHARDS_PER_EGG = 4         # so viele Scherben ergeben ein Digi-Ei
ITEM_CHANCE = 0.40         # pro Fundversuch (wenn keine Scherbe)
ENCOUNTER_CHANCE = 0.30    # wildes Digimon folgt nach Hause

ITEMS = {
    "snack": {"name": T("Leckerbissen"), "desc": T("Hunger und Kraft voll (+2 g)")},
    "weight": {"name": T("Trainingsgewicht"), "desc": T("+2 Trainings in dieser Stufe")},
    "charm": {"name": T("Glücksbringer"), "desc": T("Nächster Kampf: deutlich stärker")},
    "totem": {"name": T("Schutz-Totem"), "desc": T("Rettet einmal vor dem Tod – ab in den Kühlschrank")},
    "everstone": {"name": T("Ewigstein"), "desc": T("Solange es ihn hält, digitiert es nicht – jederzeit abnehmbar")},
    "hourglass1": {"name": T("Kleine Sanduhr"), "desc": T("Spult das Warten um 1 Std vor (Digitation, Erkunden)")},
    "hourglass3": {"name": T("Sanduhr"), "desc": T("Spult das Warten um 3 Std vor (Digitation, Erkunden)")},
    "hourglass6": {"name": T("Große Sanduhr"), "desc": T("Spult das Warten um 6 Std vor (Digitation, Erkunden)")},
    "erase": {"name": T("Löschdiskette"), "desc": T("Löscht 1 Pflegefehler")},
    # das Gegenstück: für Digitationen, die Pflegefehler brauchen (z. B. Numemon)
    "virus": {"name": T("Virus-Diskette"), "desc": T("Fügt 1 Pflegefehler hinzu – für Digitationen, die Fehler brauchen")},
    # nur im Shop (nie beim Erkunden): macht das aktive Digimon wieder zu einem zufälligen Digi-Ei
    "reset": {"name": T("Reset-Kristall"), "desc": T("Dein Digimon wird wieder zu einem zufälligen Digi-Ei")},
    # Event-Item (Halloween, game/events.py): gibt es nur während des Events
    "candy": {"name": T("Gruselbonbon"), "desc": T("Hunger +1 und Kraft +1 – schaurig lecker")},
    # Armor-Eier: sofortige Armor-Digitation (z. B. Veemon -> Flamedramon); Namen aus data/digimon.json,
    # die englische Fassung steht in game/i18n_en.py
    **{key: {**item, "name": T(item["name"]), "desc": T(item["desc"])} for key, item in data.ARMOR_ITEMS.items()},
}
# Ei-Scherben: eine Sorte pro Gebiet ("shard_wald" …) – gibt es nur beim Erkunden
SHARD_ITEMS = {f"shard_{area}": area for area in AREAS}
ITEMS.update({key: {"name": T("Ei-Scherbe {area}", area=AREAS[area]["name"]),
                    "desc": T("{n} Stück ergeben ein Digi-Ei aus {area}", n=SHARDS_PER_EGG, area=AREAS[area]["name"]),
                    "shard": True} for key, area in SHARD_ITEMS.items()})
# Wie oft welches Item gefunden wird (Gewichte): das Totem etwa jedes 16. Item, jedes
# Armor-Ei etwa jedes 32., das goldene Armor-Ei der Wunder nur etwa jedes 160.
ITEM_ODDS = {"snack": 4, "weight": 4, "charm": 3, "totem": 1,
             "hourglass1": 1.5, "hourglass3": 0.8, "hourglass6": 0.4, "erase": 0.6, "virus": 0.6, "everstone": 0.5,
             **{key: 0.1 if key == "wunder" else 0.5 for key in data.ARMOR_ITEMS}}
HOURGLASS = {"hourglass1": 60, "hourglass3": 180, "hourglass6": 360}      # Minuten


def _pick_item(rng):
    r = rng.random() * sum(ITEM_ODDS.values())
    for key, odds in ITEM_ODDS.items():
        r -= odds
        if r < 0:
            return key
    return "snack"


def _area_of_field(field):
    return next((key for key, a in AREAS.items() if field in a["fields"]), None)


# Was ein Ei ausmacht, sind seine frühen Digimon (spätere Stufen teilen sich viele Eier)
AREA_WEIGHT = {"Fresh": 3, "InTraining": 3, "Rookie": 2, "Champion": 1}


def _area_shares(line):
    """Wie stark gehört eine Ei-Linie zu welchem Gebiet? (über das Field ihrer Digimon,
    frühe Stufen zählen mehr)"""
    shares = Counter()
    for dex in {e["to"] for e in data.EVOLUTIONS if e["line"] == line}:
        d = data.DIGIMON[dex]
        area = _area_of_field(d["field"])
        if area and d["stage"] in AREA_WEIGHT:
            shares[area] += AREA_WEIGHT[d["stage"]]
    return shares


def _assign_areas():
    """Gebiet jeder Ei-Linie = wo die meisten ihrer Digimon zu Hause sind. Bleibt ein
    Gebiet leer, bekommt es die Linie, die dort am stärksten vertreten ist (von einem
    Gebiet, das mehrere Linien hat) – so findet man überall Eier."""
    shares = {line: _area_shares(line) for line in data.NORMAL_LINES}     # Event-Eier gehören nirgends hin
    assign = {line: (s.most_common(1)[0][0] if s else "wald") for line, s in shares.items()}
    for area in AREAS:
        if area in assign.values():
            continue
        crowded = Counter(assign.values())
        donors = [line for line in assign if crowded[assign[line]] > 1]
        if donors:
            assign[max(donors, key=lambda l: (shares[l][area], l))] = area
    return assign


LINE_AREA = _assign_areas()


def area_lines(area):
    return [line for line, a in LINE_AREA.items() if a == area]


def unlocked(pet, area):
    return STAGE_ORDER.index(pet["stage"]) >= STAGE_ORDER.index(AREAS[area]["min"])


# ---------------------------------------------------------------- Start / Abbruch

def start(pet, area, minutes, now):
    name = P.display_name(pet)
    P._awake_check(pet)
    if area not in AREAS or minutes not in TRIPS:
        raise P.Refused(T("Dieses Ziel gibt es nicht."))
    if not unlocked(pet, area):
        raise P.Refused(T("In {area} ist es zu gefährlich – erst ab {stage}.",
                          area=AREAS[area]["name"], stage=P.stage_name(AREAS[area]["min"])))
    if pet["sick"] or pet["injured"]:
        raise P.Refused(T("{name} ist nicht fit genug. Erst Medizin!", name=name))
    if pet["hunger"] == 0:
        raise P.Refused(T("{name} braucht Proviant – erst füttern.", name=name))
    if pet.get("battle") or pet.get("scout"):
        raise P.Refused(T("Erst den Kampf beenden."))
    pet["hunger"] -= 1
    pet["expedition"] = {"area": area, "start": now, "end": now + minutes, "minutes": minutes}
    for key in ("call_hunger", "call_strength", "call_light"):
        if pet[key] is not False:            # schon gezählte Pflegefehler nicht „vergessen“
            pet[key] = None
    P._log(pet, now, T("{name} erkundet {area}.", name=name, area=AREAS[area]["name"]))
    return T("{name} zieht los in {area}! Zurück in {duration}.",
             name=name, area=AREAS[area]["name"], duration=_duration(minutes))


def recall(pet, now):
    """Vorzeitig zurückrufen – dann ohne Funde."""
    exp = pet.get("expedition")
    if not exp:
        raise P.Refused(T("Dein Digimon ist gar nicht unterwegs."))
    pet.pop("expedition")
    P._log(pet, now, T("{name} wurde zurückgerufen.", name=P.display_name(pet)))
    return T("{name} ist zurück – leider mit leeren Händen.", name=P.display_name(pet))


def _duration(minutes):
    return T("{n} Min", n=minutes) if minutes < 60 else T("{n} Std", n=minutes // 60)


def egg_found(line, kept):
    """Ein gefundenes Ei für den Bericht – "ein Digi-Ei" (nur Event-Eier mit Sorte, siehe
    data.egg_name), ggf. mit "Sammlung voll"."""
    egg = data.egg_name(line)
    return T("ein {egg}", egg=egg) if kept else T("ein {egg} (Sammlung voll – liegen gelassen)", egg=egg)


def report_text(name, area, parts):
    """Bericht nach der Rückkehr: "<Name> ist zurück aus <Gebiet>! Gefunden: …"."""
    head = T("{name} ist zurück aus {area}!", name=name, area=AREAS[area]["name"])
    if parts:
        return head + " " + T("Gefunden: {things}.", things=join(", ", parts))
    return head + " " + T("Diesmal nichts gefunden.")


# ---------------------------------------------------------------- Rückkehr

def roll(pet, trip, rng=random):
    """Was wurde gefunden? -> {"shards": Anzahl, "eggs": [Linie, ...] (nur Event-Extras),
    "items": [...], "encounter": Nr|None}"""
    found = {"shards": 0, "eggs": [], "items": [], "encounter": None}
    luck = settings.CURRENT["explore_luck"]                  # Fundglück aus den Admin-Regeln
    shard_chance = min(0.45, SHARD_CHANCE * luck)
    item_chance = min(0.95 - shard_chance, ITEM_CHANCE * luck)
    for _ in range(TRIPS[trip["minutes"]]):
        r = rng.random()
        if r < shard_chance:
            found["shards"] += 1
        elif r < shard_chance + item_chance:
            found["items"].append(_pick_item(rng))
    if pet["stage"] in STAGE_ORDER[2:] and rng.random() < ENCOUNTER_CHANCE:
        fields = AREAS[trip["area"]]["fields"]
        pool = [dex for dex, d in data.WILD.items()
                if d["stage"] == pet["stage"] and d["field"] in fields] \
            or [dex for dex, d in data.WILD.items() if d["stage"] == pet["stage"]]
        found["encounter"] = rng.choice(pool)
    return found


def found_bits(trip, add_bits, rng=random):
    """Bits von einer Expedition (immer ein paar) -> Text für den Bericht."""
    from . import shop
    if not add_bits:
        return []
    n = shop.trip_reward(trip["minutes"], rng)
    if n:
        add_bits(n)
        return [T("{n} Bits", n=n)]
    return []


def found_shards(area, n, add_item):
    """Ei-Scherben in den Rucksack -> Text für den Bericht ("3× Ei-Scherbe Urwald")."""
    if not n:
        return []
    key = f"shard_{area}"
    for _ in range(n):
        add_item(key)
    return [ITEMS[key]["name"] if n == 1 else T("{n}× {item}", n=n, item=ITEMS[key]["name"])]


def claim(pet, now, store_egg, add_item, rng=random, add_bits=None, extra=None):
    """Wertet eine beendete Expedition aus (einmalig). Liefert einen Bericht oder None.
    `store_egg(line) -> bool` legt ein Ei in die Sammlung, `add_item(key)` füllt den Rucksack,
    `add_bits(n)` schreibt Bits gut, `extra` = Zusatz-Funde eines Events {"eggs": […], "items": […]}."""
    trip = pet.pop("expedition_return", None)
    if not trip:
        return None
    name = P.display_name(pet)
    found = roll(pet, trip, rng)
    if extra:
        found["eggs"] += extra.get("eggs", [])
        found["items"] += extra.get("items", [])
    parts = found_bits(trip, add_bits, rng) + found_shards(trip["area"], found["shards"], add_item)
    for line in found["eggs"]:
        parts.append(egg_found(line, store_egg(line)))
    for item in found["items"]:
        add_item(item)
        parts.append(ITEMS[item]["name"])
    text = report_text(name, trip["area"], parts)
    if found["encounter"]:
        from . import battle
        opp_power = battle.STAGE_POWER[pet["stage"]] + 5 * rng.randint(1, 4) + rng.randint(0, 10)
        pet["scout"] = {"dex": found["encounter"], "power": opp_power, "time": now}
        text += " " + T("Ein wildes {name} ist ihm gefolgt!", name=data.DIGIMON[found["encounter"]]["name"])
    P._log(pet, now, text)
    # der Bericht bleibt stehen, bis der Spieler die Rückkehr bestätigt (P.confirm_return)
    if pet.get("returned"):
        pet["returned"] = {"text": str(text), "en": en_of(text)}
    return {"text": text, "shards": found["shards"], "eggs": len(found["eggs"]), "items": found["items"],
            "encounter": bool(found["encounter"])}


# ---------------------------------------------------------------- Rucksack

def use_item(pet, item, now):
    name = P.display_name(pet)
    # Sanduhr und Löschdiskette gehen auch im Schlaf und unterwegs (sie spulen ja nur Uhren vor
    # bzw. löschen einen Fehler) – alles andere braucht ein waches Digimon
    if item in HOURGLASS:
        return _hourglass(pet, item, now)
    if item == "erase":
        return _erase(pet, now)
    if item == "virus":
        return _virus(pet, now)
    if item in SHARD_ITEMS:
        # zusammensetzen geht über den Rucksack (collection.combine_shards), nicht am Digimon
        raise P.Refused(T("Ei-Scherben setzt du im Rucksack zusammen."))
    if item == "reset":
        return _reset(pet, now)
    if item in ("snack", "candy"):
        P.wake_for_food(pet, now)            # Leckerbissen weckt aus dem Nickerchen wie Futter
    P._awake_check(pet)
    if item == "snack":
        pet["hunger"] = pet["strength"] = P.MAX_HEARTS
        pet["weight"] += 2
        return "eat", T("{name} verputzt den Leckerbissen. Hunger und Kraft voll!", name=name)
    if item == "candy":
        pet["hunger"] = min(P.MAX_HEARTS, pet["hunger"] + 1)
        pet["strength"] = min(P.MAX_HEARTS, pet["strength"] + 1)
        pet["weight"] += 1
        return "eat", T("{name} nascht ein Gruselbonbon. Hunger +1, Kraft +1 – schaurig lecker!", name=name)
    if item == "weight":
        if pet["sick"] or pet["injured"]:
            raise P.Refused(T("{name} ist nicht fit genug zum Trainieren.", name=name))
        pet["trainings"] += 2
        return "lift", T("{name} stemmt das Trainingsgewicht. +2 Trainings!", name=name)
    if item == "charm":
        if pet.get("charm"):
            raise P.Refused(T("{name} trägt schon einen Glücksbringer.", name=name))
        pet["charm"] = True
        return "charm", T("{name} trägt jetzt den Glücksbringer – der nächste Kampf wird leichter!", name=name)
    if item == "totem":
        if pet.get("totem"):
            raise P.Refused(T("{name} hält schon ein Schutz-Totem.", name=name))
        pet["totem"] = True
        return "totem", T("{name} hält jetzt das Schutz-Totem. Stirbt es, rettet das Totem es einmal – es landet dann im Kühlschrank.",
                          name=name)
    if item == "everstone":
        if pet.get("everstone"):
            raise P.Refused(T("{name} hält schon einen Ewigstein.", name=name))
        pet["everstone"] = True
        return "charm", T("{name} hält jetzt den Ewigstein und digitiert nicht mehr von selbst. "
                          "Abnehmen kannst du ihn jederzeit im Rucksack.", name=name)
    if item in data.ARMOR_ITEMS:
        return _armor(pet, item, now)
    raise P.Refused(T("Dieses Item gibt es nicht."))


def take_everstone(pet, now):
    """Ewigstein abnehmen (kommt zurück in den Rucksack). Ist die Zeit schon um, digitiert
    das Digimon gleich danach – sobald es wach ist."""
    if not pet.get("everstone"):
        raise P.Refused(T("{name} hält keinen Ewigstein.", name=P.display_name(pet)))
    if not pet["alive"]:
        raise P.Refused(T("Dein Digimon lebt nicht mehr."))
    pet.pop("everstone")
    return None, T("Ewigstein abgenommen – {name} kann wieder digitieren. Der Stein ist zurück im Rucksack.",
                   name=P.display_name(pet))


def _check_usable_anytime(pet):
    """Lebt, ist nicht im Kühlschrank und kein Kampf läuft – schlafen oder unterwegs ist egal."""
    if not pet["alive"]:
        raise P.Refused(T("Dein Digimon lebt nicht mehr."))
    if pet.get("frozen"):
        raise P.Refused(T("{name} ist im Kühlschrank. Erst auftauen!", name=P.display_name(pet)))
    if pet.get("battle"):
        raise P.Refused(T("Erst den Kampf beenden."))


def _digivolution_wait(pet, now):
    """Restzeit bis zur Digitation – oder der Grund, warum es da nichts vorzuspulen gibt."""
    name = P.display_name(pet)
    if pet["stage"] not in P.STAGE_TIME or not data.evolutions_from(pet["line"], pet["dex"]):
        return None, T("{name} ist in der Endstufe – da gibt es nichts vorzuspulen.", name=name)
    if pet.get("everstone"):
        return None, T("{name} hält den Ewigstein – erst abnehmen, sonst bringt die Sanduhr nichts.", name=name)
    left = P.STAGE_TIME[pet["stage"]] - (now - pet["stage_since"])
    if left <= 0:
        return None, T("Die Digitation von {name} ist schon fällig – warten lohnt sich hier nicht mehr.", name=name)
    return left, None


def _hourglass(pet, item, now):
    """Sanduhr: spult nur das WARTEN vor – die Zeit bis zur Digitation (bzw. bis das Ei schlüpft)
    und, wenn es unterwegs ist, auch die Zeit bis zur Rückkehr vom Erkunden.
    Hunger, Kacke und Rufe laufen dabei nicht mit."""
    _check_usable_anytime(pet)
    name, minutes = P.display_name(pet), HOURGLASS[item]
    hours = minutes // 60
    evo_left, why_not = _digivolution_wait(pet, now)
    # aktives Digimon unterwegs: "expedition", Digimon aus der Sammlung unterwegs: "box_trip"
    trip = pet.get("expedition") or pet.get("box_trip")
    if trip:
        # unterwegs läuft die Digitationszeit ja weiter -> beide Uhren vorspulen
        trip["end"] = max(now, trip["end"] - minutes)
        trip["start"] -= minutes
        left = trip["end"] - now
        if left <= 0:
            text = T("Die Sanduhr spult {h} Std vor – {name} ist gleich zurück vom Erkunden!", h=hours, name=name)
        else:
            text = T("Die Sanduhr spult {h} Std vor – {name} ist in {left} zurück.",
                     h=hours, name=name, left=P.duration_text(left))
        if evo_left:
            pet["stage_since"] -= minutes
            if evo_left <= minutes:
                text += " " + T("Die Digitation ist fällig – sie kommt, sobald es zurück ist.")
            else:
                text += " " + T("Digitation in {left}.", left=P.duration_text(evo_left - minutes))
        return "happy", text
    if not evo_left:
        raise P.Refused(why_not)
    pet["stage_since"] -= minutes
    left = evo_left - minutes
    if left <= 0:
        if pet.get("in_box"):
            # in der Sammlung steht die Zeit still -> es digitiert, sobald es wieder aktiv ist
            when = T("fällig – es digitiert, sobald du es aktiv setzt")
        elif pet["asleep"] and not pet.get("nap"):
            when = T("im Schlaf fällig – es digitiert nach dem Aufwachen")
        else:
            when = T("gleich so weit")
        return "happy", T("Die Sanduhr spult {h} Std vor – die Digitation ist {when}!", h=hours, when=when)
    return "happy", T("Die Sanduhr spult {h} Std vor – Digitation in {left}.", h=hours, left=P.duration_text(left))


RESET_KEEP = ("id", "name", "battles", "wins", "cheated", "immortal", "no_sleep", "totem", "log", "forms", "box")


def _reset(pet, now, rng=random):
    """Reset-Kristall: das aktive Digimon wird wieder zu einem zufälligen Digi-Ei. Spitzname,
    Siege (Rangliste), gehaltenes Schutz-Totem und das Tagebuch bleiben."""
    _check_usable_anytime(pet)
    P._away_check(pet)
    name = P.display_name(pet)
    if pet["stage"] == "Egg":
        raise P.Refused(T("Das ist schon ein Ei."))
    if pet.get("scout"):
        raise P.Refused(T("Erst den Kampf beenden (oder fliehen)."))
    if pet.get("everstone"):
        raise P.Refused(T("{name} hält den Ewigstein – erst abnehmen, dann geht der Reset.", name=name))
    forms = pet.setdefault("forms", [])               # die jetzige Form bleibt in der Sammlung
    if pet.get("dex") is not None and pet["dex"] not in forms:
        forms.append(pet["dex"])
    keep = {k: pet[k] for k in RESET_KEEP if k in pet}
    pet.clear()
    pet.update(P.new_egg(rng.choice(data.NORMAL_LINES), now))
    pet.update(keep)
    P._log(pet, now, T("Reset-Kristall: {name} ist wieder ein Digi-Ei.", name=name))
    return "reset", T("Der Reset-Kristall leuchtet … {name} wird wieder zu einem Digi-Ei! Was wohl diesmal daraus schlüpft?",
                      name=name)


def _erase(pet, now):
    """Löschdiskette: 1 Pflegefehler weg (in dieser Stufe und insgesamt)."""
    _check_usable_anytime(pet)
    name = P.display_name(pet)
    if pet["mistakes_total"] <= 0 and pet["mistakes"] <= 0:
        raise P.Refused(T("{name} hat keine Pflegefehler – die Diskette bleibt im Rucksack.", name=name))
    pet["mistakes"] = max(0, pet["mistakes"] - 1)
    pet["mistakes_total"] = max(0, pet["mistakes_total"] - 1)
    P._log(pet, now, T("Löschdiskette: 1 Pflegefehler gelöscht."))
    return "happy", T("Gelöscht! {name} hat jetzt {n} Pflegefehler in dieser Stufe ({total} insgesamt).",
                      name=name, n=pet["mistakes"], total=pet["mistakes_total"])


def _virus(pet, now):
    """Virus-Diskette: 1 Pflegefehler dazu (in dieser Stufe und insgesamt) – aber nie so viele,
    dass das Digimon daran stirbt."""
    _check_usable_anytime(pet)
    name = P.display_name(pet)
    if pet["stage"] == "Egg":
        raise P.Refused(T("Ein Ei kann noch keine Pflegefehler haben."))
    if pet["mistakes_total"] + 1 >= P.MAX_MISTAKES:
        raise P.Refused(T("Noch ein Pflegefehler wäre für {name} zu gefährlich ({total} von höchstens {max}) – "
                          "die Diskette bleibt im Rucksack.", name=name, total=pet["mistakes_total"], max=P.MAX_MISTAKES - 1))
    pet["mistakes"] += 1
    pet["mistakes_total"] += 1
    P._log(pet, now, T("Virus-Diskette: 1 Pflegefehler dazu."))
    return "angry", T("Die Virus-Diskette rauscht … {name} hat jetzt {n} Pflegefehler in dieser Stufe ({total} insgesamt).",
                     name=name, n=pet["mistakes"], total=pet["mistakes_total"])


def armor_options(pet):
    """Welche Armor-Eier passen zu diesem Digimon? {Item-Key: Entwicklung}"""
    if not pet.get("dex") or not pet["alive"]:
        return {}
    return {e["rule"]["item"]: e for e in data.evolutions_from(pet["line"], pet["dex"]) if "item" in e["rule"]}


def _armor(pet, item, now):
    """Armor-Digitation: passt das Armor-Ei, digitiert das Digimon sofort."""
    name, egg = P.display_name(pet), ITEMS[item]
    evo = armor_options(pet).get(item)
    if not evo:
        raise P.Refused(T("„{egg}“ passt nicht zu {name} – {desc}.", egg=egg["name"], name=name, desc=egg["desc"]))
    if pet["sick"] or pet["injured"]:
        raise P.Refused(T("{name} ist nicht fit genug für eine Digitation. Erst Medizin!", name=name))
    P._evolve(pet, evo, now)
    new = P.display_name(pet)
    P._log(pet, now, T("Armor-Digitation mit „{egg}“: {new}!", egg=egg["name"], new=new))
    return "armor", T("{name}, Armor-Digitation! Mit „{egg}“ wird es zu {new}!", name=name, egg=egg["name"], new=new)


def view(pet, now):
    exp = pet.get("expedition")
    if not exp:
        return {"away": None}
    return {"away": {"area": exp["area"], "area_name": AREAS[exp["area"]]["name"],
                     "minutes_left": max(0, exp["end"] - now), "minutes": exp["minutes"],
                     "end": exp["end"]}}


def areas_for(pet):
    return [{"key": k, "name": a["name"], "min": P.stage_name(a["min"]),
             "unlocked": unlocked(pet, k) if pet.get("dex") else False,
             "eggs": len(area_lines(k))} for k, a in AREAS.items()]
