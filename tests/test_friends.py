"""Tests für Freundescodes und dafür, dass Freunde keine Details sehen.  Starten mit:  python -m unittest"""
import unittest

from game import duel as D
from game import friends
from game import pet as P
from game.store import Store
from tests.test_battle import rookie

T0 = 1_000_000.0


class FriendCodeTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.users = [{"id": self.store.add_user(n, "x", "y", False), "name": n} for n in ("Mario", "Tai", "Sora")]
        self.mario, self.tai, self.sora = self.users

    def test_each_account_has_own_code(self):
        codes = {friends.code(self.store, u["id"]) for u in self.users}
        self.assertEqual(len(codes), 3)
        self.assertEqual(friends.code(self.store, self.mario["id"]), friends.code(self.store, self.mario["id"]))
        self.assertRegex(friends.code(self.store, self.mario["id"]), r"^[A-Z2-9]{4}-[A-Z2-9]{4}$")

    def test_add_is_mutual_and_code_input_is_forgiving(self):
        code = friends.code(self.store, self.tai["id"]).lower().replace("-", " ")   # tippfaul eingegeben
        friends.add(self.store, self.mario, code)
        self.assertTrue(friends.are_friends(self.store, self.mario["id"], self.tai["id"]))
        self.assertTrue(friends.are_friends(self.store, self.tai["id"], self.mario["id"]))
        self.assertFalse(friends.are_friends(self.store, self.mario["id"], self.sora["id"]))
        self.assertEqual([u["name"] for u in friends.users(self.store, self.tai["id"])], ["Mario"])

    def test_errors(self):
        for code in ("", "ABCD-EFGH", friends.code(self.store, self.mario["id"])):
            with self.assertRaises(P.Refused):
                friends.add(self.store, self.mario, code)
        friends.add(self.store, self.mario, friends.code(self.store, self.tai["id"]))
        with self.assertRaises(P.Refused):                                       # schon Freunde
            friends.add(self.store, self.tai, friends.code(self.store, self.mario["id"]))
        with self.assertRaises(P.Refused):
            friends.check(self.store, self.mario, self.sora)
        friends.check(self.store, self.mario, self.tai)                          # ok

    def test_remove_and_new_code(self):
        old = friends.code(self.store, self.tai["id"])
        friends.add(self.store, self.mario, old)
        friends.remove(self.store, self.tai, "Mario")
        self.assertFalse(friends.are_friends(self.store, self.mario["id"], self.tai["id"]))
        self.assertFalse(friends.are_friends(self.store, self.tai["id"], self.mario["id"]))
        new = friends.new_code(self.store, self.tai["id"])
        self.assertNotEqual(old, new)
        with self.assertRaises(P.Refused):                                       # alter Code gilt nicht mehr
            friends.add(self.store, self.mario, old)
        friends.add(self.store, self.mario, new)


class PrivacyTest(unittest.TestCase):
    def test_challenge_hides_why_the_friend_cannot_battle(self):
        store = Store(":memory:")
        mario, tai = {"id": 1, "name": "Mario"}, {"id": 2, "name": "Tai"}
        mine, theirs = rookie(), rookie()
        theirs["expedition"] = {"area": "wald", "start": 0, "end": 600, "minutes": 600}
        with self.assertRaises(P.Refused) as e:
            D.challenge(store, mario, tai, mine, theirs, T0)
        self.assertEqual(str(e.exception), "Tai kann gerade nicht kämpfen.")    # keine Uhrzeit, kein Grund

    def test_profile_only_for_friends_and_without_trip_times(self):
        store = Store(":memory:")
        mario, tai, sora = ({"id": store.add_user(n, "x", "y", False), "name": n} for n in ("Mario", "Tai", "Sora"))
        partner = store.add_pet(str(tai["id"]), rookie())
        partner["name"] = "Flammi"
        store.save_pet(partner)
        away = rookie()
        away.update(in_box=True, box=0, expedition={"area": "wald", "start": 0, "end": 600, "minutes": 600})
        store.add_pet(str(tai["id"]), away, active=False)
        egg = P.new_egg("ver2", 0)
        egg["in_box"] = True
        store.add_pet(str(tai["id"]), egg, active=False)
        with self.assertRaises(P.Refused):                                       # Fremde sehen nichts
            friends.profile(store, sora, "Tai")
        friends.add(store, mario, friends.code(store, tai["id"]))
        view = friends.profile(store, mario, "Tai")
        self.assertEqual((view["partner"]["name"], view["partner"]["nickname"]), ("Agumon", "Flammi"))
        self.assertEqual([p["name"] for p in view["box"]], ["Agumon"])
        self.assertEqual([p["name"] for p in view["eggs"]], ["Digi-Ei"])         # Sorte bleibt geheim
        self.assertIsNone(view["eggs"][0]["dex"])
        self.assertGreaterEqual(view["dex"], 1)
        text = repr(view)
        for secret in ("expedition", "trip", "wald", "600", "hunger", "strength"):
            self.assertNotIn(secret, text)


if __name__ == "__main__":
    unittest.main()
