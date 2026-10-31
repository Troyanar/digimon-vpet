"""Shop und Bits (die Währung der Digital World).

Bits verdient man beim Erkunden, in Kämpfen (wild und gegen Freunde) und selten
beim Putzen. Im Shop kauft man damit Items für den Rucksack – fast alle, nur
Armor-Eier nicht (die gibt es weiter nur beim Erkunden).

Kontostand pro Konto in meta "bits:<owner>".
"""
import random

from . import data, explore
from .i18n import T

# Preise in Bits – Armor-Eier stehen absichtlich nicht drin
PRICES = {
    "snack": 30,
    "weight": 50,
    "charm": 60,
    "hourglass1": 40,
    "hourglass3": 100,
    "hourglass6": 180,
    "erase": 120,
    "virus": 80,
    "everstone": 150,
    "totem": 300,
    "reset": 500,             # gibt es NUR im Shop
}
# nur während eines Events (game/events.py) im Shop
EVENT_PRICES = {"halloween": {"candy": 90}}
# Daily Steal: jeden Tag ist ein Shop-Item so viel günstiger (automatisch reihum oder vom Admin festgelegt)
STEAL_DISCOUNT = 0.40
PRICE_MAX = 100_000
# vom Admin geänderte Preise (meta "prices" = {Item: Bits}) und festgelegter Daily Steal
# (meta "daily_steal" = Item, None = jeden Tag automatisch ein anderes) – load() liest beides
OVERRIDES = {}
DAILY_PIN = {"item": None}
# Tausch gegen Event-Items (nur während des Events): Gruselbonbons -> Halloween-Ei
CANDY_OFFERS = {"halloween": {"egg": {"item": "candy", "cost": 15, "egg": "halloween"}}}
MAX_BUY = 20                  # höchstens so viele auf einmal
# Verkaufen im Rucksack: Shop-Items bringen die Hälfte ihres Preises, alles andere steht hier
SELL_EXTRA = {"candy": 10, "armor": 50, "wunder": 200, "shard": 15}

# Belohnungen
WILD_WIN = {"Rookie": 10, "Champion": 15, "Armor": 18, "Ultimate": 22, "Mega": 30}   # + 0..5 Zufall
WILD_LOSS = 2
DUEL = {"win": 25, "draw": 10, "loss": 5}                     # Aufgeben: 0
TRIP = {30: (5, 10), 120: (15, 30), 480: (50, 80)}            # pro Expedition (von–bis)
CLEAN_CHANCE = 0.10                                          # beim Putzen Bits gefunden …
CLEAN_BITS = (3, 8)                                           # … so viele


def _key(owner):
    return f"bits:{owner}"


def balance(store, owner):
    return int(store.get_meta(_key(owner), 0) or 0)


def add(store, owner, amount):
    """Bits gutschreiben (negativ = abziehen). Liefert den neuen Kontostand."""
    value = max(0, balance(store, owner) + int(amount))
    store.set_meta(_key(owner), value)
    return value


def bits_text(n):
    return T("+{n} Bits", n=n)


def wild_reward(stage, won, rng=random):
    return WILD_WIN.get(stage, 10) + rng.randint(0, 5) if won else WILD_LOSS


def trip_reward(minutes, rng=random):
    lo, hi = TRIP.get(minutes, (0, 0))
    return rng.randint(lo, hi)


def clean_reward(rng=random):
    """Beim Putzen: selten ein paar Bits zwischen der Kacke (0 = nichts gefunden)."""
    return rng.randint(*CLEAN_BITS) if rng.random() < CLEAN_CHANCE else 0


# ---------------------------------------------------------------- Preise (Admin) & Daily Steal

class ShopError(Exception):
    """Kauf nicht möglich – die Meldung sieht der Spieler."""


def default_prices():
    """Alle Items mit Shop-Preis (auch Event-Items) und ihr Standardpreis."""
    out = dict(PRICES)
    for event_prices in EVENT_PRICES.values():
        out.update(event_prices)
    return out


def all_defaults():
    """Alles mit anpassbarem Preis und sein Standard: Shop-Items (Bits), Designs ("theme:<key>")
    und Deko ("decor:<key>") – dort Bits oder, bei Event-Sachen, die Anzahl Event-Items."""
    from . import decor, themes
    out = default_prices()
    for key, t in themes.THEMES.items():
        if t.get("item") or t.get("price"):                  # das Gratis-Design bleibt gratis
            out[f"theme:{key}"] = t["items"] if t.get("item") else t["price"]
    for key, d in decor.DECOR.items():
        out[f"decor:{key}"] = d["items"] if d.get("item") else d["price"]
    return out


def cost(key, default):
    """Preis eines Designs/einer Deko ("theme:…"/"decor:…") – Admin-Preis oder Standard."""
    return OVERRIDES.get(key, default)


def label(key):
    """Lesbarer Name zu einem Preis-Schlüssel (für Meldungen im Admin-Bereich)."""
    from . import decor, themes
    kind, _, name = key.partition(":")
    if kind == "theme":
        return f"Design „{themes.THEMES[name]['name']}“"
    if kind == "decor":
        return f"Deko „{decor.DECOR[name]['name']}“"
    return str(explore.ITEMS[key]["name"])


def load(store):
    """Admin-Preise und festgelegten Daily Steal aus dem Spielstand lesen (Start / nach Backup)."""
    defaults = all_defaults()
    OVERRIDES.clear()
    OVERRIDES.update({k: int(v) for k, v in (store.get_meta("prices", {}) or {}).items() if k in defaults})
    pin = store.get_meta("daily_steal", None)
    DAILY_PIN["item"] = pin if pin in PRICES else None


def price_of(item):
    """Normaler Preis jetzt (Admin-Preis oder Standard), ohne Daily-Steal-Rabatt."""
    return OVERRIDES.get(item, default_prices().get(item))


def steal_price(item):
    return max(1, round(price_of(item) * (1 - STEAL_DISCOUNT)))


def daily_steal(minute):
    """Das Item, das heute (Spiel-Zeitzone) 40 % günstiger ist."""
    if DAILY_PIN["item"]:
        return DAILY_PIN["item"]
    from . import pet as P
    day = P.local_time(minute).date().isoformat()
    return random.Random(f"daily-steal-{day}").choice(sorted(PRICES))


def set_prices(store, changes, pin):
    """Admin: Preise ändern ({Schlüssel: Preis}, None = zurück auf Standard; Schlüssel wie in
    all_defaults) und den Daily Steal festlegen (Item oder "auto"). ValueError bei ungültigen Werten."""
    defaults = all_defaults()
    new = dict(OVERRIDES)
    for item, value in (changes or {}).items():
        if item not in defaults:
            raise ValueError(f"Unbekanntes Item: {item}")
        if value is None or value == defaults[item]:
            new.pop(item, None)
            continue
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= PRICE_MAX:
            raise ValueError(f"Preis für {label(item)}: 1 bis {PRICE_MAX}")
        new[item] = value
    if pin not in (None, "auto") and pin not in PRICES:
        raise ValueError("Diesen Daily Steal gibt es nicht.")
    store.set_meta("prices", new)
    store.set_meta("daily_steal", None if pin in (None, "auto") else pin)
    load(store)


def prices(event=None, minute=None):
    """Preise jetzt – Event-Items vorne, mit `minute` ist der Daily Steal schon rabattiert."""
    out = {key: price_of(key) for key in EVENT_PRICES.get(event, {})}
    out.update({key: price_of(key) for key in PRICES})
    if minute is not None:
        steal = daily_steal(minute)
        out[steal] = steal_price(steal)
    return out


def catalog(event=None, minute=None):
    """Was es im Shop gibt (für den Browser). Event-Items und der Daily Steal (ganz vorne) sind markiert."""
    special = EVENT_PRICES.get(event, {})
    steal = daily_steal(minute) if minute is not None else None
    rows = [{"key": key, "price": price, "name": explore.ITEMS[key]["name"], "desc": explore.ITEMS[key]["desc"],
             "event": key in special, "only_shop": key == "reset",
             "steal": key == steal, "regular": price_of(key)}
            for key, price in prices(event, minute).items()]
    rows.sort(key=lambda r: not r["steal"])          # Daily Steal zuerst (sort ist stabil)
    return rows


def candy_offers(event):
    """Tausch-Angebote gegen Event-Items (für den Browser)."""
    from . import data
    out = []
    for key, o in CANDY_OFFERS.get(event, {}).items():
        out.append({"key": key, "cost": o["cost"], "item": o["item"], "item_name": explore.ITEMS[o["item"]]["name"],
                    "name": data.line_name(o["egg"]),
                    "desc": T("Wird garantiert zu Pumpkinmon – egal, wie du dich kümmerst. Kommt in deine Sammlung.")})
    return out


def trade_candy(key, event, inventory, add_item, store_egg):
    """Event-Items eintauschen (z. B. 15 Gruselbonbons -> Digi-Ei Halloween in die Sammlung)."""
    from . import data
    offer = CANDY_OFFERS.get(event, {}).get(key)
    if not offer:
        raise ShopError(T("Diesen Tausch gibt es gerade nicht."))
    have = inventory.get(offer["item"], 0)
    name = explore.ITEMS[offer["item"]]["name"]
    if have < offer["cost"]:
        raise ShopError(T("Dafür brauchst du {n}× {item} – du hast {have}.", n=offer["cost"], item=name, have=have))
    if not store_egg(offer["egg"]):
        raise ShopError(T("Deine Sammlung ist voll – lass erst ein Digimon frei."))
    add_item(offer["item"], -offer["cost"])
    return T("Getauscht: {n}× {item} gegen ein {egg}! Es liegt in deiner Sammlung.",
             n=offer["cost"], item=name, egg=data.line_name(offer["egg"]))


def sell_price(item):
    """Bits pro Stück beim Verkaufen (None = kann man nicht verkaufen)."""
    if item in PRICES:
        return price_of(item) // 2            # vom normalen Preis, nicht vom Daily Steal
    if item in SELL_EXTRA:
        return SELL_EXTRA[item]
    if item in data.ARMOR_ITEMS:
        return SELL_EXTRA["armor"]
    if item in explore.SHARD_ITEMS:
        return SELL_EXTRA["shard"]
    return None


def sell(store, owner, item, amount, inventory, add_item):
    """Items aus dem Rucksack verkaufen – egal was, egal wie viele (bis alles weg ist)."""
    price = sell_price(item)
    if price is None or item not in explore.ITEMS:
        raise ShopError(T("Das kann man nicht verkaufen."))
    have = inventory.get(item, 0)
    if have < 1:
        raise ShopError(T("Davon hast du nichts im Rucksack."))
    if not isinstance(amount, int) or not 1 <= amount <= have:
        raise ShopError(T("Du kannst 1 bis {n} Stück verkaufen.", n=have))
    add_item(item, -amount)
    bits = price * amount
    add(store, owner, bits)
    name = explore.ITEMS[item]["name"]
    if amount == 1:
        return T("Verkauft: {item} für {bits} Bits.", item=name, bits=bits)
    return T("Verkauft: {n}× {item} für {bits} Bits.", n=amount, item=name, bits=bits)


def buy(store, owner, item, amount, add_item, event=None, minute=None):
    """Item kaufen: Bits abziehen, Item in den Rucksack (`add_item(key, anzahl)`).
    Mit `minute` gilt der Daily-Steal-Preis des Tages."""
    price = prices(event, minute).get(item)
    if price is None:
        raise ShopError(T("Das gibt es im Shop nicht."))
    if not isinstance(amount, int) or not 1 <= amount <= MAX_BUY:
        raise ShopError(T("Du kannst 1 bis {n} Stück auf einmal kaufen.", n=MAX_BUY))
    cost = price * amount
    have = balance(store, owner)
    if cost > have:
        raise ShopError(T("Dafür reichen deine Bits nicht: {cost} Bits nötig, du hast {have}.", cost=cost, have=have))
    add(store, owner, -cost)
    add_item(item, amount)
    name = explore.ITEMS[item]["name"]
    if amount == 1:
        return T("Gekauft: {item} für {cost} Bits.", item=name, cost=cost)
    return T("Gekauft: {n}× {item} für {cost} Bits.", n=amount, item=name, cost=cost)
