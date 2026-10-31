"""Tests für die V-Pet-Designs.  Starten mit:  python -m unittest"""
import re
import unittest

from game import shop, themes
from game.store import Store


class ThemeTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.bag = {}

    def add_item(self, item, n):
        self.bag[item] = self.bag.get(item, 0) + n

    def test_classic_is_free_and_default(self):
        self.assertEqual(themes.active(self.store, "1"), "classic")
        self.assertIn("classic", themes.owned(self.store, "1"))
        self.assertEqual(themes.colors("classic")["lcd"], "#a9e4d9")

    def test_buy_with_bits(self):
        with self.assertRaises(themes.ThemeError):
            themes.buy(self.store, "1", "gold", self.bag, self.add_item)        # zu wenig Bits
        shop.add(self.store, "1", 700)
        themes.buy(self.store, "1", "gold", self.bag, self.add_item)
        self.assertEqual(shop.balance(self.store, "1"), 100)
        self.assertEqual(themes.active(self.store, "1"), "gold")                # gleich aktiv
        with self.assertRaises(themes.ThemeError):
            themes.buy(self.store, "1", "gold", self.bag, self.add_item)        # schon gekauft
        themes.use(self.store, "1", "classic")
        self.assertEqual(themes.active(self.store, "1"), "classic")
        with self.assertRaises(themes.ThemeError):
            themes.use(self.store, "1", "night")                                 # nicht gekauft

    def test_halloween_costs_ten_candies(self):
        shop.add(self.store, "1", 10000)                                         # Bits helfen nicht
        self.bag = {"candy": 9}
        with self.assertRaises(themes.ThemeError):
            themes.buy(self.store, "1", "halloween", self.bag, self.add_item, event="halloween")
        self.bag["candy"] = 12
        themes.buy(self.store, "1", "halloween", self.bag, self.add_item, event="halloween")
        self.assertEqual(self.bag["candy"], 2)
        self.assertEqual(shop.balance(self.store, "1"), 10000)
        self.assertEqual(themes.active(self.store, "1"), "halloween")

    def test_halloween_only_visible_during_event(self):
        keys = lambda owner, event=None: [t["key"] for t in themes.catalog(self.store, owner, event)]
        self.assertNotIn("halloween", keys("1"))                                 # außerhalb: unsichtbar
        self.assertIn("halloween", keys("1", "halloween"))
        self.bag = {"candy": 10}
        with self.assertRaises(themes.ThemeError):                               # außerhalb: nicht kaufbar
            themes.buy(self.store, "1", "halloween", self.bag, self.add_item)
        self.assertEqual(self.bag["candy"], 10)
        themes.buy(self.store, "1", "halloween", self.bag, self.add_item, event="halloween")
        self.assertIn("halloween", keys("1"))                                    # gekauft: bleibt sichtbar
        themes.use(self.store, "1", "classic")
        themes.use(self.store, "1", "halloween")                                 # … und benutzbar
        self.assertEqual(themes.active(self.store, "1"), "halloween")

    def test_colors_are_valid(self):
        hex_color = re.compile(r"^#[0-9a-f]{6}$")
        for key, t in themes.THEMES.items():
            self.assertEqual(len(t["device"]), 3, key)
            for c in [*t["device"], t["lcd"], t["pixel"], *themes.UI[key].values()]:
                self.assertRegex(c, hex_color)
            self.assertEqual(set(themes.UI[key]), {"deep", "bg", "panel", "panel2", "line", "accent", "accent2", "muted"})
            self.assertTrue(("price" in t) != ("item" in t), key)               # Bits ODER Item


if __name__ == "__main__":
    unittest.main()
