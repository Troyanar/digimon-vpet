"""Tests für Tauschen und Jogress.  Starten mit:  python -m unittest"""
import unittest

from game import cheats, collection, data, social
from game import pet as P
from game.store import Store
from tests.test_battle import rookie

T0 = 1_000_000.0


def become(line, dex):
    p = rookie()
    cheats.apply(p, "become", {"line": line, "dex": dex}, p["last"])
    p["hunger"] = p["strength"] = 4
    return p


def find_dex(name):
    return next(d for d, v in data.PLAYABLE.items() if v["name"] == name)


class JogressTest(unittest.TestCase):
    def test_named_partner(self):
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        options = P.jogress_options(blitz)
        self.assertEqual([data.DIGIMON[e["to"]]["name"] for e, _ in options], ["Omnimon Alter-S"])
        need = options[0][1]
        self.assertTrue(P.partner_fits(need, blitz, cres))
        self.assertFalse(P.partner_fits(need, blitz, become("ver1", find_dex("BlitzGreymon"))))
        msg = P.jogress(blitz, options[0][0]["to"], cres, "Tai", blitz["last"])
        self.assertIn("Omnimon Alter-S", msg)
        self.assertEqual(P.display_name(blitz), "Omnimon Alter-S")
        self.assertEqual(P.display_name(cres), "CresGarurumon")     # Partner bleibt

    def test_attribute_partner_needs_same_stage(self):
        evo = next(e for e in data.EVOLUTIONS if isinstance(e["rule"].get("jogress"), str)
                   and e["rule"]["jogress"] == "Virus" and data.DIGIMON[e["from"]]["stage"] == "Champion")
        me = become(evo["line"], evo["from"])
        virus_champ = next(d for d, v in data.PLAYABLE.items() if v["stage"] == "Champion" and v["attribute"] == "Virus")
        virus_rookie = next(d for d, v in data.PLAYABLE.items() if v["stage"] == "Rookie" and v["attribute"] == "Virus")
        line_of = lambda dex: next(e["line"] for e in data.EVOLUTIONS if e["to"] == dex)
        self.assertTrue(P.partner_fits("Virus", me, become(line_of(virus_champ), virus_champ)))
        self.assertFalse(P.partner_fits("Virus", me, become(line_of(virus_rookie), virus_rookie)))

    def test_no_jogress_for_normal_digimon(self):
        self.assertEqual(P.jogress_options(rookie()), [])


class SocialTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.mario, self.tai = {"id": 1, "name": "Mario"}, {"id": 2, "name": "Tai"}
        for u in (self.mario, self.tai):
            self.store.add_pet(str(u["id"]), rookie())           # aktiv

    def boxed(self, user, line="ver1"):
        collection.store_egg(self.store, str(user["id"]), line, 0)
        return collection.boxed(self.store, str(user["id"]))[0]

    def test_trade_with_counter_offer(self):
        egg_m, egg_t = self.boxed(self.mario, "ver1"), self.boxed(self.tai, "ver2")
        social.offer(self.store, self.mario, self.tai, egg_m["id"], gift=False)
        req = social.trades_view(self.store, self.tai)[0]
        self.assertEqual(req["todo"], "answer")
        with self.assertRaises(P.Refused):
            social.accept_gift(self.store, self.tai, req["id"])       # kein Geschenk
        social.counter(self.store, self.tai, req["id"], egg_t["id"])
        self.assertEqual(social.trades_view(self.store, self.mario)[0]["todo"], "confirm")
        social.confirm(self.store, self.mario, req["id"])
        self.assertEqual(self.store.pet_by_id(egg_m["id"])["owner"], "2")
        self.assertEqual(self.store.pet_by_id(egg_t["id"])["owner"], "1")
        self.assertEqual(social.trades_view(self.store, self.mario), [])

    def test_gift(self):
        egg = self.boxed(self.mario)
        social.offer(self.store, self.mario, self.tai, egg["id"], gift=True)
        req = social.trades_view(self.store, self.tai)[0]
        social.accept_gift(self.store, self.tai, req["id"])
        self.assertEqual(self.store.pet_by_id(egg["id"])["owner"], "2")
        self.assertTrue(self.store.pet_by_id(egg["id"])["in_box"])

    def test_only_box_items_and_not_twice(self):
        active = self.store.active_pet("1")
        with self.assertRaises(P.Refused):
            social.offer(self.store, self.mario, self.tai, active["id"], gift=True)
        egg = self.boxed(self.mario)
        social.offer(self.store, self.mario, self.tai, egg["id"], gift=True)
        with self.assertRaises(P.Refused):
            social.offer(self.store, self.mario, self.tai, egg["id"], gift=True)

    def test_trade_fails_if_item_left_the_box(self):
        egg_m, egg_t = self.boxed(self.mario), self.boxed(self.tai)
        social.offer(self.store, self.mario, self.tai, egg_m["id"], gift=False)
        req = social.trades_view(self.store, self.tai)[0]
        social.counter(self.store, self.tai, req["id"], egg_t["id"])
        collection.switch(self.store, "2", egg_t["id"], 10)          # Tai brütet es doch selbst aus
        with self.assertRaises(P.Refused):
            social.confirm(self.store, self.mario, req["id"])
        self.assertEqual(self.store.pet_by_id(egg_m["id"])["owner"], "1")

    def test_decline_and_cancel(self):
        egg = self.boxed(self.mario)
        social.offer(self.store, self.mario, self.tai, egg["id"], gift=False)
        req = social.trades_view(self.store, self.tai)[0]
        social.decline(self.store, self.tai, req["id"])
        self.assertEqual(social.trades_view(self.store, self.mario), [])

    def test_jogress_with_friend(self):
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        blitz["id"], cres["id"] = 101, 202
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        self.assertTrue(social.jogress_view(self.store, self.tai, T0 + 1)["incoming"])
        msg = social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres}, T0 + 2)
        self.assertIn("Omnimon", msg)
        self.assertEqual(P.display_name(cres), "CresGarurumon")

    def test_jogress_request_expires(self):
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        blitz["id"], cres["id"] = 101, 202
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        with self.assertRaises(P.Refused):
            social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres},
                                  T0 + social.JOGRESS_TIMEOUT + 1)


if __name__ == "__main__":
    unittest.main()
