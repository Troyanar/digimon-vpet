"""Tests für die Rückkehr-Bestätigung nach dem Erkunden und Ziele pro Digimon.
Starten mit:  python -m unittest"""
import unittest

from game import data, explore, wishlist
from game import pet as P
from game.store import Store
from tests.test_battle import Always, rookie


def named(name):
    return next(dex for dex in data.PLAYABLE if data.DIGIMON[dex]["name"] == name)


class ReturnTest(unittest.TestCase):
    def back_home(self):
        p = rookie()
        now = p["last"]
        explore.start(p, "wald", 30, now)
        P.advance(p, now + 30)
        return p, now + 30

    def test_waits_for_ok(self):
        p, back = self.back_home()
        self.assertTrue(p["returned"])
        hunger, since = p["hunger"], p["stage_since"]
        P.advance(p, back + 600)                        # 10 Stunden niemand da
        self.assertEqual(p["hunger"], hunger)           # kein Hunger …
        self.assertEqual(p["mistakes"], 0)              # … keine Pflegefehler
        self.assertEqual(p["stage_since"], since + 600)  # Digitations-Uhr hält auch an
        with self.assertRaises(P.Refused):
            P.feed(p, "meat", back + 600)               # erst OK drücken
        P.confirm_return(p, back + 600)
        self.assertNotIn("returned", p)
        P.feed(p, "meat", back + 600)
        P.advance(p, back + 900)
        self.assertLess(p["hunger"], 4)                 # ab jetzt läuft die Zeit wieder

    def test_report_stays_until_ok(self):
        p, back = self.back_home()
        report = explore.claim(p, back, lambda line: True, lambda item: None, Always(0.99))
        self.assertEqual(p["returned"]["text"], str(report["text"]))
        self.assertIn("zurück", str(P.view(p, back)["returned"]))
        with self.assertRaises(P.Refused):
            P.confirm_return(rookie(), back)              # war gar nicht weg


class GoalTest(unittest.TestCase):
    def test_goal_per_digimon(self):
        store = Store(":memory:")
        p = rookie()
        greymon = named("Greymon")
        wishlist.set_goal(store, "1", p, greymon)
        self.assertEqual(p["goal"], greymon)
        self.assertIn(greymon, wishlist.get(store, "1"))     # kommt automatisch auf die Merkliste
        self.assertEqual(P.view(p, p["last"])["goal"], greymon)
        other = rookie()
        self.assertIsNone(P.view(other, other["last"])["goal"])   # anderes Digimon: kein Ziel
        wishlist.set_goal(store, "1", p, None)
        self.assertNotIn("goal", p)
        with self.assertRaises(ValueError):
            wishlist.set_goal(store, "1", p, 999999)


if __name__ == "__main__":
    unittest.main()
