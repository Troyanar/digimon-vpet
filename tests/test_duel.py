"""Tests für Kämpfe gegen Freunde.  Starten mit:  python -m unittest"""
import unittest

from game import duel as D
from game import pet as P
from game.store import Store
from tests.test_battle import Always, rookie

T0 = 1_000_000.0       # echte Sekunden


class DuelTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.mario = {"id": 1, "name": "Mario"}
        self.tai = {"id": 2, "name": "Tai"}
        self.pets = {"a": rookie(), "b": rookie()}
        self.pets["a"]["id"], self.pets["b"]["id"] = 11, 22

    def start(self):
        duel = D.challenge(self.store, self.mario, self.tai, self.pets["a"], self.pets["b"], T0)
        D.answer(duel, True, self.pets, T0 + 5)
        return duel

    def play_round(self, duel, rng, a=1.0, b=1.0, dodge=(False, False), now=T0 + 10):
        """Eine ganze Runde: beide schießen, dann (falls nötig) beide ausweichen."""
        D.shoot(duel, "a", a, self.pets, now, rng)
        D.shoot(duel, "b", b, self.pets, now, rng)
        for side, dodged in zip("ab", dodge):
            if duel["status"] == "active" and duel["data"]["phase"] == "dodge" and side not in duel["data"]["dodges"]:
                D.dodge(duel, side, dodged, self.pets, now, rng)

    def test_challenge_and_decline(self):
        duel = D.challenge(self.store, self.mario, self.tai, self.pets["a"], self.pets["b"], T0)
        self.assertEqual(duel["status"], "pending")
        with self.assertRaises(P.Refused):         # schon eine offene Herausforderung
            D.challenge(self.store, self.tai, self.mario, self.pets["b"], self.pets["a"], T0)
        D.answer(duel, False, self.pets, T0 + 3)
        self.assertEqual(duel["status"], "declined")

    def test_cannot_challenge_self_or_sleepy_friend(self):
        with self.assertRaises(P.Refused):
            D.challenge(self.store, self.mario, self.mario, self.pets["a"], self.pets["a"], T0)
        self.pets["b"]["asleep"] = True
        with self.assertRaises(P.Refused) as e:
            D.challenge(self.store, self.mario, self.tai, self.pets["a"], self.pets["b"], T0)
        self.assertIn("Tai", str(e.exception))

    def test_accept_costs_both(self):
        self.start()
        for pet in self.pets.values():
            self.assertEqual((pet["hunger"], pet["strength"]), (3, 3))

    def test_round_waits_for_both_shots(self):
        duel = self.start()
        D.shoot(duel, "a", 1.0, self.pets, T0 + 6, Always(0.0))
        self.assertEqual(duel["data"]["rounds"], [])
        with self.assertRaises(P.Refused):
            D.shoot(duel, "a", 1.0, self.pets, T0 + 6)       # nicht doppelt
        D.shoot(duel, "b", 0.0, self.pets, T0 + 7, Always(0.0))
        self.assertEqual(duel["data"]["phase"], "dodge")     # erst ausweichen, dann zählt die Runde
        self.assertEqual(duel["data"]["rounds"], [])
        D.dodge(duel, "a", False, self.pets, T0 + 8, Always(0.0))
        with self.assertRaises(P.Refused):
            D.dodge(duel, "a", True, self.pets, T0 + 8)      # nicht doppelt
        self.assertEqual(duel["data"]["rounds"], [])
        D.dodge(duel, "b", False, self.pets, T0 + 9, Always(0.0))
        r = duel["data"]["rounds"][0]
        self.assertTrue(r["hit"]["a"] and r["hit"]["b"])     # gleichzeitig beide getroffen
        self.assertEqual(duel["data"]["phase"], "aim")

    def test_full_fight_counts_for_both(self):
        duel = self.start()
        rng = Always(0.0)                                    # alles trifft -> gleichstand -> unentschieden
        while duel["status"] == "active":
            self.play_round(duel, rng)
        self.assertEqual(duel["status"], "done")
        self.assertTrue(duel["data"]["result"]["text"].startswith("Unentschieden"))
        for pet in self.pets.values():
            self.assertEqual(pet["battles_stage"], 1)

    def test_stronger_side_wins_and_loser_can_be_hurt(self):
        duel = self.start()
        duel["data"]["hp"]["b"] = 1
        self.play_round(duel, Always(0.0))
        self.assertEqual(duel["data"]["result"]["winner"], "a")
        self.assertEqual(self.pets["a"]["wins_stage"], 1)
        self.assertTrue(self.pets["b"]["injured"])
        view = D.view(duel, 2, self.pets, T0 + 11)
        self.assertFalse(view["result"]["won"])
        self.assertEqual(view["opponent"], "Mario")

    def test_timeouts(self):
        duel = D.challenge(self.store, self.mario, self.tai, self.pets["a"], self.pets["b"], T0)
        D.tick(duel, self.pets, T0 + D.CHALLENGE_TIMEOUT + 1)
        self.assertEqual(duel["status"], "expired")
        self.store.save_duel(duel)
        duel = self.start()
        D.shoot(duel, "a", 1.0, self.pets, T0 + 6, Always(0.0))
        t = T0 + 5 + D.SHOT_TIMEOUT + 1
        D.tick(duel, self.pets, t, Always(0.0))              # Tai schläft ein: schießt automatisch
        self.assertEqual(duel["data"]["shots"]["b"], {"aim": "high", "charge": 0})
        self.assertEqual(duel["data"]["phase"], "dodge")
        self.assertEqual(duel["data"]["rounds"], [])
        D.dodge(duel, "b", True, self.pets, t + 2, Always(0.0))
        D.tick(duel, self.pets, t + D.DODGE_TIMEOUT - 1, Always(0.0))   # noch Zeit
        self.assertEqual(duel["data"]["rounds"], [])
        D.tick(duel, self.pets, t + D.DODGE_TIMEOUT + 1, Always(0.0))   # Mario weicht nicht aus
        self.assertEqual(len(duel["data"]["rounds"]), 1)
        r = duel["data"]["rounds"][0]
        self.assertEqual(r["dodged"], {"a": False, "b": True})
        self.assertEqual(r["hit"], {"a": False, "b": True})          # Tai ist ausgewichen
        self.assertEqual(duel["data"]["hp"], {"a": 2, "b": 3})
        self.assertEqual(duel["data"]["phase"], "aim")

    def test_phases_and_view(self):
        import json
        duel = self.start()
        view = D.view(duel, 1, self.pets, T0 + 6)
        self.assertEqual((view["phase"], view["my_gauge"], view["opp_gauge"]), ("aim", 0, 0))
        self.assertEqual((view["special_name"], view["opp_special_name"]), ("Baby Flame", "Baby Flame"))
        self.assertIsNone(view["incoming"])
        D.shoot(duel, "a", {"aim": "low", "charge": 1.0}, self.pets, T0 + 6, Always(0.0))
        D.shoot(duel, "b", {"aim": "high", "charge": 2.0}, self.pets, T0 + 7, Always(0.7))   # Mega
        with self.assertRaises(P.Refused):                   # jetzt wird ausgewichen, nicht geschossen
            D.shoot(duel, "a", 1.0, self.pets, T0 + 7)
        mario, tai = D.view(duel, 1, self.pets, T0 + 8), D.view(duel, 2, self.pets, T0 + 8)
        self.assertEqual(mario["phase"], "dodge")
        self.assertEqual(mario["time_left"], D.DODGE_TIMEOUT - 1)
        self.assertEqual(mario["incoming"]["side"], "high")
        self.assertTrue(mario["incoming"]["mega"])
        self.assertEqual(tai["incoming"]["side"], "low")
        self.assertEqual(mario["my_attack"], {"aim": "low", "interrupted": False, "special": False,
                                              "power": True, "mega": False})
        D.dodge(duel, "b", True, self.pets, T0 + 8)
        mario = D.view(duel, 1, self.pets, T0 + 8)
        self.assertEqual((mario["i_dodged"], mario["they_dodged"]), (False, True))
        D.dodge(duel, "a", False, self.pets, T0 + 9)
        mario = D.view(duel, 1, self.pets, T0 + 9)
        self.assertEqual(mario["phase"], "aim")
        self.assertIsNone(mario["my_attack"])
        r = mario["rounds"][0]
        self.assertEqual((r["my_aim"], r["opp_aim"], r["opp_mega"], r["they_dodged"], r["i_dodged"]),
                         ("low", "high", True, True, False))
        self.assertEqual((r["my_hit"], r["opp_hit"], r["my_damage"], r["opp_damage"]), (False, True, 0, 2))
        # gegen Freunde füllen eingesteckte Treffer (Mario) und gelungenes Ausweichen (Tai) die Leiste,
        # ausgeteilte Treffer nicht
        self.assertEqual((r["my_gauge"], r["opp_gauge"], r["my_hp"]), (1, 1, 1))
        json.dumps([mario, D.view(duel, 2, self.pets, T0 + 9)])

    def test_special_cannot_be_dodged_and_interrupted_needs_no_dodge(self):
        duel = self.start()
        with self.assertRaises(P.Refused):                   # Leiste noch leer
            D.shoot(duel, "a", {"special": True, "mash": 1.0}, self.pets, T0 + 6)
        duel["data"]["gauge"]["a"] = 3
        D.shoot(duel, "a", {"special": True, "mash": 1.0}, self.pets, T0 + 6, Always(0.1))
        D.shoot(duel, "b", {"aim": "low", "charge": 2.0}, self.pets, T0 + 6, Always(0.1))   # unterbrochen
        # niemand muss ausweichen: Spezial ist nicht ausweichbar, auf a fliegt nichts
        r = duel["data"]["rounds"][0]
        self.assertEqual(duel["data"]["phase"], "aim")
        self.assertEqual(r["special"], {"a": True, "b": False})
        self.assertEqual(r["interrupted"], {"a": False, "b": True})
        self.assertEqual(r["damage"], {"a": 2, "b": 0})
        self.assertEqual(duel["data"]["hp"], {"a": 3, "b": 1})
        self.assertEqual(duel["data"]["gauge"], {"a": 0, "b": 1})

    def test_gauge_fills_by_taking_hits_and_dodging_not_by_dealing(self):
        duel = self.start()
        D.shoot(duel, "a", {"aim": "low", "charge": 1.0}, self.pets, T0 + 6, Always(0.0))
        D.shoot(duel, "b", {"aim": "high", "charge": 1.0}, self.pets, T0 + 6, Always(0.0))
        D.dodge(duel, "a", False, self.pets, T0 + 7)
        D.dodge(duel, "b", False, self.pets, T0 + 7)
        self.assertEqual(duel["data"]["gauge"], {"a": 1, "b": 1})     # nur eingesteckt, nicht ausgeteilt
        D.shoot(duel, "a", {"aim": "low", "charge": 1.0}, self.pets, T0 + 8, Always(0.0))
        D.shoot(duel, "b", {"aim": "high", "charge": 1.0}, self.pets, T0 + 8, Always(0.0))
        D.dodge(duel, "a", True, self.pets, T0 + 9)                     # a weicht aus: +1
        D.dodge(duel, "b", False, self.pets, T0 + 9)                    # b getroffen: +1
        self.assertEqual(duel["data"]["gauge"], {"a": 2, "b": 2})
        self.assertEqual(duel["data"]["hp"], {"a": 2, "b": 1})

    def test_old_saved_duel_still_runs(self):
        duel = self.start()
        duel["data"].pop("phase")
        duel["data"].pop("gauge")
        duel["data"]["shots"] = {"a": 1.0}                    # alte Form: Zahl
        duel["data"]["rounds"] = [{"hit": {"a": True, "b": False}, "power": {"a": True, "b": False},
                                   "hp": {"a": 3, "b": 2}}]
        self.assertEqual(D.view(duel, 1, self.pets, T0 + 6)["rounds"][0]["my_damage"], 1)
        D.shoot(duel, "b", 1.0, self.pets, T0 + 6, Always(0.0))
        self.assertEqual(duel["data"]["phase"], "dodge")

    def test_forfeit_is_a_loss(self):
        duel = self.start()
        D.forfeit(duel, "b", self.pets, T0 + 8, Always(0.99))
        self.assertEqual(duel["data"]["result"]["winner"], "a")
        self.assertEqual(self.pets["b"]["battles"], 1)
        self.assertEqual(self.pets["b"]["wins"], 0)

    def test_swapped_pet_aborts(self):
        duel = self.start()
        self.pets["b"]["id"] = 99
        D.shoot(duel, "a", 1.0, self.pets, T0 + 6)
        D.shoot(duel, "b", 1.0, self.pets, T0 + 6)
        self.assertEqual(duel["status"], "aborted")


if __name__ == "__main__":
    unittest.main()
