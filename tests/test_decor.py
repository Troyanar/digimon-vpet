"""Tests für die Deko (kaufen, an/aus, Event-Deko).  Starten mit:  python -m unittest"""
import unittest

from game import decor, shop
from game.store import Store


class DecorTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.bag = {}

    def add_item(self, item, n):
        self.bag[item] = self.bag.get(item, 0) + n

    def test_buy_with_bits_and_toggle(self):
        self.assertEqual(decor.visible(self.store, "1"), [])
        with self.assertRaises(decor.DecorError):
            decor.toggle(self.store, "1", "snow", True)                      # nicht gekauft
        with self.assertRaises(decor.DecorError):
            decor.buy(self.store, "1", "snow", self.bag, self.add_item)      # keine Bits
        shop.add(self.store, "1", 200)
        decor.buy(self.store, "1", "snow", self.bag, self.add_item)
        self.assertEqual(shop.balance(self.store, "1"), 50)
        self.assertEqual(decor.visible(self.store, "1"), ["snow"])           # gleich an
        decor.toggle(self.store, "1", "snow", False)
        self.assertEqual(decor.visible(self.store, "1"), [])
        decor.toggle(self.store, "1", "snow", True)
        self.assertEqual(decor.visible(self.store, "1"), ["snow"])

    def test_bats_free_during_halloween_buy_to_keep(self):
        self.assertIn("bats", decor.visible(self.store, "1", "halloween"))  # Event: gratis zu sehen
        self.assertNotIn("bats", decor.visible(self.store, "1"))            # danach nicht
        decor.toggle(self.store, "1", "bats", False, "halloween")
        self.assertNotIn("bats", decor.visible(self.store, "1", "halloween"))  # abschaltbar
        self.assertNotIn("bats", [d["key"] for d in decor.catalog(self.store, "1")])
        self.bag = {"candy": 5}
        with self.assertRaises(decor.DecorError):
            decor.buy(self.store, "1", "bats", self.bag, self.add_item)      # nur im Event kaufbar
        decor.buy(self.store, "1", "bats", self.bag, self.add_item, "halloween")
        self.assertEqual(self.bag["candy"], 0)
        self.assertIn("bats", decor.visible(self.store, "1"))               # bleibt nach dem Event


class SellItemTest(unittest.TestCase):
    """Verkaufen im Rucksack: egal was, egal wie viele."""
    def setUp(self):
        self.store = Store(":memory:")
        self.bag = {"mut": 7, "snack": 2, "candy": 3}

    def add_item(self, item, n):
        self.bag[item] = self.bag.get(item, 0) + n

    def sell(self, item, n):
        return shop.sell(self.store, "1", item, n, dict(self.bag), self.add_item)

    def test_prices(self):
        self.assertEqual(shop.sell_price("snack"), shop.PRICES["snack"] // 2)    # halber Shop-Preis
        self.assertEqual(shop.sell_price("mut"), 50)                             # Armor-Ei
        self.assertEqual(shop.sell_price("wunder"), 200)                         # goldenes Armor-Ei
        self.assertEqual(shop.sell_price("candy"), 10)
        from game import explore
        self.assertTrue(all(shop.sell_price(k) for k in explore.ITEMS))          # alles verkaufbar

    def test_sell_any_amount(self):
        self.sell("mut", 6)                                     # mehr als 5 auf einmal
        self.assertEqual((self.bag["mut"], shop.balance(self.store, "1")), (1, 300))
        self.sell("mut", 1)                                     # auch das letzte
        self.assertEqual(self.bag["mut"], 0)
        self.sell("candy", 3)
        self.assertEqual(shop.balance(self.store, "1"), 380)   # 6×50 + 50 + 3×10

    def test_sell_errors(self):
        for item, n in (("mut", 8), ("mut", 0), ("weight", 1), ("quatsch", 1), ("snack", "2")):
            with self.assertRaises(shop.ShopError):
                self.sell(item, n)
        self.assertEqual((self.bag["mut"], shop.balance(self.store, "1")), (7, 0))   # nichts passiert


if __name__ == "__main__":
    unittest.main()
