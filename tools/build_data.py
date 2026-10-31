"""Erzeugt data/digimon.json aus den Daten des tuipet-Pakets (MIT, Joel Taylor).

Aufruf:
    python tools/build_data.py <pfad/zum/tuipet-*.whl> [linien]

Ohne Linienangabe werden alle Linien übernommen, die zu unseren Spielregeln
passen (Pflegefehler, Training, Überfüttern, Siege). Linien mit anderen Regeln
(Level, Gebiete, ...) werden übersprungen und aufgelistet.

Nur bestimmte Linien:
    python tools/build_data.py tuipet-0.6.52-py3-none-any.whl ver1,ver2,impmon
"""
import csv
import gzip
import io
import json
import os
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "digimon.json"

# Bedeutung der 11 Animationsbilder jedes Sprites (DVPet-Reihenfolge)
FRAMES = {
    "idle": [0, 1],
    "sleep": [2, 3],
    "refuse": [4],
    "happy": [5],
    "angry": [6],
    "eat": [8, 7],
    "attack": [6],
    "tired": [9],
    "sick": [10],
}

# Unsere festen Linien – die müssen sich bauen lassen
REQUIRED = {"ver1", "ver2", "ver3", "ver4", "ver5", "impmon", "gomamon", "veemon", "wormmon", "salamon"}
# Ei-Namen verraten nur das Baby, das schlüpft – nie, was daraus wird (soll eine
# Überraschung sein). Gleiche Babys unterscheidet eine Farbe.
FIXED_NAMES = {f"ver{i}": f"Digi-Ei Version {i}" for i in range(1, 6)}
EGG_COLORS = ["rot", "blau", "grün", "gelb", "lila", "weiß", "schwarz", "orange"]


def egg_names(lines, name_of):
    """Setzt lines[...]["name"]: "Digi-Ei <Baby>" bzw. "Digi-Ei <Baby> (<Farbe>)"."""
    base = {line: FIXED_NAMES.get(line) or f"Digi-Ei {name_of(info['first'])}" for line, info in lines.items()}
    total, seen = Counter(base.values()), Counter()
    for line in lines:
        name = base[line]
        if total[name] > 1:
            i = seen[name]
            seen[name] += 1
            color = EGG_COLORS[i] if i < len(EGG_COLORS) else f"Sorte {i + 1}"
            name = f"{name} ({color})"
        lines[line]["name"] = name

# Eigene Linien nach dem Vorbild des Animes, mit denselben Regeln wie V-Pet 1-5:
# (Stufe, Sprite-Nr, Eltern ("egg" oder Sprite-Nummern), Regel, Name zur Info)
# Reihenfolge zählt: Bei gleichem Elternteil gewinnt die erste passende Regel.
CUSTOM_LINES = {
    "impmon": [
        ("Fresh", 1428, "egg", "TIME", "Kiimon"),
        ("InTraining", 934, (1428,), "TIME", "Yaamon"),
        ("Rookie", 59, (934,), "CM 0-2", "Impmon"),
        ("Rookie", 32, (934,), "CM 3+", "DemiDevimon"),
        ("Champion", 99, (59,), "CM 0-2, TR 16+", "Wizarmon"),
        ("Champion", 102, (59, 32), "CM 0-2, TR 0-15", "Devimon"),
        ("Champion", 121, (59, 32), "CM 3+, TR 8+", "Bakemon"),
        ("Champion", 102, (32,), "CM 0-2, TR 16+", "Devimon"),
        ("Champion", 117, (59, 32), "CM 3+", "Sukamon"),
        ("Ultimate", 500, (99,), "WIN 12/15", "Baalmon"),
        ("Ultimate", 203, (102,), "WIN 12/15", "Myotismon"),
        ("Ultimate", 216, (121,), "WIN 12/15", "Phantomon"),
        ("Ultimate", 778, (117,), "WIN 12/15", "KingSukamon"),
        ("Mega", 310, (500,), "CM 0-2", "Beelzemon"),
        ("Mega", 274, (203,), "CM 0-2", "VenomMyotismon"),
        ("Mega", 278, (216,), "CM 0-2", "Piedmon"),
    ],
    "gomamon": [
        ("Fresh", 8, "egg", "TIME", "Pichimon"),
        ("InTraining", 20, (8,), "TIME", "Bukamon"),
        ("Rookie", 50, (20,), "CM 0-2", "Gomamon"),
        ("Rookie", 52, (20,), "CM 3+", "Syakomon"),
        ("Champion", 107, (50,), "CM 0-2, TR 16+", "Ikkakumon"),
        ("Champion", 110, (50, 52), "CM 0-2, TR 0-15", "Seadramon"),
        ("Champion", 105, (52,), "CM 0-2, TR 16+", "Octomon"),
        ("Champion", 128, (50, 52), "CM 3+, TR 8+", "Gesomon"),
        ("Champion", 117, (50, 52), "CM 3+", "Sukamon"),
        ("Ultimate", 229, (107,), "WIN 12/15", "Zudomon"),
        ("Ultimate", 202, (110,), "WIN 12/15", "MegaSeadramon"),
        ("Ultimate", 205, (105, 128), "WIN 12/15", "MarineDevimon"),
        ("Ultimate", 778, (117,), "WIN 12/15", "KingSukamon"),
        ("Mega", 301, (229,), "CM 0-2", "Vikemon"),
        ("Mega", 275, (202,), "CM 0-2", "MetalSeadramon"),
        ("Mega", 340, (205,), "CM 0-2", "Leviamon"),
    ],
    "veemon": [
        ("Fresh", 1430, "egg", "TIME", "Chibomon"),
        ("InTraining", 939, (1430,), "TIME", "DemiVeemon"),
        ("Rookie", 62, (939,), "TIME", "Veemon"),
        ("Champion", 153, (62,), "CM 0-2, TR 16+", "XVeemon"),
        ("Champion", 144, (62,), "CM 0-2, TR 0-15", "Veedramon"),
        ("Champion", 116, (62,), "CM 3+", "Numemon"),
        ("Ultimate", 248, (153,), "WIN 12/15", "Paildramon"),
        ("Ultimate", 233, (144,), "WIN 12/15", "AeroVeedramon"),
        ("Ultimate", 192, (116,), "WIN 12/15", "Monzaemon"),
        ("Mega", 304, (248,), "CM 0-2", "Imperialdramon"),
        ("Mega", 311, (233,), "CM 0-2", "UlforceVeedramon"),
    ],
    "wormmon": [
        ("Fresh", 1434, "egg", "TIME", "Leafmon"),
        ("InTraining", 949, (1434,), "TIME", "Minomon"),
        ("Rookie", 65, (949,), "TIME", "Wormmon"),
        ("Champion", 156, (65,), "CM 0-2, TR 16+", "Stingmon"),
        ("Champion", 413, (65,), "CM 0-2, TR 0-15", "Hudiemon"),
        ("Champion", 178, (65,), "CM 3+", "Gokimon"),
        ("Ultimate", 422, (156,), "WIN 12/15", "Dinobeemon"),
        ("Ultimate", 613, (413,), "WIN 12/15", "Jewelbeemon"),
        ("Ultimate", 778, (178,), "WIN 12/15", "KingSukamon"),
        ("Mega", 314, (422,), "CM 0-2", "Imperialdramon PM"),
        ("Mega", 343, (613,), "CM 0-2", "GranKuwagamon"),
    ],
    "salamon": [
        ("Fresh", 1, "egg", "TIME", "YukimiBotamon"),
        ("InTraining", 15, (1,), "TIME", "Nyaromon"),
        ("Rookie", 47, (15,), "CM 0-2", "Salamon"),
        ("Rookie", 385, (15,), "CM 3+", "Lunamon"),
        ("Champion", 126, (47,), "CM 0-2, TR 16+", "Gatomon"),
        ("Champion", 388, (385,), "CM 0-2, TR 16+", "Lekismon"),
        ("Champion", 102, (47, 385), "CM 0-2, TR 0-15", "Devimon"),
        ("Champion", 116, (47, 385), "CM 3+", "Numemon"),
        ("Ultimate", 224, (126,), "WIN 12/15", "Angewomon"),
        ("Ultimate", 391, (388,), "WIN 12/15", "Crescemon"),
        ("Ultimate", 215, (102,), "WIN 12/15", "LadyDevimon"),
        ("Ultimate", 192, (116,), "WIN 12/15", "Monzaemon"),
        ("Mega", 303, (224,), "CM 0-2", "Ophanimon"),
        ("Mega", 377, (391,), "CM 0-2", "Dianamon"),
        ("Mega", 341, (215,), "CM 0-2", "Lilithmon"),
    ],
}
BEDTIME = {"Fresh": "20:00", "InTraining": "21:00", "Rookie": "21:00",
           "Champion": "22:00", "Armor": "22:00", "Ultimate": "23:00", "Mega": "23:00"}

# Anime-Digitationen: Die Ei-Linien stammen von den V-Pet-Spielzeugen und haben oft
# nur einen festen Weg (z. B. Leomon -> Megadramon). Diese Ketten kommen in JEDES Ei,
# in dem die Startform vorkommt. Mehrere Namen = Alternativen ("A|B").
ANIME_CHAINS = [
    ["Greymon", "MetalGreymon", "WarGreymon"],
    ["Garurumon", "WereGarurumon", "MetalGarurumon"],
    ["Birdramon", "Garudamon", "Phoenixmon"],
    ["Kabuterimon", "MegaKabuterimon", "HerculesKabuterimon"],
    ["Togemon", "Lilymon", "Rosemon"],
    ["Ikkakumon", "Zudomon", "Vikemon"],
    ["Angemon", "MagnaAngemon", "Seraphimon"],
    ["Gatomon", "Angewomon", "Magnadramon"],
    ["Devimon", "Myotismon", "VenomMyotismon"],
    ["Leomon", "GrapLeomon", "BanchoLeomon"],
    ["Seadramon", "MegaSeadramon", "MetalSeadramon"],
    ["Kuwagamon", "Okuwamon", "GranKuwagamon"],
    ["Numemon", "Monzaemon", "ShinMonzaemon"],
    ["Meramon", "SkullMeramon", "Boltmon"],
    ["Monochromon", "Triceramon"],
    ["Guardromon", "Andromon", "HiAndromon"],
    ["Gekomon", "ShogunGekomon"],
    ["XVeemon", "Paildramon", "Imperialdramon"],
    ["Stingmon", "Paildramon"],
    ["Veedramon", "AeroVeedramon", "UlforceVeedramon"],
    ["Ankylomon", "Shakkoumon"],
    ["Growmon", "WarGrowmon", "Gallantmon"],
    ["Gargomon", "Rapidmon", "MegaGargomon"],
    ["Dorugamon", "DoruGreymon", "Dorugoramon"],
    ["Firamon", "Flaremon", "Apollomon"],
    ["Lekismon", "Crescemon", "Dianamon"],
    ["Coredramon", "Wingdramon", "Slayerdramon"],
    ["Groundramon", "Breakdramon"],
    ["Raremon", "Etemon"],
]
# Gibt es schon andere Wege, braucht der Anime-Weg perfekte Pflege + viel Training
# (plus die Kämpfe, die die Stufe sowieso verlangt) – so bleiben die alten Wege möglich.
ANIME_EXTRA = {"cm": [0, 0], "tr": [16, None]}
# Neue Formen ohne andere Wege: die üblichen Regeln der Stufe
STAGE_RULE = {"Ultimate": {"win": {"wins": 12, "battles": 15}}, "Mega": {"cm": [0, 2]}}
BATTLE_KEYS = ("win", "btl", "wins")
# Regeln aus tuipet, die so nie greifen können (gleiche Bedingung wie ein Geschwister davor)
RULE_FIXES = {
    ("vbu", "Garurumon", "Mammothmon"): {"cm": [3, None], "win": {"wins": 12, "battles": 15}},
}
STAGE_ORDER = ["Fresh", "InTraining", "Rookie", "Champion", "Ultimate", "Mega"]
# keine echten Digimon (Crossover, z. B. Kiryu = Mechagodzilla) – kommen nicht ins Spiel
EXCLUDE_NAMES = {"Kiryu"}
# feste Wahl für automatisch ergänzte Wege: (Vorgänger, Art) -> Digimon
# (sonst könnte eine Änderung an anderer Stelle ein Digimon ganz aus dem Spiel schieben)
PINNED_PICKS = {("KingSukamon", "neglect"): "Ogudomon"}

# Armor-Digitation wie in Adventure 02: Mit einem Armor-Ei aus dem Rucksack digitiert das
# Digimon sofort zu seiner Armor-Form (nie von allein). Die Eier findet man beim Erkunden.
# Armor-Formen haben ihre eigene Stufe "Armor" und sind Endstufen (keine weitere Digitation).
# Namen wie in der deutschen Serie; Digimon-Namen hier so, wie sie in tuipet heißen.
ARMOR_EGGS = {
    "mut": {"name": "Armor-Ei des Mutes", "uses": [("Veemon", "Flamedramon")]},
    "freundschaft": {"name": "Armor-Ei der Freundschaft", "uses": [("Veemon", "Raidramon")]},
    "liebe": {"name": "Armor-Ei der Liebe", "uses": [("Hawkmon", "Holsmon")]},
    "aufrichtigkeit": {"name": "Armor-Ei der Aufrichtigkeit", "uses": [("Hawkmon", "Shurimon")]},
    "wissen": {"name": "Armor-Ei des Wissens", "uses": [("Armadimon", "Digmon")]},
    "zuverlaessigkeit": {"name": "Armor-Ei der Zuverlässigkeit", "uses": [("Armadimon", "Submarimon")]},
    "hoffnung": {"name": "Armor-Ei der Hoffnung", "uses": [("Patamon", "Pegasmon")]},
    "licht": {"name": "Armor-Ei des Lichts", "uses": [("Salamon", "Nefertimon"), ("Gatomon", "Nefertimon")]},
    "wunder": {"name": "Goldenes Armor-Ei der Wunder", "uses": [("Veemon", "Magnamon")]},
}
ARMOR_STAGE = "Armor"
ULTRA_FIGHTS = {"win": {"wins": 12, "battles": 15}}
# Hawkmon (für Halsemon und Shurimon) wie im Anime: Pururumon -> Poromon -> Hawkmon -> Aquilamon
# -> Silphymon. (Vorgänger, Digimon, Regel) – kommt in jedes Ei, in dem der Vorgänger vorkommt,
# hinter dessen bisherige Wege.
EXTRA_PATHS = [
    ("Pururumon", "Poromon", {}),
    ("Poromon", "Hawkmon", {"cm": [0, 2]}),
    ("Poromon", "Gabumon", {}),
    ("Hawkmon", "Aquilamon", {"cm": [0, 2], "tr": [16, None]}),
    ("Hawkmon", "Birdramon", {"cm": [0, 2]}),
    ("Hawkmon", "Kokatorimon", {}),
    ("Aquilamon", "Silphymon", {"cm": [0, 2], **ULTRA_FIGHTS}),
    ("Aquilamon", "Garudamon", dict(ULTRA_FIGHTS)),
    ("Silphymon", "Valkyrimon", {"cm": [0, 2]}),
    ("Silphymon", "Ornismon", {"cm": [3, None]}),
]
# bisherige Wege, deren Regel sich dafür ändert: Pururumon wurde bisher immer zu
# TorikaraBallmon – jetzt nur noch, wenn es überfüttert wurde (sonst Poromon)
PATH_RULES = {("Pururumon", "TorikaraBallmon"): {"of": [1, None]}}
# Sprite-Wahl, wo es mehrere gibt
PREFER_SPRITE = {"Poromon": 1475}
# Namen wie in der deutschen Serie bzw. die offiziellen westlichen Namen (tuipet nutzt hier
# japanische Schreibweisen oder hat Tippfehler). Intern (CANON, ANIME_CHAINS ...) gelten weiter
# die tuipet-Namen – umbenannt wird erst bei der Ausgabe.
NAME_DE = {
    # Adventure / 02
    "Armadimon": "Armadillomon", "Holsmon": "Halsemon", "Pegasmon": "Pegasusmon", "XVeemon": "ExVeemon",
    "Wizarmon": "Wizardmon", "Wizarmon X": "Wizardmon X", "Mushmon": "Mushroomon", "Vegimon": "Vegiemon",
    "RedVegimon": "RedVegiemon", "Garbamon": "Garbagemon", "Lilymon": "Lillymon", "Lilymon X": "Lillymon X",
    "BanchoLilymon": "BanchoLillymon", "Demon": "Daemon", "Tortamon": "Tortomon",
    # Tamers
    "Growmon": "Growlmon", "Growmon X": "Growlmon X", "WarGrowmon": "WarGrowlmon", "WarGrowmon X": "WarGrowlmon X",
    # Frontier
    "Chakmon": "Chackmon", "Lucemon FM": "Lucemon Chaos Mode",
    # Data Squad
    "RizeGreymon": "RiseGreymon",
    # offizielle Namen (nicht in der deutschen Serie)
    "Craniumon": "Craniamon", "Milleniumon": "Millenniummon", "MoonMilleniumon": "Moon=Millenniummon",
    "ZeedMilleniumon": "ZeedMillenniummon", "Shawjinmon": "Shawujinmon", "Stefilmon": "Stiffilmon",
    "Kiimon": "Keemon", "Yaamon": "Yarmon", "Beastmon": "Bastemon",
    "Pumpmon": "Pumpkinmon", "NoblePumpmon": "NoblePumpkinmon",
}

# Event-Eier: gibt es nur während eines Events (game/events.py). Sie haben eine FESTE Reihe –
# jede Stufe digitiert nach Ablauf der Zeit ohne Bedingung, egal wie man sich kümmert.
# Werden NACH design_graph/merge_same_eggs angehängt, damit sie nicht umgebaut oder mit
# anderen Eiern (gleiches Baby) zusammengelegt werden. Namen hier = tuipet-Namen.
EVENT_LINES = {
    "halloween": {"name": "Digi-Ei Halloween", "event": "halloween",
                  "chain": ["Yuramon", "Tanemon", "Candlemon", "Bakemon", "Pumpmon", "NoblePumpmon"],
                  # gibt es NUR über dieses Event-Ei (alle anderen Wege dorthin fallen weg)
                  "exclusive": ["Pumpmon", "NoblePumpmon"]},
}


def add_event_lines(lines, evolutions, by_num):
    """EVENT_LINES als eigene Linien mit festen Wegen (Regel {} = keine Bedingung) anhängen.
    Exklusive Digimon verlieren vorher alle Wege in den normalen Eiern (hin und weiter)."""
    in_game = {e["to"] for e in evolutions}
    bedtimes = {}                                   # Schlafenszeit merken, bevor Wege wegfallen
    for e in evolutions:
        bedtimes.setdefault(e["to"], e["bedtime"])
    exclusive = {name for ev in EVENT_LINES.values() for name in ev.get("exclusive", [])}
    gone = [e for e in evolutions if by_num[e["to"]]["name"] in exclusive
            or (e["from"] is not None and by_num[e["from"]]["name"] in exclusive)]
    evolutions[:] = [e for e in evolutions if e not in gone]
    print("Nur im Event:", ", ".join(sorted(exclusive)), f"({len(gone)} normale Wege entfernt)")
    for line, ev in EVENT_LINES.items():
        nums = []
        for name in ev["chain"]:
            found = [n for n in in_game if by_num[n]["name"] == name]
            if len(found) != 1:
                raise ValueError(f"Event-Linie {line}: {name} nicht eindeutig im Spiel ({found})")
            nums.append(found[0])
        lines[line] = {"name": ev["name"], "first": nums[0], "event": ev["event"]}
        for frm, to in zip([None] + nums, nums):
            evolutions.append({"line": line, "from": frm, "to": to, "stage": by_num[to]["stage"],
                               "rule": {}, "bedtime": bedtimes[to], "name": by_num[to]["name"]})


def _battle_part(rule):
    """Kampf-Bedingungen einer Regel (bei ODER-Regeln die der ersten Möglichkeit ohne Fusion)."""
    if "any" in rule:
        rule = next((r for r in rule["any"] if "jogress" not in r), {})
    return {k: v for k, v in rule.items() if k in BATTLE_KEYS}


MIN_CHOICES = 2       # so viele Möglichkeiten (ohne Fusion) soll jedes Digimon mindestens haben
NEGLECT = [3, None]   # ab 3 Pflegefehlern: der "vernachlässigt"-Weg
GOOD = [0, 2]


def _without_fusion(rule):
    """Geht diese Entwicklung auch ohne Fusion? (bei ODER-Regeln reicht eine Möglichkeit)"""
    return any("jogress" not in alt for alt in rule.get("any", [rule]))


def _core(name):
    """Namenskern für Familien: "Garurumon" -> "garuru" (findet WereGarurumon)."""
    n = name.lower()
    return n[:-3] if n.endswith("mon") else n


def _pick(by_num, frm, stage, taken, kind, line_dex, in_game, used_count):
    """Sucht eine passende nächste Form: gleiche Familie/Feld/Attribut, möglichst aus der
    Linie, für den Vernachlässigt-Weg gern ein Virus-Digimon, und möglichst abwechslungsreich."""
    src = by_num[frm]
    core = _core(src["name"])
    taken_names = {by_num[t]["name"] for t in taken} | {src["name"]}
    best, best_score = None, None
    pinned = PINNED_PICKS.get((src["name"], kind))
    for num, s in by_num.items():
        if s["stage"] != stage or s["name"] in taken_names or CANON.get(s["name"], num) != num \
                or s["name"] in EXCLUDE_NAMES:
            continue
        if s["name"] == pinned:
            return num
        score = 0
        if len(core) >= 4 and core in s["name"].lower():
            score += 6 if kind != "neglect" else 3
        if s.get("field") and s.get("field") == src.get("field"):
            score += 3 if kind != "neglect" else 2
        if kind == "neglect" and s.get("attribute") == "Virus":
            score += 3
        if kind != "neglect" and s.get("attribute") == src.get("attribute"):
            score += 1
        if num in line_dex:
            score += 4
        elif num in in_game:
            score += 2
        if " " in s["name"]:
            score -= 2                       # Varianten wie "Leomon X" seltener
        score -= 2 * used_count.get(num, 0)  # nicht überall dasselbe Digimon
        key = (score, -num)
        if best_score is None or key > best_score:
            best, best_score = num, key
    return best




CANON = {}   # Name -> die eine Sprite-Nummer, die im Spiel für diesen Namen steht


def merge_same_names(lines, evolutions, by_num):
    """Gleichnamige Sprites (z. B. zwei Agumon in verschiedenen Zeichenstilen) werden zu
    EINEM Digimon. Liefert {alte Nummer: neue Nummer} für schon laufende Spielstände."""
    count, ours = {}, set()
    for e in evolutions:
        for dex in (e["from"], e["to"]):
            if dex is not None:
                count[dex] = count.get(dex, 0) + 1
                if e["line"] in REQUIRED:
                    ours.add(dex)
    # Nummern aus unseren eigenen Eiern gewinnen (bleiben stabil), sonst die häufigste
    for dex in sorted(count, key=lambda d: (d not in ours, -count[d], d)):
        CANON.setdefault(by_num[dex]["name"], dex)
    alias = {dex: CANON[by_num[dex]["name"]] for dex in count if CANON[by_num[dex]["name"]] != dex}
    def fix_partner(rule):            # Jogress-Partner auch umstellen
        if "any" in rule:
            return {**rule, "any": [fix_partner(r) for r in rule["any"]]}
        if isinstance(rule.get("jogress"), int):
            partner = rule["jogress"]
            name = by_num[partner]["name"] if partner in by_num else None
            return {**rule, "jogress": alias.get(partner, CANON.get(name, partner))}
        return rule

    seen, merged = set(), []
    for e in evolutions:
        e = {**e, "from": alias.get(e["from"], e["from"]), "to": alias.get(e["to"], e["to"]),
             "rule": fix_partner(e["rule"])}
        key = (e["line"], e["from"], e["to"])
        if key not in seen:                                         # doppelte Wege weglassen
            seen.add(key)
            merged.append(e)
    evolutions[:] = merged
    for info in lines.values():
        info["first"] = alias.get(info["first"], info["first"])
    return alias


MAX_CHOICES = 3
GOOD_TRAINED = {"cm": GOOD, "tr": [16, None]}
# Bedingungen je Anzahl der Möglichkeiten (die erste passende gewinnt, die letzte fängt alles)
SLOTS = {
    2: [{"cm": GOOD}, {"cm": NEGLECT}],
    3: [GOOD_TRAINED, {"cm": GOOD}, {"cm": NEGLECT}],
    4: [GOOD_TRAINED, {"cm": GOOD, "of": [3, None]}, {"cm": GOOD}, {"cm": NEGLECT}],
    5: [GOOD_TRAINED, {"cm": GOOD, "of": [3, None]}, {"cm": GOOD}, {"cm": NEGLECT, "tr": [16, None]}, {"cm": NEGLECT}],
    6: [GOOD_TRAINED, {"cm": GOOD, "of": [3, None]}, {"cm": GOOD}, {"cm": NEGLECT, "tr": [16, None]},
        {"cm": NEGLECT, "of": [3, None]}, {"cm": NEGLECT}],
}
FRESH_SLOTS = [{"tr": [3, None]}, {"of": [1, None]}]      # Baby I: Extra-Wege, dann der normale
# Zusätzliche Wege neben den Original-Wegen: eigene Sonder-Bedingungen (vor die Originale
# gestellt), damit die bekannten Wege genau so bleiben wie bisher
EXTRA_SLOTS = [{"cm": [0, 0], "of": [3, None]}, {"cm": [1, 2], "of": [3, None]}]


def _allows_neglect(rule):
    """Greift diese Regel auch bei beliebig vielen Pflegefehlern?"""
    return any("jogress" not in alt and (alt.get("cm") is None or alt["cm"][1] is None)
               for alt in rule.get("any", [rule]))


def _quality(rule):
    """Wie "gut" war der ursprüngliche Weg? (wenig Pflegefehler, viel Training = besser)"""
    alt = next((r for r in rule.get("any", [rule]) if "jogress" not in r), {})
    return (alt.get("cm", [0])[0], -alt.get("tr", [0])[0])


def design_graph(lines, evolutions, by_num):
    """Plant den Entwicklungsbaum EINMAL für das ganze Spiel:
    - jedes Digimon entwickelt sich in jedem Ei gleich (das Ei bestimmt nur das Baby),
    - jedes Digimon behält alle Wege aus seinem Heimat-Ei (unsere eigenen Linien zuerst,
      sonst das Ei mit den meisten Wegen) – samt Original-Regeln,
    - jedes Digimon (außer Mega) hat mindestens 2 Möglichkeiten ohne Fusion,
    - kein Digimon geht verloren: wer sonst keinen Vorgänger hätte, wird dort angehängt,
      wo am wenigsten Wege sind. Wo sich die Wege dadurch ändern, werden die Bedingungen
      einheitlich (gut gepflegt + trainiert / gut gepflegt / vernachlässigt).
    Liefert die Liste der Digimon, die keinen Platz mehr bekommen haben."""
    popular = Counter((e["from"], e["to"]) for e in evolutions if e["from"] is not None)
    cand, jog = {}, {}
    for e in sorted(evolutions, key=lambda e: e["line"] not in REQUIRED):   # unsere Regeln zuerst
        if e["from"] is None:
            continue
        target = cand if _without_fusion(e["rule"]) else jog
        target.setdefault(e["from"], {}).setdefault(e["to"], e)
    # Heimat-Wege jedes Digimon (in Original-Reihenfolge, mit Original-Regeln)
    per_line = {}
    for e in evolutions:
        if e["from"] is not None and _without_fusion(e["rule"]):
            per_line.setdefault((e["line"], e["from"]), []).append(e)
    home = {}
    for (line, frm), edges in per_line.items():
        score = (line in REQUIRED, len({x["to"] for x in edges}))
        if frm not in home or score > home[frm][0]:
            home[frm] = (score, edges)
    home = {frm: edges for frm, (_, edges) in home.items()}

    def pref(p, t):
        e = cand[p][t]
        return (e["line"] in REQUIRED, e.get("src") == "anime", popular[(p, t)], -t)

    roots = sorted({info["first"] for info in lines.values()})
    reach, sel, dropped = set(roots), {}, []
    used_count, all_known = {}, set(cand) | {t for ts in cand.values() for t in ts}
    for stage in STAGE_ORDER[:-1]:
        parents = sorted(d for d in reach if by_num[d]["stage"] == stage)
        options = {p: sorted(cand.get(p, {}), key=lambda t: pref(p, t), reverse=True) for p in parents}
        parent_of = {}
        for p, ts in options.items():
            sel.setdefault(p, [])
            for t in ts:
                parent_of.setdefault(t, []).append(p)
        add = lambda p, t: sel[p].append(t) if t not in sel[p] else None
        covered = lambda t: any(t in sel[p] for p in parent_of.get(t, []))
        # 1. Digimon mit nur einem möglichen Vorgänger: der muss es nehmen
        for t, ps in parent_of.items():
            if len(ps) == 1:
                add(ps[0], t)
        # 2. jeder Vorgänger behält seine Heimat-Wege (z. B. Agumon alle fünf)
        for p in parents:
            for e in home.get(p, []):
                add(p, e["to"])
        # 3. Digimon ohne Vorgänger: zu dem echten Vorgänger (der sich schon in einem Ei zu
        #    ihm entwickelt hat), zu dem es am besten passt – unsere Linien, Anime-Weg, in
        #    den meisten Eiern; bei Gleichstand der mit weniger Wegen
        for t in sorted(parent_of, key=lambda t: (len(parent_of[t]), t)):
            if covered(t):
                continue
            free = [p for p in parent_of[t] if len(sel[p]) < len(SLOTS) + 1]
            if free:
                add(max(free, key=lambda p: (pref(p, t)[:3], -len(sel[p]), -p)), t)
            else:
                dropped.append(t)
        # 4. wer dann noch zu wenig hat, bekommt ein passendes Digimon dazu
        nxt = STAGE_ORDER[STAGE_ORDER.index(stage) + 1]
        for p in parents:
            while len(sel[p]) < MIN_CHOICES:
                kind = "train" if stage == "Fresh" else "neglect" if sel[p] else "good"
                t = _pick(by_num, p, nxt, set(sel[p]), kind, reach, all_known, used_count)
                if t is None:
                    break
                used_count[t] = used_count.get(t, 0) + 1
                cand.setdefault(p, {})[t] = {"line": "", "from": p, "to": t, "stage": nxt,
                                             "rule": {"cm": NEGLECT} if kind == "neglect" else {}, "src": "pick"}
                sel[p].append(t)
        # 5. passt bei 3+ Pflegefehlern gar kein Weg (z. B. viele Ultras), gibt es einen
        #    eigenen "vernachlässigt"-Weg – sonst bliebe das Digimon für immer stehen
        if stage != "Fresh":
            for p in parents:
                # die Regeln, die am Ende wirklich gelten: Heimat-Wege mit ihren Original-Regeln
                used_rules = [e["rule"] for e in home.get(p, [])]
                used_rules += [cand[p][t]["rule"] for t in sel[p] if t not in {e["to"] for e in home.get(p, [])}]
                if not sel[p] or any(_allows_neglect(r) for r in used_rules):
                    continue
                t = _pick(by_num, p, nxt, set(sel[p]), "neglect", reach, all_known, used_count)
                if t is None:
                    continue
                used_count[t] = used_count.get(t, 0) + 1
                cand[p][t] = {"line": "", "from": p, "to": t, "stage": nxt, "rule": {"cm": NEGLECT}, "src": "neglect"}
                sel[p].append(t)
        for p in parents:
            reach.update(sel[p])
            reach.update(jog.get(p, {}))
    # Fusionen ab Mega (Mega + Mega -> Mega) auch erreichbar machen
    todo = [p for p in reach if by_num[p]["stage"] == "Mega"]
    while todo:
        for t in jog.get(todo.pop(), {}):
            if t not in reach:
                reach.add(t)
                todo.append(t)
    dropped = [t for t in dropped if t not in reach]

    # Bedingungen vergeben
    final = {}
    for p in reach:
        kids = sel.get(p, [])
        if not kids:
            # z. B. Mega: nur Fusionen (WarGreymon + MetalGarurumon -> Omnimon)
            if jog.get(p):
                final[p] = [{k: v for k, v in e.items() if k not in ("line", "src")} for e in jog[p].values()]
            continue
        stage = by_num[p]["stage"]
        homeset = [e["to"] for e in home.get(p, [])]
        edges = []
        extras = [t for t in kids if t not in homeset]
        originals = [{k: v for k, v in e.items() if k not in ("line", "src")} for e in home.get(p, [])]
        battle = _battle_part(home[p][0]["rule"]) if home.get(p) else {}
        if stage == "Champion":
            battle = battle or {"win": {"wins": 12, "battles": 15}}
        if not extras:
            # unverändert: Original-Wege mit Original-Regeln und -Reihenfolge
            edges = originals
        elif stage != "Fresh" and homeset and \
                len([t for t in extras if cand[p][t].get("src") != "neglect"]) <= len(EXTRA_SLOTS):
            # Original-Wege bleiben genau so; Extras davor mit eigener Bedingung,
            # der "vernachlässigt"-Weg (falls nötig) dahinter
            neglect = [t for t in extras if cand[p][t].get("src") == "neglect"]
            niche = [t for t in extras if t not in neglect]
            slots = [{"cm": NEGLECT}] if len(set(homeset)) == 1 and len(niche) == 1 and not neglect \
                else EXTRA_SLOTS

            def edge(t, rule):
                h, m = (int(x) for x in BEDTIME[by_num[t]["stage"]].split(":"))
                return {"from": p, "to": t, "stage": by_num[t]["stage"], "rule": {**battle, **rule},
                        "bedtime": cand[p][t].get("bedtime", h * 60 + m), "name": by_num[t]["name"]}
            edges = [edge(t, rule) for t, rule in zip(niche, slots)] + originals
            edges += [edge(t, {"cm": NEGLECT}) for t in neglect]
        else:
            if stage == "Fresh":
                default = max(kids, key=lambda t: pref(p, t))
                extras = [t for t in kids if t != default]
                rules = list(zip(extras, FRESH_SLOTS)) + [(default, {})]
            else:
                order = sorted(kids, key=lambda t: (_quality(cand[p][t]["rule"]), -pref(p, t)[2], t))
                rules = list(zip(order, SLOTS[min(len(order), len(SLOTS) + 1)]))
            for t, rule in rules:
                old = cand[p][t]
                rule = dict(rule)
                if stage == "Champion" or STAGE_ORDER.index(by_num[t]["stage"]) > STAGE_ORDER.index(stage) + 1:
                    rule["win"] = {"wins": 12, "battles": 15}      # Ultra (und Stufensprünge): Kämpfe
                fusion = [a for a in old["rule"].get("any", []) if "jogress" in a]
                if fusion:
                    rule = {"any": [rule] + fusion}                   # "… ODER Fusion" bleibt erhalten
                h, m = (int(x) for x in BEDTIME[by_num[t]["stage"]].split(":"))
                edges.append({"from": p, "to": t, "stage": by_num[t]["stage"], "rule": rule,
                              "bedtime": old.get("bedtime", h * 60 + m), "name": by_num[t]["name"]})
        edges += [{k: v for k, v in e.items() if k not in ("line", "src")} for e in jog.get(p, {}).values()]
        final[p] = edges

    # jede Linie: ihr Ei + alles, was davon aus erreichbar ist
    result = []
    for line, info in lines.items():
        egg = next(e for e in evolutions if e["line"] == line and e["from"] is None)
        result.append({k: v for k, v in egg.items() if k != "src"})
        seen, todo = set(), [info["first"]]
        while todo:
            node = todo.pop(0)
            if node in seen:
                continue
            seen.add(node)
            for e in final.get(node, []):
                result.append({"line": line, **e})
                todo.append(e["to"])
    evolutions[:] = result
    return sorted(set(dropped))


def merge_same_eggs(lines, evolutions):
    """Nach unify() sind Eier mit demselben Baby völlig gleich -> nur eins behalten
    (unsere eigenen Linien haben Vorrang). Liefert {altes Ei: behaltenes Ei}."""
    keep, alias = {}, {}
    order = sorted(lines, key=lambda l: (l not in REQUIRED, list(lines).index(l)))
    for line in order:
        first = lines[line]["first"]
        if first in keep:
            alias[line] = keep[first]
        else:
            keep[first] = line
    for line in alias:
        del lines[line]
    evolutions[:] = [e for e in evolutions if e["line"] not in alias]
    return alias




def add_armor_paths(lines, evolutions, by_num):
    """Hängt nach design_graph() Armor-Digitationen und EXTRA_PATHS ein. Jedes Digimon
    entwickelt sich danach weiter in jedem Ei gleich: die Wege werden pro Digimon geplant
    und jede Linie neu vom Ei aus aufgebaut. Liefert ({Item-Key: {"name", "desc"}},
    {Nummern der Armor-Formen})."""
    def num(name):
        if name in PREFER_SPRITE:
            return PREFER_SPRITE[name]
        if name in CANON:
            return CANON[name]
        nums = sorted(n for n, s in by_num.items() if s["name"] == name)
        if not nums:
            raise ValueError(f"kein Sprite für {name}")
        return nums[0]

    def edge(a, b, rule, stage=None):
        stage = stage or by_num[b]["stage"]
        h, m = (int(x) for x in BEDTIME[stage].split(":"))
        return {"from": a, "to": b, "stage": stage, "rule": rule, "bedtime": h * 60 + m, "name": by_num[b]["name"]}

    # Wege je Digimon (in jedem Ei gleich -> aus der ersten Linie, in der es vorkommt)
    home_line, out_of = {}, {}
    for e in evolutions:
        if e["from"] is not None and home_line.setdefault(e["from"], e["line"]) == e["line"]:
            out_of.setdefault(e["from"], []).append({k: v for k, v in e.items() if k != "line"})

    for (a, b), rule in PATH_RULES.items():
        hit = [e for e in out_of.get(num(a), []) if e["to"] == num(b)]
        if not hit:
            raise ValueError(f"Weg {a} -> {b} fehlt")
        hit[0]["rule"] = rule
    for a, b, rule in EXTRA_PATHS:
        out_of.setdefault(num(a), []).append(edge(num(a), num(b), rule))
    items, forms = {}, set()
    for key, egg in ARMOR_EGGS.items():
        for a, b in egg["uses"]:
            out_of.setdefault(num(a), []).append(edge(num(a), num(b), {"item": key}, ARMOR_STAGE))
            forms.add(num(b))
        users = " oder ".join(dict.fromkeys(NAME_DE.get(a, a) for a, _ in egg["uses"]))
        items[key] = {"name": egg["name"], "desc": f"Armor-Digitation für {users}", "armor": True}
    for dex in forms:
        if out_of.pop(dex, None):                      # Armor-Formen sind Endstufen
            print("Armor-Form hatte Wege (entfernt):", by_num[dex]["name"])
    # jede Linie neu: Ei + alles, was davon aus erreichbar ist
    result = []
    for line, info in lines.items():
        egg = next(e for e in evolutions if e["line"] == line and e["from"] is None)
        result.append(egg)
        seen, todo = set(), [info["first"]]
        while todo:
            node = todo.pop(0)
            if node in seen:
                continue
            seen.add(node)
            for e in out_of.get(node, []):
                result.append({"line": line, **e})
                todo.append(e["to"])
    evolutions[:] = result
    return items, forms


def add_anime_paths(lines, evolutions, by_num):
    """Hängt die ANIME_CHAINS in alle passenden Linien ein. Liefert die Anzahl neuer Wege."""
    by_name = {}
    for num, s in sorted(by_num.items()):
        by_name.setdefault(s["name"].lower(), []).append(num)
    in_game = {e["to"] for e in evolutions}

    def resolve(alts):
        for alt in alts.split("|"):
            nums = by_name.get(alt.lower(), [])
            if nums:
                return min(nums, key=lambda n: (n not in in_game, n))     # schon im Spiel bevorzugt
        return None

    added = 0
    for chain in ANIME_CHAINS:
        nums = [resolve(n) for n in chain]
        if None in nums:
            print("Anime-Kette übersprungen (Sprite fehlt):", chain)
            continue
        for line in lines:
            for a, b in zip(nums, nums[1:]):
                present = {e["to"] for e in evolutions if e["line"] == line}
                stage = by_num[b]["stage"]
                if a not in present or STAGE_ORDER.index(stage) != STAGE_ORDER.index(by_num[a]["stage"]) + 1:
                    continue
                options = [i for i, e in enumerate(evolutions) if e["line"] == line and e["from"] == a]
                if any(evolutions[i]["to"] == b for i in options):
                    continue
                plain = [i for i in options if "jogress" not in json.dumps(evolutions[i]["rule"])]
                if plain:
                    rule = {**_battle_part(evolutions[plain[0]]["rule"]), **ANIME_EXTRA}
                    where = options[0]                       # vor die alten Wege
                else:
                    rule = dict(STAGE_RULE[stage])
                    where = (options[-1] + 1) if options else len(evolutions)
                h, m = (int(x) for x in BEDTIME[stage].split(":"))
                evolutions.insert(where, {"line": line, "from": a, "to": b, "stage": stage, "rule": rule,
                                          "bedtime": h * 60 + m, "name": by_num[b]["name"], "src": "anime"})
                added += 1
    return added


def custom_rows():
    """CUSTOM_LINES im selben Format wie die Zeilen aus lines.csv."""
    for line, entries in CUSTOM_LINES.items():
        for stage, dex, parents, rule, name in entries:
            yield {
                "LineID": line, "Stage": stage, "DexNum": str(dex),
                "Parents": parents if parents == "egg" else ";".join(map(str, parents)),
                "Rule": rule, "Bedtime": BEDTIME[stage], "Notes": name,
            }

# Soundeffekte, die ins Spiel kopiert werden (static/sounds/)
SOUNDS = ["alarm", "attack", "cancel", "click", "death", "eat", "evolve", "happy",
          "hatch", "lose", "poop", "refuse", "trainhit", "wash", "win", "menu", "confirm",
          "attackHit", "strongAttack", "strongHit", "startBattle", "reward"]


def parse_range(text):
    """'0-2' -> [0, 2], '3+' -> [3, None], '5' -> [5, 5]"""
    text = text.strip()
    if text.endswith("+"):
        return [int(text[:-1]), None]
    if "-" in text:
        a, b = text.split("-")
        return [int(a), int(b)]
    return [int(text), int(text)]


def parse_rule(rule):
    """'CM 0-2, TR 16+' -> {"cm": [0, 2], "tr": [16, None]}
    'A | B' (A oder B) -> {"any": [A, B]}"""
    options = [parse_conditions(p) for p in rule.split("|")]
    return options[0] if len(options) == 1 else {"any": options}


def parse_conditions(text):
    out = {}
    for part in text.split(","):
        part = part.strip()
        if not part or part == "TIME":
            continue
        key, _, val = part.partition(" ")
        if key in ("CM", "TR", "OF"):
            out[key.lower()] = parse_range(val)
        elif key == "BTL":                      # Kämpfe in dieser Stufe
            out["btl"] = parse_range(val)
        elif key == "KO6":                      # Siege in dieser Stufe
            out["wins"] = parse_range(val)
        elif key == "WIN":
            wins, battles = val.split("/")
            out["win"] = {"wins": int(wins), "battles": int(battles)}
        elif key == "JOGRESS":                  # Partner-Nr. oder Attribut (z. B. Vaccine/Data)
            out["jogress"] = int(val) if val.isdigit() else val
        else:
            raise ValueError(f"Unbekannte Regel: {part!r}")
    return out


def clean_name(notes):
    return re.split(r" \(|;|:", notes)[0].strip()


def build_line(line, rows, by_num):
    """Wandelt die Zeilen einer Linie um. Wirft ValueError, wenn die Linie nicht
    zu unseren Spielregeln passt (fremde Regeln, falsche Stufen, Lücken)."""
    first, evolutions, known = None, [], set()
    for r in rows:
        dex = int(r["DexNum"])
        sprite = by_num.get(dex)
        if not sprite:
            raise ValueError(f"kein Sprite für Nr. {dex}")
        if sprite["stage"] != r["Stage"]:
            raise ValueError(f"{sprite['name']} ist {sprite['stage']}, nicht {r['Stage']}")
        bed_h, bed_m = (int(x) for x in r["Bedtime"].split(":"))
        if r["Parents"] == "egg":
            if first is not None:
                raise ValueError("mehr als ein Ei")
            first, parents = dex, [None]
        else:
            parents = [int(p) for p in r["Parents"].split(";")]
        rule = parse_rule(r["Rule"])
        for p in parents:
            evolutions.append({
                "line": line, "from": p, "to": dex, "stage": r["Stage"], "rule": rule,
                "bedtime": bed_h * 60 + bed_m, "name": clean_name(r["Notes"]),
            })
        known.add(dex)
    if first is None:
        raise ValueError("kein Ei")
    missing = {e["from"] for e in evolutions if e["from"] is not None} - known
    if missing:
        raise ValueError(f"Eltern fehlen: {sorted(missing)}")
    return {"name": None, "first": first}, evolutions        # Name: egg_names()


def main():
    wheel = sys.argv[1]
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None   # Standard: alle passenden
    z = zipfile.ZipFile(wheel)
    sprites = json.loads(gzip.decompress(z.read("tuipet/data/sprites.json.gz")))
    by_num = {s["num"]: s for s in sprites}
    rows = list(csv.DictReader(io.StringIO(z.read("tuipet/data/lines.csv").decode("utf8"))))
    rows += list(custom_rows())

    by_line = {}
    for r in rows:
        by_line.setdefault(r["LineID"], []).append(r)

    lines, evolutions, skipped = {}, [], []
    for line, line_rows in by_line.items():
        if only and line not in only:
            continue
        try:
            info, evos = build_line(line, line_rows, by_num)
        except ValueError as e:
            if line in REQUIRED:        # unsere festen Linien müssen klappen
                raise ValueError(f"{line}: {e}") from e
            skipped.append(f"{line} ({e})")
            continue
        # gleiche Linie zweimal (z. B. V-Pet-Nachbau) nicht doppelt aufnehmen
        signature = sorted((e["from"] or 0, e["to"]) for e in evos)
        if any(sorted((e["from"] or 0, e["to"]) for e in evolutions if e["line"] == l) == signature
               for l in lines):
            skipped.append(f"{line} (doppelt)")
            continue
        lines[line] = info
        evolutions += evos
    evolutions[:] = [e for e in evolutions if by_num[e["to"]]["name"] not in EXCLUDE_NAMES
                     and (e["from"] is None or by_num[e["from"]]["name"] not in EXCLUDE_NAMES)]
    aliases = merge_same_names(lines, evolutions, by_num)
    print("Gleichnamige zusammengelegt:", len(aliases))
    for e in evolutions:
        key = (e["line"], e["from"] and by_num[e["from"]]["name"], by_num[e["to"]]["name"])
        if key in RULE_FIXES:
            e["rule"] = RULE_FIXES[key]
    print("Anime-Digitationen ergänzt:", add_anime_paths(lines, evolutions, by_num))
    # Sprünge über Stufen hinweg (z. B. Keramon X: Rookie -> Mega) bekommen eine
    # Kampf-Bedingung – sonst wäre das ein kostenloser Weg zum Mega
    order = ["Fresh", "InTraining", "Rookie", "Champion", "Ultimate", "Mega"]
    for e in evolutions:
        if e["from"] is None:
            continue
        a, b = order.index(by_num[e["from"]]["stage"]), order.index(e["stage"])
        if b > a + 1 and not e["rule"]:
            e["rule"] = {"win": {"wins": 12, "battles": 15}}
            print("Stufensprung mit Kampf-Bedingung:", by_num[e["from"]]["name"], "->", by_num[e["to"]]["name"])
    # Sprites von allem, was es irgendwann gab, behalten – falls ein laufender Spielstand
    # noch ein Digimon hat, das im neuen Baum nicht mehr vorkommt
    known = {d for e in evolutions for d in (e["from"], e["to"]) if d is not None}
    dropped = design_graph(lines, evolutions, by_num)
    print("Ohne Platz geblieben:", ", ".join(by_num[d]["name"] for d in dropped) or "keins")
    items, armor_forms = add_armor_paths(lines, evolutions, by_num)
    print("Armor-Eier:", len(items))
    line_aliases = merge_same_eggs(lines, evolutions)
    print("Gleiche Eier zusammengelegt:", len(line_aliases))
    egg_names(lines, lambda dex: NAME_DE.get(by_num[dex]["name"], by_num[dex]["name"]))
    add_event_lines(lines, evolutions, by_num)
    print("Event-Eier:", ", ".join(EVENT_LINES))
    used ={e["to"] for e in evolutions} | known | set(aliases) | set(aliases.values())
    for s in skipped:
        print("übersprungen:", s)

    digimon = {}
    for dex in sorted(used):
        s = by_num[dex]
        digimon[dex] = {
            "name": NAME_DE.get(s["name"], s["name"]),
            "stage": ARMOR_STAGE if dex in armor_forms else s["stage"], "attribute": s["attribute"],
            "field": s["field"], "element": s["element"], "frames": s["frames"],
        }
    for e in evolutions:
        e["name"] = NAME_DE.get(e["name"], e["name"])

    OUT.write_text(json.dumps({
        "source": "Sprites & Linien: tuipet (MIT, Joel Taylor) / Digimon (c) Bandai",
        "frames": FRAMES, "lines": lines, "evolutions": evolutions,
        "digimon": digimon,
        # Armor-Eier (Items aus dem Rucksack): Key -> Name, Beschreibung
        "items": items,
        # alte Nummer -> neue (gleichnamige Digimon wurden zusammengelegt)
        "aliases": {str(k): v for k, v in sorted(aliases.items())},
        # altes Ei -> behaltenes Ei (Eier mit gleichem Baby wurden zusammengelegt)
        "line_aliases": line_aliases,
    }, ensure_ascii=False, separators=(",", ":")), encoding="utf8")
    print(f"{len(lines)} Linien, {len(digimon)} Digimon, {len(evolutions)} Entwicklungen -> {OUT}")

    # Sounds gleich ohrenfreundlich machen (die Originale sind schrille Rechteck-Pieptöne)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from soften_sounds import soften
    sound_dir = OUT.parent.parent / "static" / "sounds"
    sound_dir.mkdir(exist_ok=True)
    for name in SOUNDS:
        (sound_dir / f"{name}.wav").write_bytes(soften(z.read(f"tuipet/data/sounds/{name}.wav")))
    print(f"{len(SOUNDS)} Sounds (weich gemacht) -> {sound_dir}")


if __name__ == "__main__":
    main()
