"""Tests für Tauschen und Jogress.  Starten mit:  python -m unittest"""
import copy
import unittest

from game import cheats, collection, data, social, progress
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
        self.store.add_pet("1", blitz)
        self.store.add_pet("2", cres)
        blitz["name"], cres["name"] = "Blitz", "Cres"
        born = (blitz["born"], cres["born"])
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        self.assertTrue(social.jogress_view(self.store, self.tai, T0 + 1)["incoming"])
        msg = social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres}, T0 + 2)
        self.assertIn("Omnimon", msg)
        self.assertEqual(P.display_name(blitz), "Omnimon Alter-S")
        self.assertEqual(P.display_name(cres), "Omnimon Alter-S")
        self.assertEqual((blitz["name"], cres["name"]), ("Blitz", "Cres"))
        self.assertEqual((blitz["born"], cres["born"]), born)
        self.assertEqual(self.store.active_pet("2")["dex"], to)
        self.assertEqual(self.store.active_pet("1")["dex"], to)
        with self.assertRaises(P.Refused):
            social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres}, T0 + 3)

    def test_friend_becomes_unready_neither_changes(self):
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        self.store.add_pet("1", blitz)
        self.store.add_pet("2", cres)
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        cres["sick"] = True
        before = copy.deepcopy((blitz, cres))
        with self.assertRaises(P.Refused):
            social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres}, T0 + 2)
        self.assertEqual((blitz, cres), before)
        self.assertEqual(self.store.active_pet("1")["dex"], find_dex("BlitzGreymon"))

    def test_friend_save_failure_rolls_back_both_and_request(self):
        from unittest.mock import patch
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        self.store.add_pet("1", blitz)
        self.store.add_pet("2", cres)
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        before = copy.deepcopy((blitz, cres))
        with patch.object(self.store, "finish_jogress", side_effect=ValueError("save failed")):
            with self.assertRaises(ValueError):
                social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres}, T0 + 2)
        self.assertEqual((blitz, cres), before)
        self.assertEqual(social.jogress_view(self.store, self.tai, T0 + 3)["status"], "pending")

    def test_old_friend_request_needs_new_consent(self):
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        self.store.add_pet("1", blitz)
        self.store.add_pet("2", cres)
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        req = self.store.requests_for(1, "jogress", ("pending",))[0]
        req["data"].pop("fusion_rule")
        self.store.save_request(req)
        with self.assertRaises(P.Refused):
            social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres}, T0 + 2)
        self.assertEqual(P.display_name(blitz), "BlitzGreymon")

    def test_jogress_request_expires(self):
        blitz, cres = become("ver1", find_dex("BlitzGreymon")), become("ver2", find_dex("CresGarurumon"))
        blitz["id"], cres["id"] = 101, 202
        to = P.jogress_options(blitz)[0][0]["to"]
        social.jogress_ask(self.store, self.mario, self.tai, blitz, to, cres, T0)
        with self.assertRaises(P.Refused):
            social.jogress_answer(self.store, self.tai, True, {"a": blitz, "b": cres},
                                  T0 + social.JOGRESS_TIMEOUT + 1)


class SoloFusionTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.me = {"id": 1, "name": "Tester"}
        self.active = become("ver1", find_dex("WarGreymon"))
        self.partner = become("ver2", find_dex("MetalGarurumon"))
        self.active.update(name="Feuer", wins=12, mistakes_total=3)
        self.partner.update(name="Eis", wins=7, mistakes_total=5, in_box=True, box=0)
        self.store.add_pet("1", self.active)
        self.store.add_pet("1", self.partner, active=False)
        self.now = self.active["last"]
        self.to = find_dex("Omnimon")

    def tearDown(self):
        self.store.db.close()

    def fuse(self, basis=None):
        return social.jogress_box(self.store, self.me, self.to, self.partner["id"],
                                 self.active["id"] if basis is None else basis, self.now)

    def test_two_become_one_active_basis_and_digidex_survives(self):
        self.fuse()
        result = self.store.active_pet("1")
        self.assertEqual(len(self.store.all_pets("1")), 1)
        self.assertEqual(result["id"], self.active["id"])
        self.assertEqual(result["dex"], self.to)
        self.assertEqual(result["name"], "Feuer")
        self.assertEqual(result["born"], self.active["born"])
        self.assertEqual(result["wins"], 12)
        self.assertEqual(result["mistakes_total"], 3)
        self.assertEqual(result["skills"], {"power": 0, "speed": 0, "defense": 0})
        self.assertTrue(any(e in result["log"] for e in self.active["log"]))
        self.assertIn(self.partner["dex"], progress.owned(self.store, "1"))
        self.assertEqual(progress.stats(self.store, "1")["wins"], 19)

    def test_collection_basis_keeps_age_and_becomes_active(self):
        self.partner["born"] -= 1440
        self.store.save_pet(self.partner)
        age = self.partner["last"] - self.partner["born"]
        self.fuse(self.partner["id"])
        result = self.store.active_pet("1")
        self.assertEqual(result["id"], self.partner["id"])
        self.assertEqual(result["last"] - result["born"], age)
        self.assertEqual(result["name"], "Eis")
        self.assertEqual(result["wins"], 7)
        self.assertFalse(result.get("in_box"))
        self.assertIsNone(self.store.pet_by_id(self.active["id"]))
        self.assertEqual(len(self.store.all_pets("1")), 1)

    def test_invalid_partner_basis_recipe_and_repeat_do_not_consume(self):
        with self.assertRaises(P.Refused):
            self.fuse(999)
        self.to = find_dex("Agumon")
        with self.assertRaises(P.Refused):
            self.fuse()
        self.assertEqual(len(self.store.all_pets("1")), 2)
        self.to = find_dex("Omnimon")
        self.fuse()
        with self.assertRaises(P.Refused):
            self.fuse()
        self.assertEqual(len(self.store.all_pets("1")), 1)

    def test_unavailable_or_traded_partner_cannot_be_consumed(self):
        for change in ({"sick": True}, {"frozen": True}, {"box_trip": {"area": "wald", "end": self.now + 30}}):
            partner = copy.deepcopy(self.partner)
            partner.update(change)
            self.store.save_pet(partner)
            with self.assertRaises(P.Refused):
                self.fuse()
            self.assertEqual(self.store.active_pet("1")["dex"], self.active["dex"])
            self.assertEqual(len(self.store.all_pets("1")), 2)
        self.store.save_pet(self.partner)
        social.offer(self.store, self.me, {"id": 2, "name": "Other"}, self.partner["id"], True)
        with self.assertRaises(P.Refused):
            self.fuse()
        self.assertEqual(len(self.store.all_pets("1")), 2)

    def test_transaction_failure_restores_consumed_partner(self):
        invalid = copy.deepcopy(self.active)
        invalid["invalid"] = object()
        with self.assertRaises(TypeError):
            self.store.finish_jogress([invalid], owner="1", consumed=self.partner["id"], active=invalid["id"])
        self.assertIsNotNone(self.store.pet_by_id(self.partner["id"]))
        self.assertEqual(self.store.active_pet("1")["dex"], self.active["dex"])


if __name__ == "__main__":
    unittest.main()
