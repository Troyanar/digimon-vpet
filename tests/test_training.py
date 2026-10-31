"""Tests für die drei Trainingsarten.  Starten mit:  python -m unittest"""
import unittest

from game import cheats
from game import pet as P
from tests.test_battle import rookie


class TrainingTest(unittest.TestCase):
    def test_success_gives_skill_point_and_counts(self):
        p = rookie(strength=0)
        P.train(p, True, p["last"], "speed")
        P.train(p, False, p["last"], "defense")
        self.assertEqual(p["trainings"], 2)                 # beide zählen für die Digitation
        self.assertEqual(p["skills"], {"power": 0, "speed": 1, "defense": 0})
        self.assertEqual(p["strength"], 1)
        with self.assertRaises(P.Refused):
            P.train(p, True, p["last"], "fliegen")

    def test_skill_is_capped(self):
        p = rookie()
        for _ in range(15):
            P.train(p, True, p["last"], "power")
        self.assertEqual(p["skills"]["power"], P.SKILL_CAP)

    def test_style_needs_clear_majority(self):
        p = rookie()
        p["skills"] = {"power": 4, "speed": 0, "defense": 0}
        self.assertIsNone(P.style(p))                       # zu wenig
        p["skills"] = {"power": 5, "speed": 4, "defense": 0}
        self.assertIsNone(P.style(p))                       # nicht klar genug
        p["skills"] = {"power": 6, "speed": 2, "defense": 1}
        self.assertEqual(P.style(p), "power")

    def test_style_steers_evolution(self):
        # Agumon, 0 Pflegefehler. Normal: Greymon ab 16 Trainings, sonst Devimon.
        p = rookie(trainings=8)
        self.assertEqual(P.next_form(p)["name"], "Devimon")
        p["skills"] = {"power": 6, "speed": 0, "defense": 0}         # Kraft -> Feuer
        self.assertEqual(P.next_form(p)["name"], "Greymon")
        p = rookie(trainings=20)
        p["skills"] = {"power": 0, "speed": 7, "defense": 0}         # Tempo -> Dunkel
        self.assertEqual(P.next_form(p)["name"], "Devimon")

    def test_style_cannot_skip_care_rules(self):
        p = rookie(trainings=20)
        p["mistakes"] = 4                                   # zu viele Pflegefehler für Greymon
        p["skills"] = {"power": 8, "speed": 0, "defense": 0}
        self.assertNotIn(P.next_form(p)["name"], ("Greymon", "Devimon"))

    def test_evolution_resets_skills(self):
        p = rookie(trainings=20)
        p["skills"] = {"power": 8, "speed": 1, "defense": 1}
        cheats.apply(p, "evolve_now", {}, p["last"])
        self.assertEqual(p["skills"], {"power": 0, "speed": 0, "defense": 0})

    def test_cheat_sets_skills(self):
        p = rookie()
        cheats.apply(p, "set", {"values": {"speed": 99, "defense": 3}}, p["last"])
        self.assertEqual((p["skills"]["speed"], p["skills"]["defense"]), (P.SKILL_CAP, 3))


if __name__ == "__main__":
    unittest.main()
