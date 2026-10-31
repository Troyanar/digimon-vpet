"""Tests fürs Erkunden, den Rucksack und Gratis-Eier.  Starten mit:  python -m unittest"""
import unittest

from game import battle, cheats, collection, data, explore
from game import pet as P
from game.store import Store
from tests.test_battle import Always, rookie
from tests.test_pet import MORNING, run


class AreaTest(unittest.TestCase):
    def test_every_line_has_an_area(self):
        self.assertEqual(set(explore.LINE_AREA), set(data.NORMAL_LINES))   # Event-Eier gehören nirgends hin
        for area in explore.AREAS:
            self.assertTrue(explore.area_lines(area), f"{area} hat keine Eier")
        self.assertEqual(explore.LINE_AREA["gomamon"], "kueste")
        self.assertEqual(explore.LINE_AREA["impmon"], "dunkel")

    def test_areas_are_locked_by_stage(self):
        p = rookie()
        self.assertTrue(explore.unlocked(p, "wald"))
        self.assertFalse(explore.unlocked(p, "stadt"))
        with self.assertRaises(P.Refused):
            explore.start(p, "vulkan", 30, p["last"])


class ExpeditionTest(unittest.TestCase):
    def test_trip_costs_food_and_pauses_needs(self):
        p = rookie()
        now = p["last"]
        explore.start(p, "wald", 120, now)
        self.assertEqual(p["hunger"], 3)
        with self.assertRaises(P.Refused):
            P.feed(p, "meat", now)                     # ist ja weg
        P.advance(p, now + 119)
        self.assertEqual(p["hunger"], 3)               # kein Hunger unterwegs
        self.assertIn("expedition", p)
        P.advance(p, now + 121)
        self.assertNotIn("expedition", p)
        self.assertIn("expedition_return", p)

    def test_claim_hands_out_findings_once(self):
        p = rookie()
        now = p["last"]
        explore.start(p, "kueste", 480, now)
        P.advance(p, now + 480)
        eggs, items = [], []
        report = explore.claim(p, now + 480, lambda line: eggs.append(line) or True,
                               items.append, Always(0.0))
        self.assertEqual(report["shards"], 6)          # 0.0 < Scherben-Chance bei allen 6 Versuchen
        self.assertEqual((eggs, items), ([], ["shard_kueste"] * 6))   # keine ganzen Eier mehr, nur Scherben
        self.assertIn("6× Ei-Scherbe Küste", report["text"])
        self.assertTrue(report["encounter"])
        self.assertEqual(data.DIGIMON[p["scout"]["dex"]]["stage"], "Rookie")
        self.assertIsNone(explore.claim(p, now + 480, lambda l: True, items.append))

    def test_wild_digimon_from_trip_can_be_fought_after_ok(self):
        # Bug: das mitgekommene wilde Digimon wartete schon, bevor die Rückkehr bestätigt war –
        # Kämpfen ging nicht, nur Fliehen. Jetzt: erst OK (Meldung nennt den Gegner), dann kämpfen.
        p = rookie()
        now = p["last"]
        explore.start(p, "wald", 30, now)
        P.advance(p, now + 30)
        explore.claim(p, now + 30, lambda l: True, lambda i: None, Always(0.0))
        name = data.DIGIMON[p["scout"]["dex"]]["name"]
        P.advance(p, now + 200)                        # lange nicht reingeschaut: der Gegner wartet trotzdem
        text = P.confirm_return(p, now + 200)
        self.assertIn(f"Ein wildes {name} ist mitgekommen", text)
        self.assertIn(name, text.en)
        P.advance(p, now + 205)
        self.assertIn("Kampf gegen", battle.fight(p, now + 205))
        self.assertIn("battle", p)

    def test_bad_luck(self):
        p = rookie()
        explore.start(p, "wald", 30, p["last"])
        P.advance(p, p["last"] + 30)
        report = explore.claim(p, p["last"], lambda l: True, lambda i: None, Always(0.99))
        self.assertEqual((report["eggs"], report["items"], report["encounter"]), (0, [], False))

    def test_warp_cheat_finishes_trip(self):
        p = rookie()
        explore.start(p, "wald", 480, p["last"])
        cheats.apply(p, "warp", {"minutes": 480}, p["last"])
        self.assertNotIn("expedition", p)
        self.assertIn("expedition_return", p)

    def test_recall_gives_nothing(self):
        p = rookie()
        explore.start(p, "wald", 480, p["last"])
        explore.recall(p, p["last"] + 10)
        self.assertNotIn("expedition", p)
        self.assertNotIn("expedition_return", p)
        P.feed(p, "meat", p["last"])                   # wieder da

    def test_cannot_box_or_freeze_while_away(self):
        p = rookie()
        explore.start(p, "wald", 30, p["last"])
        with self.assertRaises(P.Refused):
            P.set_frozen(p, True, p["last"])


class ItemTest(unittest.TestCase):
    def test_items(self):
        p = rookie(strength=0)
        p["hunger"] = 0
        explore.use_item(p, "snack", p["last"])
        self.assertEqual((p["hunger"], p["strength"]), (4, 4))
        explore.use_item(p, "weight", p["last"])
        self.assertEqual(p["trainings"], 2)

    def test_charm_boosts_one_battle(self):
        p = rookie()
        normal = battle.power(p)
        explore.use_item(p, "charm", p["last"])
        self.assertGreater(battle.power(p), normal)
        with self.assertRaises(P.Refused):
            explore.use_item(p, "charm", p["last"])    # nur einer gleichzeitig
        from tests.test_battle import battle_once
        battle_once(p, 1.0, Always(0.0))
        self.assertNotIn("charm", p)


class VirusDiskTest(unittest.TestCase):
    def test_adds_a_mistake_but_never_a_deadly_one(self):
        p = rookie()
        p["stage"] = "Rookie"
        explore.use_item(p, "virus", p["last"])
        self.assertEqual((p["mistakes"], p["mistakes_total"]), (1, 1))
        p["mistakes_total"] = P.MAX_MISTAKES - 2
        explore.use_item(p, "virus", p["last"])                 # 19 von 20: geht noch
        self.assertEqual(p["mistakes_total"], P.MAX_MISTAKES - 1)
        with self.assertRaises(P.Refused):                       # der 20. wäre tödlich
            explore.use_item(p, "virus", p["last"])
        P.advance(p, p["last"] + 1)
        self.assertTrue(p["alive"])
        with self.assertRaises(P.Refused):
            explore.use_item(P.new_egg("ver1", 0), "virus", 0)   # ein Ei hat keine Pflegefehler

    def test_counts_for_digivolution(self):
        # Digitationen mit Pflegefehler-Bedingung ("cm") sehen die Fehler der Diskette
        p = rookie()
        before = p["mistakes"]
        explore.use_item(p, "virus", p["last"])
        self.assertEqual(p["mistakes"], before + 1)


class ShardTest(unittest.TestCase):
    def setUp(self):
        self.store, self.owner = Store(":memory:"), "1"
        self.bag = {"shard_wald": 3}

    def take(self, n):
        self.bag["shard_wald"] -= n

    def combine(self):
        return collection.combine_shards(self.store, self.owner, "shard_wald", self.bag["shard_wald"], self.take, 0)

    def test_four_shards_make_an_egg_from_that_area(self):
        with self.assertRaises(P.Refused):                       # 3 reichen nicht
            self.combine()
        self.bag["shard_wald"] = 5
        self.assertIn("Digi-Ei aus Urwald", self.combine())
        self.assertEqual(self.bag["shard_wald"], 1)
        eggs = collection.boxed(self.store, self.owner)
        self.assertEqual(len(eggs), 1)
        self.assertEqual(eggs[0]["stage"], "Egg")
        self.assertEqual(explore.LINE_AREA[eggs[0]["line"]], "wald")

    def test_full_collection_keeps_the_shards(self):
        self.bag["shard_wald"] = 4
        for _ in range(collection.BOX_SIZE):
            collection.store_egg(self.store, self.owner, "ver1", 0)
        with self.assertRaises(P.Refused):
            self.combine()
        self.assertEqual(self.bag["shard_wald"], 4)

    def test_shards_cannot_be_used_on_the_digimon_but_sold(self):
        from game import shop
        with self.assertRaises(P.Refused):
            explore.use_item(rookie(), "shard_wald", 0)
        self.assertEqual(shop.sell_price("shard_wald"), 15)
        self.assertNotIn("shard_wald", shop.PRICES)              # nicht im Shop
        self.assertNotIn("shard_wald", explore.ITEM_ODDS)        # kommt nur als Scherben-Fund

    def test_box_trips_bring_shards(self):
        p = rookie()
        p.update(in_box=True, box=0)
        pet = self.store.add_pet(self.owner, p, active=False)
        collection.send(self.store, self.owner, pet["id"], "wald", 480, 0)
        items = []
        collection.claim_trips(self.store, self.owner, 480, items.append, Always(0.0))
        self.assertEqual(items, ["shard_wald"] * 6)


class TotemTest(unittest.TestCase):
    def starve(self, p, minutes=3 * 24 * 60):
        p["hunger"] = 0
        P.advance(p, p["last"] + minutes)

    def test_totem_saves_once_into_the_fridge(self):
        p = rookie()
        explore.use_item(p, "totem", p["last"])
        with self.assertRaises(P.Refused):
            explore.use_item(p, "totem", p["last"])    # nur eins gleichzeitig
        self.starve(p)
        self.assertTrue(p["alive"])
        self.assertTrue(p["frozen"])
        self.assertNotIn("totem", p)                    # verbraucht
        self.assertIn("Schutz-Totem", p["log"][-1]["text"])
        # im Kühlschrank steht die Zeit still – auch die restliche Zeit nach der Rettung
        in_stage, hunger = p["last"] - p["stage_since"], p["hunger"]
        P.advance(p, p["last"] + 5 * 24 * 60)
        self.assertEqual((p["last"] - p["stage_since"], p["hunger"]), (in_stage, hunger))
        self.assertTrue(p["alive"])
        # aufgetaut und wieder vernachlässigt: ohne Totem stirbt es diesmal
        P.set_frozen(p, False, p["last"])
        self.starve(p)
        self.assertFalse(p["alive"])

    def test_without_totem_it_dies(self):
        p = rookie()
        self.starve(p)
        self.assertFalse(p["alive"])
        self.assertFalse(p.get("frozen"))

    def test_totem_is_rare(self):
        import random
        rng = random.Random(1)
        picks = [explore._pick_item(rng) for _ in range(16000)]
        self.assertTrue(700 < picks.count("totem") < 1300)        # etwa jedes 16.
        self.assertTrue(40 < picks.count("wunder") < 170)         # goldenes Armor-Ei: etwa jedes 160.


class FreeEggTest(unittest.TestCase):
    def test_free_egg_only_when_nothing_left(self):
        store, owner = Store(":memory:"), "1"
        self.assertTrue(collection.can_get_free_egg(store, owner))
        p = store.add_pet(owner, rookie())
        self.assertFalse(collection.can_get_free_egg(store, owner))
        p["alive"] = False
        store.save_pet(p)
        self.assertTrue(collection.can_get_free_egg(store, owner))
        collection.store_egg(store, owner, "ver1", MORNING)
        self.assertFalse(collection.can_get_free_egg(store, owner))     # Ei in der Sammlung


if __name__ == "__main__":
    unittest.main()
