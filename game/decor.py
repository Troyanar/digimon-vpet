"""Deko fürs V-Pet-Display (Fledermäuse, Sterne, Schnee …) – kaufen und an-/ausschalten.

Gekaufte Deko gehört zum Konto (meta "decor:<owner>"), ob sie an ist, steht in
meta "decor_on:<owner>" ({Key: an/aus}). Event-Deko (z. B. Fledermäuse zu Halloween) ist
während ihres Events für alle gratis zu sehen (abschaltbar) und nur dann kaufbar – wer sie
kauft, behält sie auch nach dem Event. Gezeichnet wird sie im Browser (game.js renderDecor).
"""
from . import shop
from .i18n import T

DECOR = {
    "bats": {"name": T("Fledermäuse"), "desc": T("Flattern oben durch die Symbolleiste"),
             "item": "candy", "items": 5, "event": "halloween"},
    "stars": {"name": T("Sternenfunkeln"), "desc": T("Kleine Sterne funkeln oben im Display"), "price": 100},
    "bubbles": {"name": T("Seifenblasen"), "desc": T("Blasen steigen am Rand des Displays auf"), "price": 120},
    "hearts": {"name": T("Herzchen"), "desc": T("Ab und zu steigt ein Herz über deinem Digimon auf"), "price": 120},
    "snow": {"name": T("Schneefall"), "desc": T("Schneeflocken rieseln durchs Display"), "price": 150},
}


class DecorError(Exception):
    """Kauf/Schalten nicht möglich – die Meldung sieht der Spieler."""


def owned(store, owner):
    return set(store.get_meta(f"decor:{owner}", []) or [])


def settings(store, owner):
    return dict(store.get_meta(f"decor_on:{owner}", {}) or {})


def _available(key, have, event):
    """Darf die Deko gerade gezeigt werden? (gekauft – oder Event-Deko während ihres Events)"""
    return key in have or (event is not None and DECOR[key].get("event") == event)


def visible(store, owner, event=None):
    """Welche Deko das Display jetzt zeigt (für den Browser)."""
    have, on = owned(store, owner), settings(store, owner)
    return [key for key in DECOR if _available(key, have, event) and on.get(key, True)]


def cost(key):
    """Preis jetzt: Bits – oder bei Event-Deko die Anzahl Event-Items (der Admin kann beides ändern)."""
    d = DECOR[key]
    return shop.cost(f"decor:{key}", d["items"] if d.get("item") else d["price"])


def catalog(store, owner, event=None):
    """Deko für den Shop: Event-Deko nur während ihres Events (oder wenn man sie hat)."""
    from . import explore
    have, on = owned(store, owner), settings(store, owner)
    out = []
    for key, d in DECOR.items():
        if d.get("event") and d["event"] != event and key not in have:
            continue
        out.append({"key": key, "name": d["name"], "desc": d["desc"],
                    "price": None if d.get("item") else cost(key),
                    "item": d.get("item"), "items": cost(key) if d.get("item") else None,
                    "item_name": explore.ITEMS[d["item"]]["name"] if d.get("item") else None,
                    "event": d.get("event"), "owned": key in have,
                    "available": _available(key, have, event), "on": on.get(key, True)})
    return out


def buy(store, owner, key, inventory, add_item, event=None):
    d = DECOR.get(key)
    if not d:
        raise DecorError(T("Diese Deko gibt es nicht."))
    if key in owned(store, owner):
        raise DecorError(T("Die Deko „{name}“ hast du schon.", name=d["name"]))
    if d.get("event") and d["event"] != event:
        raise DecorError(T("Die Deko „{name}“ gibt es nur während des Events.", name=d["name"]))
    price = cost(key)
    if d.get("item"):
        from . import explore
        have = inventory.get(d["item"], 0)
        if have < price:
            raise DecorError(T("Dafür brauchst du {n}× {item} – du hast {have}.",
                               n=price, item=explore.ITEMS[d["item"]]["name"], have=have))
        add_item(d["item"], -price)
    else:
        bits = shop.balance(store, owner)
        if bits < price:
            raise DecorError(T("Dafür reichen deine Bits nicht: {cost} Bits nötig, du hast {have}.",
                               cost=price, have=bits))
        shop.add(store, owner, -price)
    store.set_meta(f"decor:{owner}", sorted(owned(store, owner) | {key}))
    toggle(store, owner, key, True, event)
    return T("Neue Deko: {name}! Sie ist gleich an.", name=d["name"])


def toggle(store, owner, key, on, event=None):
    d = DECOR.get(key)
    if not d:
        raise DecorError(T("Diese Deko gibt es nicht."))
    if not _available(key, owned(store, owner), event):
        raise DecorError(T("Die Deko „{name}“ musst du erst kaufen.", name=d["name"]))
    value = settings(store, owner)
    value[key] = bool(on)
    store.set_meta(f"decor_on:{owner}", value)
    return T("{name}: an.", name=d["name"]) if on else T("{name}: aus.", name=d["name"])
