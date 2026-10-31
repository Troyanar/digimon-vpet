"""Tests für das Cheat-Menü.  Starten mit:  python -m unittest"""
import unittest

from game import cheats, data
from game import pet as P
from tests.test_pet import MORNING, run


def hatched(line="ver1"):
    p = P.new_egg(line, MORNING)
    run(p, MORNING, 20, every=1)          # -> Koromon
    return p


class CheatTest(unittest.TestCase):
    def test_warp_moves_time_forward(self):
        p = hatched()
        now = p["last"]
        hunger = p["hunger"]
        cheats.apply(p, "warp", {"minutes": 120}, now)
        self.assertLess(p["hunger"], hunger)          # 2 h ohne Futter
        self.assertEqual(p["last"], now)              # Uhr bleibt in der Gegenwart
        self.assertTrue(p["cheated"])

    def test_evolve_now_uses_rules(self):
        p = hatched()
        now = p["last"]
        cheats.apply(p, "evolve_now", {}, now)
        self.assertEqual(P.display_name(p), "Agumon")         # 0 Pflegefehler
        cheats.apply(p, "set", {"values": {"mistakes": 0, "trainings": 20}}, now)
        cheats.apply(p, "evolve_now", {}, now)
        self.assertEqual(P.display_name(p), "Greymon")
        with self.assertRaises(P.Refused):                     # Ultra braucht Siege
            cheats.apply(p, "evolve_now", {}, now)
        cheats.apply(p, "set", {"values": {"battles_stage": 15, "wins_stage": 12}}, now)
        cheats.apply(p, "evolve_now", {}, now)
        self.assertEqual(P.display_name(p), "MetalGreymon")

    def test_egg_hatches_now(self):
        p = P.new_egg("ver2", MORNING)
        cheats.apply(p, "evolve_now", {}, MORNING)
        self.assertEqual(P.display_name(p), "Punimon")

    def test_set_is_clamped(self):
        p = hatched()
        cheats.apply(p, "set", {"values": {"hunger": 99, "strength": -5, "mistakes": 3}}, p["last"])
        self.assertEqual((p["hunger"], p["strength"]), (4, 0))
        self.assertGreaterEqual(p["mistakes_total"], 3)
        with self.assertRaises(P.Refused):
            cheats.apply(p, "set", {"values": {"hunger": "viel"}}, p["last"])

    def test_become_any_digimon(self):
        p = hatched()
        beelzemon = 310
        cheats.apply(p, "become", {"line": "impmon", "dex": beelzemon}, p["last"])
        self.assertEqual((P.display_name(p), p["stage"], p["line"]), ("Beelzemon", "Mega", "impmon"))
        with self.assertRaises(P.Refused):
            cheats.apply(p, "become", {"line": "ver1", "dex": beelzemon}, p["last"])

    def test_immortal_and_revive(self):
        p = hatched()
        cheats.apply(p, "flags", {"immortal": True}, p["last"])
        P.advance(p, p["last"] + 3 * 24 * 60)
        self.assertTrue(p["alive"])
        cheats.apply(p, "flags", {"immortal": False}, p["last"])
        P.advance(p, p["last"] + 24 * 60)
        self.assertFalse(p["alive"])
        cheats.apply(p, "revive", {}, p["last"])
        self.assertTrue(p["alive"])
        P.advance(p, p["last"] + 5)
        self.assertTrue(p["alive"])

    def test_no_sleep(self):
        p = hatched()
        run(p, p["last"], 12 * 60 + 30, every=5)     # abends -> schläft
        self.assertTrue(p["asleep"])
        cheats.apply(p, "flags", {"no_sleep": True}, p["last"])
        P.advance(p, p["last"] + 5)
        self.assertFalse(p["asleep"])

    def test_status(self):
        p = hatched()
        for what in ("sick", "injured", "poop"):
            cheats.apply(p, "status", {"what": what}, p["last"])
        self.assertTrue(p["sick"] and p["injured"] and p["poop"] >= 1)
        cheats.apply(p, "status", {"what": "heal"}, p["last"])
        self.assertFalse(p["sick"] or p["injured"])


if __name__ == "__main__":
    unittest.main()
