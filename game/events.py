"""Zeitlich begrenzte Events (z. B. Halloween).

Ein Event läuft jedes Jahr im selben Zeitraum (Datum in der Spiel-Zeitzone). Solange es
läuft, gibt es ein Banner im Spiel und kleine Extras:
  ghosts  – wilde Gegner sind oft „Geister“ (Digimon dieser Liste, gleiche Stufe):
            Sieg = doppelte Bits und eine Chance auf das Event-Item
  eggs    – beim Erkunden eine Extra-Chance auf ein Ei dieser Linien
  item    – Event-Item: beim Erkunden / nach Geister-Siegen und im Shop (nur während des Events)
Zum Testen kann der Admin ein Event per Cheat erzwingen (meta "event_force").

Neues Event = neuer Eintrag in EVENTS (+ englische Texte in game/i18n_en.py). Jedes Event hat
eine kleine Story (`story`, Absätze) und ein Symbol (`icon`, aus game.js ICONS) für den Event-Tab;
die Belohnungen im Tab rechnet details() aus den Zahlen unten aus.
"""
import random

from . import data
from . import pet as P
from .i18n import T

EVENTS = {
    "halloween": {
        "name": T("Halloween"),
        "text": T("Geister spuken durch die Digital World! Jedes zweite wilde Digimon ist ein Geist – "
                  "besiegst du ihn, gibt es doppelte Bits und manchmal ein Gruselbonbon. Beim Erkunden "
                  "findest du öfter Grusel-Eier."),
        "story": [
            T("Jedes Jahr Ende Oktober wird es in der Digital World merkwürdig still. Nebel kriecht aus der "
              "Dunklen Zone herauf, und überall leuchten Kürbislaternen – an Orten, an denen nie jemand welche "
              "aufgestellt hat."),
            T("Dann feiern die Geister-Digimon ihr Fest: Bakemon schweben durch den Urwald, Wizardmon lässt "
              "Irrlichter tanzen, und irgendwo im Nebel kichert ein Pumpkinmon. Wer sich ihnen stellt, wird "
              "belohnt – Geister lassen doppelt so viele Bits fallen und manchmal ein Gruselbonbon."),
            T("Und ganz selten findet ein Tamer ein Ei, das leise flackert wie eine Kerze. Was daraus schlüpft, "
              "ist kein Geheimnis: Es wird immer ein Pumpkinmon. Aber beeil dich – am 2. November verzieht sich "
              "der Nebel, und mit ihm verschwinden die Geister bis zum nächsten Jahr."),
        ],
        "icon": "pumpkin",
        "start": (10, 25), "end": (11, 2),          # (Monat, Tag), beide Tage gehören dazu
        "ghosts": ["Candlemon", "DemiDevimon", "Impmon", "Tsukaimon", "Dracmon",
                   "Bakemon", "Soulmon", "Wizardmon", "Devimon", "Sangloupmon",
                   "Phantomon", "Pumpkinmon", "Myotismon", "LadyDevimon", "SkullSatamon", "Mummymon", "SkullGreymon",
                   "NeoMyotismon", "Piedmon", "Daemon", "Beelzemon"],
        "eggs": ["ver3", "impmon", "cocomon", "cotsucomon", "kuramon", "dokimon"],
        "item": "candy",
    },
}

GHOST_CHANCE = 0.5            # so oft ist ein wilder Gegner ein Geist
GHOST_ITEM_CHANCE = 0.3       # Event-Item nach einem Geister-Sieg
GHOST_EGG_CHANCE = 0.08       # Event-Ei (z. B. Halloween-Ei mit Pumpkinmon) nach einem Geister-Sieg
TRIP_EGG_CHANCE = 0.2         # pro Expedition: Extra-Ei …
TRIP_EVENT_EGG_SHARE = 0.5    # … davon so oft das Event-Ei, sonst ein Ei aus den Grusel-Linien
TRIP_ITEM_CHANCE = 0.5        # pro Expedition: Event-Item


def event_egg(key):
    """Das Event-Ei (eigene Linie mit fester Reihe, z. B. Pumpkinmon) – oder None."""
    return next((line for line, ev in data.EVENT_LINES.items() if ev == key), None)


def _in_range(month_day, start, end):
    if start <= end:
        return start <= month_day <= end
    return month_day >= start or month_day <= end      # über den Jahreswechsel


def current(minute, forced=None):
    """Key des laufenden Events (oder None). `forced` = per Cheat erzwungenes Event."""
    if forced in EVENTS:
        return forced
    t = P.local_time(minute)
    for key, ev in EVENTS.items():
        if _in_range((t.month, t.day), ev["start"], ev["end"]):
            return key
    return None


def _date(month_day):
    return "%02d.%02d." % (month_day[1], month_day[0])


def view(key):
    """Kurzform fürs Banner (steckt in jedem Spielstand)."""
    if not key:
        return None
    ev = EVENTS[key]
    return {"key": key, "name": ev["name"], "text": ev["text"], "icon": ev.get("icon", "star"),
            "from": _date(ev["start"]), "until": _date(ev["end"])}


def _days_left(ev, minute):
    """Wie viele Tage das Event noch läuft (heute mitgezählt)."""
    today = P.local_time(minute).date()
    end = today.replace(month=ev["end"][0], day=ev["end"][1])
    if end < today:                                  # Ende liegt im nächsten Jahr
        end = end.replace(year=today.year + 1)
    return (end - today).days + 1


def _chain(line):
    """Die feste Reihe eines Event-Eis als Digimon-Nummern (z. B. Yuramon … NoblePumpkinmon)."""
    out, dex = [], None
    while True:
        evos = data.evolutions_from(line, dex)
        if not evos or evos[0]["to"] in out:
            return out
        dex = evos[0]["to"]
        out.append(dex)


def _pct(x):
    return round(x * 100)


def details(key, minute):
    """Alles für den Event-Tab: Story, Belohnungen, Geister, Event-Ei (ohne Shop-Angebote)."""
    if not key:
        return None
    ev = EVENTS[key]
    egg = event_egg(key)
    item = ev.get("item")
    from . import explore
    item_name = explore.ITEMS[item]["name"] if item else None
    rewards = [T("Geister besiegen: doppelte Bits")]
    if item:
        rewards.append(T("Geister besiegen: {p} % Chance auf ein {item}", p=_pct(GHOST_ITEM_CHANCE), item=item_name))
    if egg:
        rewards.append(T("Geister besiegen: {p} % Chance auf das {egg}", p=_pct(GHOST_EGG_CHANCE), egg=data.line_name(egg)))
    if item:
        rewards.append(T("Erkunden: {p} % Chance pro Ausflug auf ein {item}", p=_pct(TRIP_ITEM_CHANCE), item=item_name))
    rewards.append(T("Erkunden: {p} % Chance pro Ausflug auf ein Extra-Ei – die Hälfte davon ist das {egg}",
                     p=_pct(TRIP_EGG_CHANCE), egg=data.line_name(egg)) if egg else
                   T("Erkunden: {p} % Chance pro Ausflug auf ein Extra-Ei", p=_pct(TRIP_EGG_CHANCE)))
    names = _by_name()
    return {**view(key), "story": ev.get("story", []), "rewards": rewards,
            "ghost_chance": _pct(GHOST_CHANCE), "days_left": _days_left(ev, minute),
            "ghosts": [names[n] for n in ev["ghosts"] if n in names],
            "egg": {"line": egg, "name": data.line_name(egg), "chain": _chain(egg)} if egg else None,
            "item": item, "item_name": item_name}


def _by_name():
    out = {}
    for dex, d in data.PLAYABLE.items():
        out.setdefault(d["name"], dex)
    return out


def ghosts(key, stage):
    """Geister-Digimon dieses Events für eine Stufe (Nummern)."""
    if not key:
        return []
    names = _by_name()
    return [names[n] for n in EVENTS[key]["ghosts"] if n in names and data.PLAYABLE[names[n]]["stage"] == stage]


def trip_bonus(key, rng=random):
    """Extra-Funde einer Expedition während eines Events -> {"eggs": [...], "items": [...]}."""
    found = {"eggs": [], "items": []}
    if not key:
        return found
    ev = EVENTS[key]
    lines = [line for line in ev["eggs"] if line in data.LINES]
    special = event_egg(key)
    if rng.random() < TRIP_EGG_CHANCE:
        if special and (not lines or rng.random() < TRIP_EVENT_EGG_SHARE):
            found["eggs"].append(special)
        elif lines:
            found["eggs"].append(rng.choice(lines))
    if ev.get("item") and rng.random() < TRIP_ITEM_CHANCE:
        found["items"].append(ev["item"])
    return found
