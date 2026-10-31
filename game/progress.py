"""Sammel-Fortschritt (wie der Pokédex) und Erfolge.

Gesammelt = jede Form, die eines deiner Digimon je hatte (``pet["forms"]``) – gemerkt pro
Konto in meta "dex:<owner>", damit freigelassene oder getauschte Digimon gezählt bleiben. Erfolge gibt es für Sammeln, Stufen, Kämpfe, Erkunden … – jeder bringt einmalig
Bits (game/shop.py). Zähler für Dinge, die man den Digimon nicht ansieht (Siege gesamt,
Expeditionen …), stehen in meta "stats:<owner>".
"""
from . import data, shop
from .i18n import T

# Digimon-Nummern, die man sammeln kann (alles, was in einem Ei vorkommt)
COLLECTABLE = set(data.PLAYABLE)
ARMOR_FORMS = {dex for dex in COLLECTABLE if data.DIGIMON[dex]["stage"] == "Armor"}


def _named(name):
    return next((dex for dex in COLLECTABLE if data.DIGIMON[dex]["name"] == name), None)


PUMPKINMON = _named("Pumpkinmon")


# ---------------------------------------------------------------- Sammlung

def owned(store, owner):
    return set(store.get_meta(f"dex:{owner}", []) or [])


def sync(store, owner, pets=None):
    """Alle Formen aller Digimon des Kontos übernehmen. Liefert die gesammelten Nummern."""
    have = owned(store, owner)
    before = len(have)
    for pet in pets if pets is not None else store.all_pets(owner):
        have.update(d for d in pet.get("forms", []) if d in COLLECTABLE)
        if pet.get("dex") in COLLECTABLE:
            have.add(pet["dex"])
    if len(have) != before:
        store.set_meta(f"dex:{owner}", sorted(have))
    return have


# ---------------------------------------------------------------- Zähler

STATS = ("wins", "pvp_wins", "trips", "jogress", "ghosts")


def stats(store, owner):
    value = store.get_meta(f"stats:{owner}", None)
    if value is None:
        # erstes Mal: Siege aus den vorhandenen Digimon übernehmen (die gab es schon vorher)
        value = {k: 0 for k in STATS}
        value["wins"] = sum(p.get("wins", 0) for p in store.all_pets(owner))
        store.set_meta(f"stats:{owner}", value)
    return {k: value.get(k, 0) for k in STATS}


def count(store, owner, key, n=1):
    value = stats(store, owner)
    value[key] = value.get(key, 0) + n
    store.set_meta(f"stats:{owner}", value)


# ---------------------------------------------------------------- Erfolge
# (id, Name, Beschreibung, Bits, Fortschritt(ctx) -> (hat, braucht))

def _stage(stage):
    return lambda c: (min(1, sum(data.DIGIMON[d]["stage"] == stage for d in c["owned"])), 1)


def _dex(n):
    return lambda c: (min(n, len(c["owned"])), n)


def _stat(key, n):
    return lambda c: (min(n, c["stats"][key]), n)


ACHIEVEMENTS = [
    ("hatch", T("Hallo, Welt!"), T("Lass ein Digi-Ei schlüpfen."), 20, _stage("Fresh")),
    ("rookie", T("Großgeworden"), T("Zieh ein Digimon bis zum Rookie groß."), 30, _stage("Rookie")),
    ("champion", T("Champion!"), T("Erreiche die Champion-Stufe."), 50, _stage("Champion")),
    ("ultimate", T("Ultra-Kraft"), T("Erreiche die Ultra-Stufe."), 100, _stage("Ultimate")),
    ("mega", T("Mega-Digitation"), T("Erreiche die Mega-Stufe."), 250, _stage("Mega")),
    ("armor", T("Armor-Held"), T("Digitiere mit einem Armor-Ei."), 100, _stage("Armor")),
    ("armor_all", T("Alle Wappen"), T("Sammle alle Armor-Formen."), 500,
     lambda c: (len(c["owned"] & ARMOR_FORMS), len(ARMOR_FORMS))),
    ("dex10", T("Sammler"), T("Sammle 10 verschiedene Digimon."), 30, _dex(10)),
    ("dex25", T("Eifriger Sammler"), T("Sammle 25 verschiedene Digimon."), 60, _dex(25)),
    ("dex50", T("Digidex-Forscher"), T("Sammle 50 verschiedene Digimon."), 120, _dex(50)),
    ("dex100", T("Digidex-Profi"), T("Sammle 100 verschiedene Digimon."), 250, _dex(100)),
    ("dex250", T("Digidex-Legende"), T("Sammle 250 verschiedene Digimon."), 600, _dex(250)),
    ("wins10", T("Kämpfer"), T("Gewinne 10 Kämpfe."), 30, _stat("wins", 10)),
    ("wins50", T("Veteran"), T("Gewinne 50 Kämpfe."), 100, _stat("wins", 50)),
    ("wins200", T("Champion der Digital World"), T("Gewinne 200 Kämpfe."), 300, _stat("wins", 200)),
    ("pvp1", T("Freundschaftskampf"), T("Gewinne einen Kampf gegen einen Freund."), 50, _stat("pvp_wins", 1)),
    ("pvp10", T("Rivale"), T("Gewinne 10 Kämpfe gegen Freunde."), 200, _stat("pvp_wins", 10)),
    ("trips10", T("Entdecker"), T("Komm 10-mal vom Erkunden zurück."), 40, _stat("trips", 10)),
    ("trips50", T("Weltenbummler"), T("Komm 50-mal vom Erkunden zurück."), 150, _stat("trips", 50)),
    ("jogress", T("Zwei werden eins"), T("Schaffe eine Jogress."), 100, _stat("jogress", 1)),
    ("ghosts5", T("Geisterjäger"), T("Besiege 5 Geister während Halloween."), 150, _stat("ghosts", 5)),
    ("pumpkin", T("Kürbiskopf"), T("Zieh ein Pumpkinmon groß."), 200,
     lambda c: (int(PUMPKINMON in c["owned"]), 1)),
]


def _context(store, owner, pets=None):
    return {"owned": sync(store, owner, pets), "stats": stats(store, owner)}


def check(store, owner, pets=None):
    """Neu geschaffte Erfolge eintragen und belohnen. Liefert [{"name", "reward"}]."""
    ctx = _context(store, owner, pets)
    done = set(store.get_meta(f"ach:{owner}", []) or [])
    new = []
    for key, name, _desc, reward, progress in ACHIEVEMENTS:
        if key in done:
            continue
        have, need = progress(ctx)
        if have >= need:
            done.add(key)
            shop.add(store, owner, reward)
            new.append({"key": key, "name": name, "reward": reward})
    if new:
        store.set_meta(f"ach:{owner}", sorted(done))
    return new


def view(store, owner):
    """Sammlung + alle Erfolge mit Fortschritt (für Browser)."""
    ctx = _context(store, owner)
    done = set(store.get_meta(f"ach:{owner}", []) or [])
    out = []
    for key, name, desc, reward, progress in ACHIEVEMENTS:
        have, need = progress(ctx)
        out.append({"key": key, "name": name, "desc": desc, "reward": reward,
                    "done": key in done, "have": have, "need": need})
    return {"owned": sorted(ctx["owned"]), "total": len(COLLECTABLE), "achievements": out}
