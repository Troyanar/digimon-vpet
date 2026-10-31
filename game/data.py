"""Lädt data/digimon.json (Digimon, Sprites, Entwicklungslinien)."""
import json
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "digimon.json"

DATA = json.loads(_PATH.read_text(encoding="utf8"))
DIGIMON = {int(k): v for k, v in DATA["digimon"].items()}
LINES = DATA["lines"]
EVOLUTIONS = DATA["evolutions"]
# Nur Digimon, die in einem Ei vorkommen (DIGIMON enthält zusätzlich die Sprites
# ehemaliger Digimon, damit alte Spielstände noch angezeigt werden können)
PLAYABLE = {dex: DIGIMON[dex] for dex in sorted({e["to"] for e in EVOLUTIONS})}
# alte Digimon-Nummer -> neue (gleichnamige Sprites wurden zu einem Digimon zusammengelegt)
ALIASES = {int(k): v for k, v in DATA.get("aliases", {}).items()}
# altes Ei -> behaltenes Ei (Eier mit demselben Baby wurden zusammengelegt)
LINE_ALIASES = DATA.get("line_aliases", {})
# Armor-Eier (Rucksack-Items für die Armor-Digitation): Key -> {"name", "desc", "armor"}
ARMOR_ITEMS = DATA.get("items", {})
# Event-Eier (z. B. Halloween) gibt es nur während ihres Events – nie als Zufalls-Ei,
# nicht beim normalen Erkunden und nicht als Kampf-Beute. Linie -> Event-Key
EVENT_LINES = {line: info["event"] for line, info in LINES.items() if info.get("event")}
# alle "normalen" Eier – daraus wird gezogen, wenn ein zufälliges Ei gebraucht wird
NORMAL_LINES = [line for line in LINES if line not in EVENT_LINES]
# Digimon, die es nur in Event-Eiern gibt (z. B. Pumpkinmon) – keine normalen wilden Gegner
EVENT_ONLY = {e["to"] for e in EVOLUTIONS if e["line"] in EVENT_LINES} \
    - {e["to"] for e in EVOLUTIONS if e["line"] not in EVENT_LINES}
# wilde Gegner außerhalb von Events
WILD = {dex: d for dex, d in PLAYABLE.items() if dex not in EVENT_ONLY}


def line_name(line):
    """Name einer Ei-Linie zum Anzeigen (zweisprachig): "Digi-Ei Version 1" / "Digi-Egg Version 1"."""
    from .i18n import T
    name = LINES[line]["name"]
    if name.startswith("Digi-Ei "):
        return T("Digi-Ei {name}", name=name[len("Digi-Ei "):])
    return T(name)


def egg_name(line):
    """Wie ein Ei für Spieler heißt: Event-Eier (z. B. „Digi-Ei Halloween“) mit Sorte, alle
    anderen nur „Digi-Ei“ – was daraus schlüpft, bleibt eine Überraschung."""
    from .i18n import T
    return line_name(line) if line in EVENT_LINES else T("Digi-Ei")


_DEX_PATH =Path(__file__).resolve().parent.parent / "static" / "digidex.json"
_SKILLS = {}           # Dex-Nummer -> Attacken laut Digidex (einmal gelesen)


def special_name(dex):
    """Name der Spezialattacke = erste Attacke im Digidex (static/digidex.json) – oder None."""
    if "dex" not in _SKILLS:
        try:
            entries = json.loads(_DEX_PATH.read_text(encoding="utf8"))
        except (OSError, ValueError):
            entries = {}
        _SKILLS["dex"] = {int(k): v.get("skills") or [] for k, v in entries.items()
                          if str(k).isdigit() and isinstance(v, dict)}
    skills = _SKILLS["dex"].get(dex)
    return skills[0] if skills and isinstance(skills[0], str) else None


_INDEX = {"of": None}


def _index():
    """(Linie, Digimon) -> Wege und Digimon -> Wege (irgendeine Linie); neu, wenn sich EVOLUTIONS ändert."""
    if _INDEX["of"] is not EVOLUTIONS:
        by_line, by_dex = {}, {}
        for e in EVOLUTIONS:
            by_line.setdefault((e["line"], e["from"]), []).append(e)
        for (line, dex), edges in by_line.items():
            by_dex.setdefault(dex, edges)
        _INDEX.update({"of": EVOLUTIONS, "line": by_line, "dex": by_dex})
    return _INDEX


def evolutions_from(line, dex):
    """Mögliche nächste Formen, in Prüfreihenfolge (die erste passende gewinnt).
    Jedes Digimon entwickelt sich in jedem Ei gleich – kommt es in seiner Linie nicht
    (mehr) vor (alter Spielstand), gelten seine Wege aus einer anderen Linie."""
    idx = _index()
    found = idx["line"].get((line, dex))
    if found is None and dex is not None:
        found = idx["dex"].get(dex)
    return list(found or [])


def bedtime(line, dex):
    for e in EVOLUTIONS:
        if e["line"] == line and e["to"] == dex:
            return e["bedtime"]
    return 21 * 60
