"""Tests für Shop, Bits und die neuen Items (Ewigstein, Sanduhren, Löschdiskette).
Starten mit:  python -m unittest"""
import unittest

from game import battle, data, duel, explore, shop
from game import pet as P
from game.store import Store
from tests.test_battle import Always, rookie


class ShopTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.bag = {}

    def add_item(self, item, n):
        self.bag[item] = self.bag.get(item, 0) + n

    def test_buy_needs_bits(self):
        with self.assertRaises(shop.ShopError):
            shop.buy(self.store, "1", "snack", 1, self.add_item)
        shop.add(self.store, "1", 100)
        shop.buy(self.store, "1", "snack", 2, self.add_item)
        self.assertEqual(self.bag, {"snack": 2})
        self.assertEqual(shop.balance(self.store, "1"), 100 - 2 * shop.PRICES["snack"])
        self.assertEqual(shop.balance(self.store, "2"), 0)              # anderes Konto

    def test_armor_eggs_and_nonsense_not_for_sale(self):
        shop.add(self.store, "1", 10000)
        for item in [*data.ARMOR_ITEMS, "gibtsnicht"]:
            with self.assertRaises(shop.ShopError):
                shop.buy(self.store, "1", item, 1, self.add_item)
        for amount in (0, -1, shop.MAX_BUY + 1, "3"):
            with self.assertRaises(shop.ShopError):
                shop.buy(self.store, "1", "snack", amount, self.add_item)
        self.assertEqual(self.bag, {})
        self.assertFalse(set(shop.PRICES) & set(data.ARMOR_ITEMS))
        self.assertTrue(set(shop.PRICES) <= set(explore.ITEMS))

    def test_balance_never_negative(self):
        shop.add(self.store, "1", 5)
        self.assertEqual(shop.add(self.store, "1", -50), 0)


def minute(month, day, hour=12):
    from datetime import datetime
    return int(datetime(2026, month, day, hour, 0).timestamp() // 60)


class PriceAndStealTest(unittest.TestCase):
    """Admin-Preise und Daily Steal (immer 40 % günstiger)."""
    def setUp(self):
        self.store = Store(":memory:")
        self.bag = {}

    def tearDown(self):
        shop.OVERRIDES.clear()                    # Modul-Zustand für andere Tests zurücksetzen
        shop.DAILY_PIN["item"] = None

    def add_item(self, item, n):
        self.bag[item] = self.bag.get(item, 0) + n

    def test_candy_costs_90(self):
        self.assertEqual(shop.price_of("candy"), 90)

    def test_daily_steal_same_all_day_changes_between_days(self):
        day = shop.daily_steal(minute(11, 5, 1))
        self.assertEqual(shop.daily_steal(minute(11, 5, 23)), day)
        self.assertIn(day, shop.PRICES)
        days = {shop.daily_steal(minute(11, d)) for d in range(1, 29)}
        self.assertGreater(len(days), 3)                                   # wechselt wirklich

    def test_steal_is_40_percent_off_and_on_top(self):
        now = minute(11, 5)
        steal = shop.daily_steal(now)
        rows = shop.catalog(None, now)
        self.assertEqual(rows[0]["key"], steal)
        self.assertTrue(rows[0]["steal"])
        self.assertEqual(rows[0]["price"], round(shop.PRICES[steal] * 0.6))
        self.assertEqual(rows[0]["regular"], shop.PRICES[steal])
        self.assertFalse(any(r["steal"] for r in rows[1:]))
        shop.add(self.store, "1", 10000)
        shop.buy(self.store, "1", steal, 2, self.add_item, minute=now)
        self.assertEqual(shop.balance(self.store, "1"), 10000 - 2 * round(shop.PRICES[steal] * 0.6))
        self.assertEqual(shop.sell_price(steal), shop.PRICES[steal] // 2)   # Verkauf vom normalen Preis

    def test_admin_prices_and_pinned_steal(self):
        shop.set_prices(self.store, {"totem": 250, "snack": None}, "totem")
        self.assertEqual(shop.price_of("totem"), 250)
        self.assertEqual(shop.daily_steal(minute(11, 5)), "totem")
        self.assertEqual(shop.catalog(None, minute(11, 5))[0]["price"], 150)   # 250 − 40 %
        shop.set_prices(self.store, {"totem": shop.PRICES["totem"]}, "auto")  # zurück auf Standard
        self.assertNotIn("totem", shop.OVERRIDES)
        self.assertIsNone(shop.DAILY_PIN["item"])
        shop.set_prices(self.store, {"candy": 120}, "auto")
        shop.OVERRIDES.clear()
        shop.load(self.store)                                                # übersteht einen Neustart
        self.assertEqual(shop.price_of("candy"), 120)
        for bad in ({"snack": 0}, {"snack": -5}, {"snack": "30"}, {"snack": True}, {"gibtsnicht": 5}):
            with self.assertRaises(ValueError):
                shop.set_prices(self.store, bad, "auto")
        with self.assertRaises(ValueError):
            shop.set_prices(self.store, {}, "mut")                           # Armor-Eier nicht im Shop


class ThemeDecorPriceTest(unittest.TestCase):
    """Admin-Preise auch für Designs und Deko (Bits bzw. Anzahl Event-Items)."""
    def setUp(self):
        self.store = Store(":memory:")
        self.bag = {"candy": 20}

    def tearDown(self):
        shop.OVERRIDES.clear()
        shop.DAILY_PIN["item"] = None

    def add_item(self, item, n):
        self.bag[item] = self.bag.get(item, 0) + n

    def test_defaults_cover_themes_and_decor(self):
        d = shop.all_defaults()
        self.assertEqual((d["theme:gold"], d["theme:halloween"], d["decor:snow"], d["decor:bats"]), (600, 10, 150, 5))
        self.assertNotIn("theme:classic", d)                                # gratis bleibt gratis

    def test_changed_prices_apply_to_catalog_and_buy(self):
        from game import decor, themes
        shop.set_prices(self.store, {"theme:gold": 400, "theme:halloween": 12, "decor:snow": 90, "decor:bats": 3}, "auto")
        cat = {t["key"]: t for t in themes.catalog(self.store, "1", "halloween")}
        self.assertEqual((cat["gold"]["price"], cat["halloween"]["items"]), (400, 12))
        shop.add(self.store, "1", 1000)
        themes.buy(self.store, "1", "gold", self.bag, self.add_item)
        self.assertEqual(shop.balance(self.store, "1"), 600)
        themes.buy(self.store, "1", "halloween", self.bag, self.add_item, "halloween")
        decor.buy(self.store, "1", "bats", self.bag, self.add_item, "halloween")
        self.assertEqual(self.bag["candy"], 20 - 12 - 3)
        decor.buy(self.store, "1", "snow", self.bag, self.add_item)
        self.assertEqual(shop.balance(self.store, "1"), 510)
        with self.assertRaises(ValueError):
            shop.set_prices(self.store, {"theme:classic": 5}, "auto")       # gibt es nicht zu kaufen


class RewardTest(unittest.TestCase):
    def test_wild_battle_pays_bits(self):
        p = rookie(strength=4, trainings=20, power=10)
        now = p["last"]
        battle.scout(p, now, Always(0.0))
        battle.fight(p, now)
        result = {}
        while not result.get("over"):
            result = battle.shot(p, 1.0, now, Always(0.0))
            if not result["over"]:                           # immer ausweichen
                result = battle.evade(p, [True] * len(result["incoming"]), now, Always(0.0))
        self.assertTrue(result["won"])
        self.assertEqual(result["bits"], shop.WILD_WIN["Rookie"])
        self.assertIn("Bits", result["message"])

    def test_expedition_pays_bits(self):
        p = rookie()
        now = p["last"]
        explore.start(p, "wald", 120, now)
        P.advance(p, now + 120)
        got = []
        report = explore.claim(p, now + 120, lambda line: True, lambda item: None, Always(0.99), got.append)
        self.assertEqual(got, [shop.TRIP[120][0]])
        self.assertIn("Bits", report["text"])

    def test_clean_bonus_is_rare(self):
        self.assertEqual(shop.clean_reward(Always(0.5)), 0)
        self.assertEqual(shop.clean_reward(Always(0.0)), shop.CLEAN_BITS[0])

    def test_duel_bits(self):
        d = {"data": {"names": {"a": "A", "b": "B"}, "pets": {}}}
        duel._finish(d, {"a": None, "b": None}, "a", 0, Always(0.0))
        self.assertEqual(d["data"]["bits"], {"a": shop.DUEL["win"], "b": shop.DUEL["loss"]})
        duel._finish(d, {"a": None, "b": None}, "b", 0, Always(0.0), gave_up="a")
        self.assertEqual(d["data"]["bits"]["a"], 0)                      # wer aufgibt, bekommt nichts


class ItemTest(unittest.TestCase):
    def test_everstone_stops_digivolution_until_taken_off(self):
        p = rookie()
        now = p["last"]
        explore.use_item(p, "everstone", now)
        with self.assertRaises(P.Refused):
            explore.use_item(p, "everstone", now)                        # schon einer
        p["stage_since"] = now - P.STAGE_TIME["Rookie"] - 5               # Zeit ist längst um
        P.advance(p, now + 1)
        self.assertEqual(p["stage"], "Rookie")
        self.assertTrue(P.view(p, now + 1)["everstone"])
        explore.take_everstone(p, now + 1)
        P.advance(p, now + 2)
        self.assertEqual(p["stage"], "Champion")

    def test_hourglass_only_skips_waiting(self):
        p = rookie()
        now = p["last"]
        hunger, since = p["hunger"], p["stage_since"]
        explore.use_item(p, "hourglass6", now)
        self.assertEqual(p["stage_since"], since - 360)
        self.assertEqual(p["hunger"], hunger)                            # Hunger läuft nicht mit
        self.assertEqual(p["mistakes"], 0)

    def test_hourglass_shortens_expedition(self):
        p = rookie()
        now = p["last"]
        since = p["stage_since"]
        explore.start(p, "wald", 480, now)
        explore.use_item(p, "hourglass3", now)                           # geht auch unterwegs
        self.assertEqual(p["expedition"]["end"], now + 300)
        self.assertEqual(p["stage_since"], since - 180)                  # Digitationszeit spult mit
        explore.use_item(p, "hourglass6", now)
        self.assertEqual(p["expedition"]["end"], now)
        P.advance(p, now + 1)
        self.assertIn("expedition_return", p)

    def test_hourglass_away_works_even_without_digivolution(self):
        p = rookie()
        now = p["last"]
        explore.use_item(p, "everstone", now)
        since = p["stage_since"]
        explore.start(p, "wald", 480, now)
        explore.use_item(p, "hourglass1", now)                           # Ewigstein: nur die Reise
        self.assertEqual(p["expedition"]["end"], now + 420)
        self.assertEqual(p["stage_since"], since)

    def test_hourglass_on_collection_digimon(self):
        from game import collection
        store = Store(":memory:")
        p = rookie()
        now = p["last"]
        p["in_box"] = True
        pet_id = store.add_pet("1", p, active=False)["id"]
        since = p["stage_since"]
        collection.send(store, "1", pet_id, "wald", 480, now)
        collection.use_hourglass(store, "1", pet_id, "hourglass3", now)  # Reise + Digitation
        boxed = collection.boxed(store, "1")[0]
        self.assertEqual(boxed["box_trip"]["end"], now + 300)
        self.assertEqual(boxed["stage_since"], since - 180)
        with self.assertRaises(P.Refused):
            collection.use_hourglass(store, "1", pet_id, "snack", now)   # nur Sanduhren
        collection.recall_trip(store, "1", pet_id, now)
        with self.assertRaises(P.Refused) as e:                         # ohne Reise: geht nicht
            collection.use_hourglass(store, "1", pet_id, "hourglass1", now)
        self.assertIn("Das geht nicht", str(e.exception))
        self.assertEqual(collection.boxed(store, "1")[0]["stage_since"], since - 180)

    def test_hourglass_refused_when_nothing_to_wait_for(self):
        p = rookie()
        now = p["last"]
        p["stage_since"] = now - P.STAGE_TIME["Rookie"]
        with self.assertRaises(P.Refused):
            explore.use_item(p, "hourglass1", now)                       # Digitation schon fällig
        p = rookie()
        explore.use_item(p, "everstone", now)
        with self.assertRaises(P.Refused):
            explore.use_item(p, "hourglass1", now)                       # Ewigstein hält es auf

    def test_erase_disk(self):
        p = rookie()
        now = p["last"]
        with self.assertRaises(P.Refused):
            explore.use_item(p, "erase", now)                            # nichts zu löschen
        p["mistakes"], p["mistakes_total"] = 2, 5
        explore.use_item(p, "erase", now)
        self.assertEqual((p["mistakes"], p["mistakes_total"]), (1, 4))


if __name__ == "__main__":
    unittest.main()
