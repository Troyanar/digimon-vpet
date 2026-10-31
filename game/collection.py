"""Sammlung: mehrere Digimon und Eier pro Spieler, eins davon ist aktiv.

In der Sammlung steht die Zeit still (``in_box``). Sie ist wie der PC bei Pokémon in
Boxen aufgeteilt (``pet["box"]``), die man benennen kann. Verstorbene Digimon bleiben
als Erinnerung erhalten.
"""
import random

from . import data, explore, settings
from . import pet as P
from .i18n import T, en_of, stored

BOXES = 8                     # Anzahl Boxen
PER_BOX = 20                  # Plätze pro Box
BOX_SIZE = BOXES * PER_BOX    # Plätze in der Sammlung insgesamt (ohne das aktive Digimon)
NAME_MAX = 16
MAX_TRIPS = 3                 # so viele Digimon aus der Sammlung dürfen gleichzeitig erkunden


def _migrate(store, owner):
    """Früher wurden Digimon beim Neustart freigelassen – lebende kommen jetzt in
    die Sammlung (eingefroren ab dem Moment, als sie freigelassen wurden)."""
    for pet in store.all_pets(owner):
        if not pet["active"] and pet.get("alive") and not pet.get("in_box") and pet.get("released"):
            pet["in_box"] = True
            pet["last"] = pet.pop("released")
            store.save_pet(pet)


def boxed(store, owner):
    return [p for p in store.all_pets(owner) if not p["active"] and p.get("in_box")]


def layout(store, owner):
    """Ordnet jedem Digimon der Sammlung eine Box zu: wer schon eine (nicht volle) Box hat,
    bleibt dort, alle anderen (neu, getauscht, alte Spielstände) kommen in die erste Box
    mit freiem Platz. Liefert die Sammlung, älteste zuerst."""
    pets = sorted(boxed(store, owner), key=lambda p: p["id"])
    count = [0] * BOXES
    homeless = []
    for pet in pets:
        b = pet.get("box")
        if isinstance(b, int) and 0 <= b < BOXES and count[b] < PER_BOX:
            count[b] += 1
        else:
            homeless.append(pet)
    for pet in homeless:
        pet["box"] = next((i for i in range(BOXES) if count[i] < PER_BOX), BOXES - 1)
        count[pet["box"]] += 1
        store.save_pet(pet)
    return pets


def box_names(store, owner):
    names = store.get_meta(f"boxnames:{owner}", None) or []
    return [(names[i] if i < len(names) and names[i] else T("Box {n}", n=i + 1)) for i in range(BOXES)]


def rename_box(store, owner, box, name):
    if not isinstance(box, int) or not 0 <= box < BOXES:
        raise P.Refused(T("Diese Box gibt es nicht."))
    name = " ".join(str(name or "").split())[:NAME_MAX]
    names = box_names(store, owner)
    names[box] = name or T("Box {n}", n=box + 1)
    store.set_meta(f"boxnames:{owner}", [str(n) for n in names])
    return T("Die Box heißt jetzt „{name}“.", name=names[box])


def move(store, owner, pet_id, box):
    """Ein Digimon/Ei in eine andere Box legen."""
    if not isinstance(box, int) or not 0 <= box < BOXES:
        raise P.Refused(T("Diese Box gibt es nicht."))
    pets = layout(store, owner)
    target = next((p for p in pets if p["id"] == pet_id), None)
    if not target:
        raise P.Refused(T("Dieses Digimon ist nicht in deiner Sammlung."))
    if target["box"] == box:
        return T("{name} ist schon in dieser Box.", name=P.display_name(target))
    if sum(p["box"] == box for p in pets) >= PER_BOX:
        raise P.Refused(T("{box} ist voll ({n} Plätze).", box=box_names(store, owner)[box], n=PER_BOX))
    target["box"] = box
    store.save_pet(target)
    return T("{name} liegt jetzt in {box}.", name=P.display_name(target), box=box_names(store, owner)[box])


def _stash_active(store, owner, now, free_slots=0, box=None):
    """Legt das aktive Digimon in die Sammlung (verstorbene werden zur Erinnerung) –
    in Box `box`, sonst in seine alte Box bzw. die erste mit Platz."""
    pet = store.active_pet(owner)
    if not pet:
        return
    P.advance(pet, now)
    if pet["alive"]:
        P._away_check(pet)
        if len(boxed(store, owner)) - free_slots >= BOX_SIZE:
            raise P.Refused(T("Die Sammlung ist voll ({n} Plätze). Lass erst eins frei.", n=BOX_SIZE))
        pet["in_box"] = True
        pet["frozen"] = False
        if box is not None:
            pet["box"] = box
        P._log(pet, now, T("{name} ruht jetzt in der Sammlung.", name=P.display_name(pet)))
    store.save_pet(pet, active=False)


def new_egg(store, owner, now, line=None, cheated=False):
    """Neues Ei wird aktiv; das bisherige Digimon kommt in die Sammlung."""
    _migrate(store, owner)
    _stash_active(store, owner, now)
    egg = P.new_egg(line or random.choice(data.NORMAL_LINES), now)
    if cheated:
        egg["cheated"] = True
    return store.add_pet(owner, egg)


def can_get_free_egg(store, owner):
    """Gratis-Ei nur als Notnagel: wenn man gar kein Digimon und kein Ei mehr hat."""
    _migrate(store, owner)
    pet = store.active_pet(owner)
    if not settings.CURRENT["free_egg"]:
        return False
    return not (pet and pet.get("alive")) and not boxed(store, owner)


def store_egg(store, owner, line, now):
    """Ein gefundenes Ei kommt in die Sammlung. False, wenn sie voll ist."""
    _migrate(store, owner)
    if len(boxed(store, owner)) >= BOX_SIZE:
        return False
    egg = P.new_egg(line, now)
    egg["in_box"] = True
    store.add_pet(owner, egg, active=False)
    return True


def combine_shards(store, owner, item, have, take, now, rng=random):
    """4 Ei-Scherben aus einem Gebiet -> ein Digi-Ei aus diesem Gebiet in der Sammlung.
    `have` = Scherben im Rucksack, `take(n)` nimmt sie heraus. Liefert die Meldung."""
    area = explore.SHARD_ITEMS.get(item)
    if not area:
        raise P.Refused(T("Das ist keine Ei-Scherbe."))
    need = explore.SHARDS_PER_EGG
    if have < need:
        raise P.Refused(T("Für ein Digi-Ei brauchst du {need} Scherben – du hast erst {have}. Erkunde {area}!",
                          need=need, have=have, area=explore.AREAS[area]["name"]))
    if not store_egg(store, owner, rng.choice(explore.area_lines(area) or list(data.NORMAL_LINES)), now):
        raise P.Refused(T("Deine Sammlung ist voll – mach erst Platz, dann setz die Scherben zusammen."))
    take(need)
    return T("Die {n} Scherben fügen sich zusammen … ein Digi-Ei aus {area}! Es liegt jetzt in deiner Sammlung.",
             n=need, area=explore.AREAS[area]["name"])


def switch(store, owner, pet_id, now):
    _migrate(store, owner)
    target = next((p for p in layout(store, owner) if p["id"] == pet_id), None)
    if not target:
        raise P.Refused(T("Dieses Digimon ist nicht in deiner Sammlung."))
    _trip_check(target)
    _stash_active(store, owner, now, free_slots=1, box=target["box"])     # tauscht den Platz
    P.advance(target, now)          # Uhren dort weiterlaufen lassen, wo sie standen
    target["in_box"] = False
    P._log(target, now, T("{name} ist wieder dein Partner!", name=P.display_name(target)))
    store.save_pet(target, active=True)
    return T("{name} ist jetzt aktiv.", name=P.display_name(target))


def _trip_check(pet):
    trip = pet.get("box_trip")
    if trip:
        end = P.local_time(trip["end"]).strftime("%H:%M")
        raise P.Refused(T("{name} erkundet gerade {area} – zurück um {end} Uhr.",
                          name=P.display_name(pet), area=explore.AREAS[trip["area"]]["name"], end=end))


# ---------------------------------------------------------------- Erkunden aus der Sammlung
# Digimon in der Sammlung können auch auf Expedition (höchstens MAX_TRIPS gleichzeitig).
# Für sie steht die Zeit weiter still (kein Hunger, keine Rufe) – nur die Reise läuft,
# deshalb hat sie eigene Zeitpunkte (``box_trip``), die beim Einfrieren nicht mitwandern.

def send(store, owner, pet_id, area, minutes, now):
    pets = layout(store, owner)
    pet = next((p for p in pets if p["id"] == pet_id), None)
    if not pet:
        raise P.Refused(T("Dieses Digimon ist nicht in deiner Sammlung."))
    name = P.display_name(pet)
    _trip_check(pet)
    if not pet["alive"] or pet["stage"] == "Egg":
        raise P.Refused(T("Eier können nicht erkunden."))
    if area not in explore.AREAS or minutes not in explore.TRIPS:
        raise P.Refused(T("Dieses Ziel gibt es nicht."))
    if not explore.unlocked(pet, area):
        raise P.Refused(T("In {area} ist es für {name} zu gefährlich – erst ab {stage}.",
                          area=explore.AREAS[area]["name"], name=name,
                          stage=P.stage_name(explore.AREAS[area]["min"])))
    if pet["sick"] or pet["injured"]:
        raise P.Refused(T("{name} ist nicht fit genug. Erst Medizin – dafür muss es aktiv sein.", name=name))
    if sum(1 for p in pets if p.get("box_trip")) >= MAX_TRIPS:
        raise P.Refused(T("Es sind schon {n} Digimon aus deiner Sammlung unterwegs.", n=MAX_TRIPS))
    pet["box_trip"] = {"area": area, "start": now, "end": now + minutes, "minutes": minutes}
    P._log(pet, now, T("{name} erkundet {area}.", name=name, area=explore.AREAS[area]["name"]))
    store.save_pet(pet)
    return T("{name} zieht los in {area}! Zurück in {duration}.",
             name=name, area=explore.AREAS[area]["name"], duration=explore._duration(minutes))


def recall_trip(store, owner, pet_id, now):
    pet = next((p for p in boxed(store, owner) if p["id"] == pet_id), None)
    if not pet or not pet.get("box_trip"):
        raise P.Refused(T("Dieses Digimon ist gar nicht unterwegs."))
    pet.pop("box_trip")
    P._log(pet, now, T("{name} wurde zurückgerufen.", name=P.display_name(pet)))
    store.save_pet(pet)
    return T("{name} ist zurück – leider mit leeren Händen.", name=P.display_name(pet))


def claim_trips(store, owner, now, add_item, rng=random, add_bits=None, extra=None):
    """Wertet beendete Reisen aus der Sammlung aus. Liefert die Berichte (Texte).
    Wilde Digimon folgen dabei nicht nach Hause – kämpfen kann nur das aktive Digimon.
    `add_bits(n)` schreibt die gefundenen Bits gut, `extra()` liefert Zusatz-Funde eines Events."""
    reports = []
    for pet in boxed(store, owner):
        trip = pet.get("box_trip")
        if not trip or trip["end"] > now:
            continue
        pet.pop("box_trip")
        store.save_pet(pet)                  # zuerst: Funde gibt es genau einmal
        found = explore.roll(pet, trip, rng)
        if extra:
            bonus = extra()
            found["eggs"] += bonus.get("eggs", [])
            found["items"] += bonus.get("items", [])
        parts = explore.found_bits(trip, add_bits, rng) + explore.found_shards(trip["area"], found["shards"], add_item)
        for line in found["eggs"]:
            parts.append(explore.egg_found(line, store_egg(store, owner, line, now)))
        for item in found["items"]:
            add_item(item)
            parts.append(explore.ITEMS[item]["name"])
        text = explore.report_text(P.display_name(pet), trip["area"], parts)
        P._log(pet, now, text)
        store.save_pet(pet)
        _remember_trip(store, owner, now, text)
        reports.append(text)
    return reports


# ---------------------------------------------------------------- Übersicht "Zurück vom Erkunden"
# Die letzten Berichte von Sammlungs-Expeditionen (meta "tripreports:<owner>", neueste zuerst) –
# damit man auch später noch sieht, was mitgebracht wurde.
TRIP_REPORTS_MAX = 15


def _remember_trip(store, owner, now, text):
    items = store.get_meta(f"tripreports:{owner}", []) or []
    items.insert(0, {"t": now, "text": str(text), "en": en_of(text)})
    store.set_meta(f"tripreports:{owner}", items[:TRIP_REPORTS_MAX])


def trip_reports(store, owner):
    return [{"t": r["t"], "text": stored(r["text"], r.get("en"))}
            for r in store.get_meta(f"tripreports:{owner}", []) or []]


def use_hourglass(store, owner, pet_id, item, now):
    """Sanduhr für ein Digimon aus der Sammlung, das gerade erkundet: verkürzt seine Reise und
    spult die Zeit bis zur Digitation vor. Ohne Reise geht es nicht – in der Sammlung steht die
    Zeit still (sonst sah es so aus, als träfe die Sanduhr das aktive Digimon)."""
    pet = next((p for p in boxed(store, owner) if p["id"] == pet_id), None)
    if not pet:
        raise P.Refused(T("Dieses Digimon ist nicht in deiner Sammlung."))
    if item not in explore.HOURGLASS:
        raise P.Refused(T("Für Digimon in der Sammlung gehen nur Sanduhren."))
    if pet["alive"] and pet["stage"] == "Egg":
        raise P.Refused(T("Ein Ei schlüpft sofort, wenn du es ausbrütest – da gibt es nichts vorzuspulen."))
    if not pet.get("box_trip"):
        raise P.Refused(T("Das geht nicht: {name} ruht in der Sammlung, dort steht die Zeit still. Eine Sanduhr "
                          "geht nur für dein aktives Digimon oder für Digimon aus der Sammlung, die gerade erkunden.",
                          name=P.display_name(pet)))
    P.advance(pet, now)              # eingefrorene Uhren auf jetzt schieben
    _, message = explore.use_item(pet, item, now)
    store.save_pet(pet)
    return message


def trip_view(pet, now):
    trip = pet.get("box_trip")
    if not trip:
        return None
    return {"area": trip["area"], "area_name": explore.AREAS[trip["area"]]["name"],
            "end": trip["end"], "minutes_left": max(0, trip["end"] - now)}


def release(store, owner, pet_id):
    target = next((p for p in boxed(store, owner) if p["id"] == pet_id), None)
    if not target:
        raise P.Refused(T("Dieses Digimon ist nicht in deiner Sammlung."))
    _trip_check(target)
    store.delete_pet(owner, pet_id)
    return T("{name} wurde freigelassen. Mach's gut!", name=P.display_name(target))


def ranking(store):
    """Rangliste aller Spieler nach Siegen (über alle ihre Digimon zusammen) – ohne Admins."""
    rows = []
    for user in store.all_users():
        if user["is_admin"]:
            continue
        pets = store.all_pets(str(user["id"]))
        active = next((p for p in pets if p["active"] and p.get("alive")), None)
        rows.append({
            "name": user["name"],
            "wins": sum(p.get("wins", 0) for p in pets),
            "battles": sum(p.get("battles", 0) for p in pets),
            "partner": P.label(active) if active else None,
            "cheated": any(p.get("cheated") for p in pets),
        })
    rows.sort(key=lambda r: (-r["wins"], r["battles"], r["name"].lower()))
    return rows


def overview(store, owner, now):
    _migrate(store, owner)
    box = [{**P.view(pet, now), "box": pet["box"], "trip": trip_view(pet, now),
            "areas": [a["key"] for a in explore.areas_for(pet) if a["unlocked"]]} for pet in layout(store, owner)]
    memories = [{"name": P.display_name(pet), "dex": pet["dex"],
                 "cause": T(pet["death_cause"]) if pet.get("death_cause") else None, "died": pet.get("died")}
                for pet in store.all_pets(owner) if not pet["active"] and not pet.get("in_box") and not pet.get("alive")]
    return {"box": box, "box_size": BOX_SIZE, "boxes": box_names(store, owner), "per_box": PER_BOX,
            "memories": memories[:20], "max_trips": MAX_TRIPS, "trip_reports": trip_reports(store, owner),
            "area_names": {k: a["name"] for k, a in explore.AREAS.items()}}
