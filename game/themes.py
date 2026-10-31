"""V-Pet-Designs: Farben für Gehäuse und Display (wie die verschiedenen Original-V-Pets).

Ein Design kauft man im Shop – mit Bits oder (Event-Designs) mit Event-Items wie
Gruselbonbons. Gekaufte Designs gehören zum Konto (meta "themes:<owner>"), das aktive
steht in meta "theme:<owner>". Die Farben schickt der Server mit, der Browser setzt sie
als CSS-Variablen (Gehäuse-Verlauf, Display-Hintergrund, Pixel).
"""
from . import shop
from .i18n import T

DEFAULT = "classic"

# device: Verlauf des Gehäuses (3 Farben), lcd: Display, pixel: Pixel-Farbe
THEMES = {
    "classic": {"name": T("Klassisch"), "price": 0,
                "device": ["#2ee6ff", "#1b6dff", "#ff8a1f"], "lcd": "#a9e4d9", "pixel": "#06232f"},
    "original": {"name": T("Original Grau"), "price": 150,
                 "device": ["#e2e2e2", "#8c8c8c", "#3a3a3a"], "lcd": "#b7c4a4", "pixel": "#1f2a14"},
    "agumon": {"name": T("Agumon Orange"), "price": 150,
               "device": ["#ffd23f", "#ff8a1f", "#c4400a"], "lcd": "#f3e3b0", "pixel": "#3a1d00"},
    "gabumon": {"name": T("Gabumon Blau"), "price": 150,
                "device": ["#e8f1ff", "#3d7bff", "#0b2a8a"], "lcd": "#bcd6f5", "pixel": "#0a1a3d"},
    "biyomon": {"name": T("Biyomon Pink"), "price": 150,
                "device": ["#ffc2e0", "#ff4fa3", "#8a1a5c"], "lcd": "#f7d6e6", "pixel": "#3d0a24"},
    "palmon": {"name": T("Palmon Grün"), "price": 150,
               "device": ["#d8ff8a", "#4fc25a", "#1d5e2a"], "lcd": "#cfe8b8", "pixel": "#10260b"},
    "night": {"name": T("Nachtmodus"), "price": 250,
              "device": ["#4a5070", "#151a2e", "#05060c"], "lcd": "#0c1a24", "pixel": "#5ef0ff"},
    "gold": {"name": T("Gold"), "price": 600,
             "device": ["#fff2a8", "#e8b923", "#7a5200"], "lcd": "#f4e7b6", "pixel": "#3b2a00"},
    # Event-Design: kostet Gruselbonbons (Halloween-Item) statt Bits und ist nur während des
    # Events im Shop zu sehen/kaufen (wer es hat, behält es)
    "halloween": {"name": T("Halloween"), "item": "candy", "items": 10, "event": "halloween",
                  "device": ["#ff7a00", "#7a2cbf", "#2a0a3d"], "lcd": "#2a1838", "pixel": "#ffa53a"},
}

# Farben fürs ganze Spiel (Hintergrund, Flächen, Linien, Akzente) – passend zum Gehäuse.
# accent ersetzt das Cyan, accent2 das Orange (Hauptknöpfe haben dunkle Schrift -> hell genug wählen),
# muted = Nebenschrift (Stufe, Alter, Hinweise)
UI = {
    "classic": {"deep": "#030817", "bg": "#061031", "panel": "#0a1740", "panel2": "#0f2154", "line": "#1f3d86",
                "accent": "#2ee6ff", "accent2": "#ff8a1f", "muted": "#86a1d1"},
    "original": {"deep": "#0a0b0c", "bg": "#141618", "panel": "#1c1f22", "panel2": "#262a2e", "line": "#424950",
                 "accent": "#b7d99a", "accent2": "#e6e6e6", "muted": "#a0a8a0"},
    "agumon": {"deep": "#140802", "bg": "#221005", "panel": "#2f1708", "panel2": "#3d1f0b", "line": "#6b3a12",
               "accent": "#ffd23f", "accent2": "#ff8a1f", "muted": "#cfa67c"},
    "gabumon": {"deep": "#020a1c", "bg": "#06143a", "panel": "#0b1d52", "panel2": "#11286b", "line": "#2a4fa8",
                "accent": "#9cc4ff", "accent2": "#ffc94a", "muted": "#9fb4dd"},
    "biyomon": {"deep": "#140510", "bg": "#23091c", "panel": "#300d27", "panel2": "#3f1233", "line": "#7a2a63",
                "accent": "#ff8cc8", "accent2": "#ffb347", "muted": "#d6a0c4"},
    "palmon": {"deep": "#04120a", "bg": "#082012", "panel": "#0d2c19", "panel2": "#133a21", "line": "#2f6b3c",
               "accent": "#a6f07a", "accent2": "#ff8fc0", "muted": "#a2c99d"},
    "night": {"deep": "#000000", "bg": "#04070d", "panel": "#0a0f1a", "panel2": "#101828", "line": "#1e2c45",
              "accent": "#5ef0ff", "accent2": "#a99bff", "muted": "#7f93b3"},
    "gold": {"deep": "#120d02", "bg": "#1f1604", "panel": "#2b1f06", "panel2": "#3a2a09", "line": "#6b5214",
             "accent": "#ffe27a", "accent2": "#ffb000", "muted": "#cfb87e"},
    "halloween": {"deep": "#0b0414", "bg": "#160826", "panel": "#200b35", "panel2": "#2b1046", "line": "#4d2378",
                  "accent": "#c48bff", "accent2": "#ff8a1f", "muted": "#ad93cc"},
}


class ThemeError(Exception):
    """Kauf/Wechsel nicht möglich – die Meldung sieht der Spieler."""


def owned(store, owner):
    return {DEFAULT} | set(store.get_meta(f"themes:{owner}", []) or [])


def active(store, owner):
    key = store.get_meta(f"theme:{owner}", DEFAULT)
    return key if key in THEMES and key in owned(store, owner) else DEFAULT


def colors(key):
    t = THEMES[key]
    return {"key": key, "device": t["device"], "lcd": t["lcd"], "pixel": t["pixel"], "ui": UI[key]}


def cost(key):
    """Preis jetzt: Bits – oder bei Event-Designs die Anzahl Event-Items (der Admin kann beides ändern)."""
    t = THEMES[key]
    return shop.cost(f"theme:{key}", t["items"] if t.get("item") else t.get("price", 0))


def catalog(store, owner, event=None):
    """Designs für den Shop. Event-Designs nur während ihres Events – oder wenn man sie schon hat."""
    have, now = owned(store, owner), active(store, owner)
    from . import explore
    return [{**colors(key), "name": t["name"], "price": None if t.get("item") else cost(key), "item": t.get("item"),
             "item_name": explore.ITEMS[t["item"]]["name"] if t.get("item") else None,
             "items": cost(key) if t.get("item") else None, "owned": key in have, "active": key == now,
             "event": t.get("event")}
            for key, t in THEMES.items() if not t.get("event") or t["event"] == event or key in have]


def buy(store, owner, key, inventory, add_item, event=None):
    """Design kaufen: mit Bits oder mit Items aus dem Rucksack (`inventory` = {Item: Anzahl})."""
    t = THEMES.get(key)
    if not t:
        raise ThemeError(T("Dieses Design gibt es nicht."))
    if key in owned(store, owner):
        raise ThemeError(T("Das Design „{name}“ hast du schon.", name=t["name"]))
    if t.get("event") and t["event"] != event:
        raise ThemeError(T("Das Design „{name}“ gibt es nur während des Events.", name=t["name"]))
    price = cost(key)
    if t.get("item"):
        from . import explore
        have = inventory.get(t["item"], 0)
        if have < price:
            raise ThemeError(T("Dafür brauchst du {n}× {item} – du hast {have}.",
                               n=price, item=explore.ITEMS[t["item"]]["name"], have=have))
        add_item(t["item"], -price)
    else:
        bits = shop.balance(store, owner)
        if bits < price:
            raise ThemeError(T("Dafür reichen deine Bits nicht: {cost} Bits nötig, du hast {have}.",
                               cost=price, have=bits))
        shop.add(store, owner, -price)
    store.set_meta(f"themes:{owner}", sorted(owned(store, owner) | {key}))
    store.set_meta(f"theme:{owner}", key)                # gleich benutzen
    return T("Neues Design: {name}! Es ist gleich aktiv.", name=t["name"])


def use(store, owner, key):
    if key not in THEMES:
        raise ThemeError(T("Dieses Design gibt es nicht."))
    if key not in owned(store, owner):
        raise ThemeError(T("Das Design „{name}“ musst du erst kaufen.", name=THEMES[key]["name"]))
    store.set_meta(f"theme:{owner}", key)
    return T("Design gewechselt: {name}.", name=THEMES[key]["name"])
