"""Server-weite Einstellungen, die der Admin im Admin-Bereich ändert.

Gespeichert in der meta-Tabelle (Schlüssel "settings"). Die Spiel-Logik liest
immer `CURRENT` – der Server lädt es beim Start und nach jeder Änderung neu.
"""

DEFAULTS = {
    # Spielregeln
    "death": True,             # können Digimon sterben?
    "need_speed": 1.0,         # Tempo von Hunger, Kraft und Kacke (0.5 = halb so schnell)
    "explore_luck": 1.0,       # Fundglück beim Erkunden
    "battle_egg_chance": 0.12, # Ei-Chance nach einem Sieg gegen wilde Digimon
    "free_egg": True,          # Notfall-Ei, wenn man gar nichts mehr hat
    # Zugang
    "registration": "invite",  # invite (nur mit Code) / open / closed
    "maintenance": False,      # nur Admins können spielen
    "announcement": "",        # Nachricht an alle (Banner im Spiel)
}

# erlaubte Werte (Liste) bzw. Bereich (Tupel min, max)
ALLOWED = {
    "death": (False, True),
    "need_speed": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0],
    "explore_luck": [0.5, 1.0, 1.5, 2.0, 3.0],
    "battle_egg_chance": (0.0, 0.5),
    "free_egg": (False, True),
    "registration": ["invite", "open", "closed"],
    "maintenance": (False, True),
}

CURRENT = dict(DEFAULTS)


def load(store):
    CURRENT.clear()
    CURRENT.update(DEFAULTS)
    CURRENT.update({k: v for k, v in (store.get_meta("settings", {}) or {}).items() if k in DEFAULTS})
    return CURRENT


def update(store, changes):
    """Übernimmt gültige Änderungen; liefert die neuen Einstellungen.
    Wirft ValueError bei ungültigen Werten."""
    if not isinstance(changes, dict):
        raise ValueError("Ungültige Einstellungen.")
    new = dict(CURRENT)
    for key, value in changes.items():
        if key not in DEFAULTS:
            raise ValueError(f"Unbekannte Einstellung: {key}")
        if key == "announcement":
            if not isinstance(value, str):
                raise ValueError("Die Nachricht muss ein Text sein.")
            value = value.strip()[:300]
        elif isinstance(DEFAULTS[key], bool):
            if not isinstance(value, bool):               # "false" wäre sonst True
                raise ValueError(f"{key} muss an oder aus sein.")
        elif isinstance(ALLOWED[key], list):
            if isinstance(DEFAULTS[key], float):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError(f"Ungültiger Wert für {key}")
                value = float(value)
            if value not in ALLOWED[key]:
                raise ValueError(f"Ungültiger Wert für {key}")
        else:
            lo, hi = ALLOWED[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Ungültiger Wert für {key}")
            value = float(value)
            if not lo <= value <= hi:                     # fängt auch NaN/unendlich ab
                raise ValueError(f"{key} muss zwischen {lo} und {hi} liegen")
        new[key] = value
    store.set_meta("settings", new)
    CURRENT.clear()
    CURRENT.update(new)
    return CURRENT
