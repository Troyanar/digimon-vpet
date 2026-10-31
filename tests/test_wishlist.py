"""Tests für die Merkliste.  Starten mit:  python -m unittest"""
import unittest

from game import data, wishlist
from game.store import Store


def find(name):
    return next(d for d, v in data.PLAYABLE.items() if v["name"] == name)


class WishlistTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")

    def test_add_remove_per_account(self):
        greymon, garurumon = find("Greymon"), find("Garurumon")
        self.assertEqual(wishlist.toggle(self.store, "1", greymon, True), [greymon])
        self.assertEqual(wishlist.toggle(self.store, "1", greymon, True), [greymon])      # nicht doppelt
        wishlist.toggle(self.store, "1", garurumon, True)
        self.assertEqual(wishlist.get(self.store, "2"), [])                               # anderes Konto
        self.assertEqual(wishlist.toggle(self.store, "1", greymon, False), [garurumon])

    def test_unknown_digimon_and_limit(self):
        with self.assertRaises(ValueError):
            wishlist.toggle(self.store, "1", 999999, True)
        for dex in list(data.PLAYABLE)[:wishlist.MAX]:
            wishlist.toggle(self.store, "1", dex, True)
        with self.assertRaises(ValueError):
            wishlist.toggle(self.store, "1", list(data.PLAYABLE)[wishlist.MAX], True)

    def test_merged_numbers_are_mapped(self):
        if not data.ALIASES:
            self.skipTest("keine zusammengelegten Digimon")
        old, new = next(iter(data.ALIASES.items()))
        self.store.set_meta("wishlist:1", [old])
        self.assertEqual(wishlist.get(self.store, "1"), [new])


if __name__ == "__main__":
    unittest.main()
