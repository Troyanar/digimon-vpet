"""Tests für Nickerchen, Kühlschrank und Sammlung.  Starten mit:  python -m unittest"""
import unittest

from game import collection
from game import pet as P
from game.store import Store
from tests.test_pet import MORNING, run


def koromon():
    p = P.new_egg("ver1", MORNING)
    run(p, MORNING, 20, every=1)
    return p


class NapTest(unittest.TestCase):
    def test_light_off_starts_nap_and_light_on_wakes(self):
        p = koromon()
        now = p["last"]
        P.toggle_light(p, now)
        self.assertTrue(p["asleep"] and p["nap"])
        with self.assertRaises(P.Refused):
            P.train(p, True, now)                     # Training weckt es nicht
        P.toggle_light(p, now)
        self.assertFalse(p["asleep"] or p["nap"])

    def test_food_wakes_from_nap_but_not_at_night(self):
        p = koromon()
        now = p["last"]
        P.toggle_light(p, now)                        # Nickerchen – wird dabei langsam hungrig
        p["hunger"] = 0
        P.feed(p, "meat", now)                        # riecht Futter, wacht auf, isst
        self.assertFalse(p["asleep"] or p["nap"])
        self.assertTrue(p["light"])
        self.assertEqual(p["hunger"], 1)
        night = koromon()
        run(night, night["last"], 13 * 60, every=5)   # bis in die Nacht
        self.assertTrue(night["asleep"] and not night.get("nap"))
        with self.assertRaises(P.Refused):
            P.feed(night, "meat", night["last"])      # nachts schläft es wirklich (und hungert nicht)

    def test_nap_halves_hunger_and_stops_poop(self):
        awake, napping = koromon(), koromon()
        now = awake["last"]
        P.toggle_light(napping, now)
        P.advance(awake, now + 120)
        P.advance(napping, now + 120)
        self.assertGreater(napping["hunger"], awake["hunger"])
        self.assertEqual(napping["poop"], 0)
        self.assertTrue(napping["asleep"])            # bleibt im Nickerchen

    def test_nap_turns_into_night_sleep(self):
        p = koromon()
        run(p, p["last"], 11 * 60, every=5)           # gut versorgt bis ca. 20:20
        P.toggle_light(p, p["last"])                  # Nickerchen
        P.advance(p, p["last"] + 90)                  # 21:50: Schlafenszeit (21 Uhr) ist da
        self.assertTrue(p["asleep"])
        self.assertFalse(p["nap"])                    # jetzt echter Nachtschlaf
        P.advance(p, p["last"] + 11 * 60)             # nächster Morgen
        # Licht ist noch aus: es döst als Nickerchen weiter, bis man das Licht anmacht
        self.assertTrue(p["asleep"] and p["nap"])
        self.assertFalse(p["light"])
        P.toggle_light(p, p["last"])
        self.assertFalse(p["asleep"])
        self.assertTrue(p["light"])

    def test_morning_with_light_on_wakes_up(self):
        p = koromon()
        run(p, p["last"], 11 * 60, every=5)
        P.advance(p, p["last"] + 90)                  # Schlafenszeit, Licht bleibt an (Pflegefehler)
        P.advance(p, p["last"] + 11 * 60)
        self.assertFalse(p["asleep"])                 # Licht war an -> normal aufgewacht

    def test_evolution_clock_pauses_in_fridge(self):
        p = koromon()
        since = p["stage_since"]
        P.set_frozen(p, True, p["last"])
        P.advance(p, p["last"] + 7 * 24 * 60)
        P.set_frozen(p, False, p["last"])
        self.assertEqual(P.display_name(p), "Koromon")
        self.assertEqual(p["stage_since"] - since, 7 * 24 * 60)   # Uhr um die Woche verschoben


class FridgeTest(unittest.TestCase):
    def test_frozen_time_stands_still(self):
        p = koromon()
        hunger, now = p["hunger"], p["last"]
        P.set_frozen(p, True, now)
        P.advance(p, now + 7 * 24 * 60)               # eine Woche Urlaub
        self.assertTrue(p["alive"])
        self.assertEqual(p["hunger"], hunger)
        with self.assertRaises(P.Refused):
            P.clean(p, p["last"])
        P.set_frozen(p, False, p["last"])
        P.advance(p, p["last"] + 30)
        self.assertLess(p["hunger"], hunger)          # läuft wieder


class CollectionTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.owner = "1"

    def test_new_egg_puts_old_into_box_and_switch_back(self):
        first = self.store.add_pet(self.owner, koromon())
        collection.new_egg(self.store, self.owner, MORNING + 30)
        box = collection.boxed(self.store, self.owner)
        self.assertEqual([p["id"] for p in box], [first["id"]])
        self.assertEqual(self.store.active_pet(self.owner)["stage"], "Egg")

        hunger = box[0]["hunger"]
        collection.switch(self.store, self.owner, first["id"], MORNING + 10 * 60)
        active = self.store.active_pet(self.owner)
        self.assertEqual(active["id"], first["id"])
        self.assertEqual(active["hunger"], hunger)    # in der Box stand die Zeit still
        self.assertEqual(len(collection.boxed(self.store, self.owner)), 1)   # das Ei

    def test_box_is_limited_but_switch_works_when_full(self):
        self.store.add_pet(self.owner, koromon())
        for _ in range(collection.BOX_SIZE):
            collection.new_egg(self.store, self.owner, MORNING + 30)
        with self.assertRaises(P.Refused):
            collection.new_egg(self.store, self.owner, MORNING + 30)
        some = collection.boxed(self.store, self.owner)[0]
        collection.switch(self.store, self.owner, some["id"], MORNING + 40)   # Tausch geht
        collection.release(self.store, self.owner, collection.boxed(self.store, self.owner)[0]["id"])
        collection.new_egg(self.store, self.owner, MORNING + 50)              # jetzt wieder Platz

    def test_boxes_like_pokemon_pc(self):
        self.assertEqual((collection.BOXES, collection.PER_BOX, collection.BOX_SIZE), (8, 20, 160))
        for _ in range(23):
            collection.store_egg(self.store, self.owner, "ver1", MORNING)
        view = collection.overview(self.store, self.owner, MORNING)
        boxes = [p["box"] for p in view["box"]]
        self.assertEqual(boxes.count(0), 20)                 # Box 1 voll, der Rest in Box 2
        self.assertEqual(boxes.count(1), 3)
        self.assertEqual(view["boxes"][:2], ["Box 1", "Box 2"])
        # verschieben – aber nicht in eine volle Box
        some = next(p for p in view["box"] if p["box"] == 1)
        with self.assertRaises(P.Refused):
            collection.move(self.store, self.owner, some["id"], 0)
        collection.move(self.store, self.owner, some["id"], 7)
        view = collection.overview(self.store, self.owner, MORNING)
        self.assertEqual(next(p for p in view["box"] if p["id"] == some["id"])["box"], 7)
        with self.assertRaises(P.Refused):
            collection.move(self.store, self.owner, some["id"], 8)          # gibt's nicht
        # umbenennen (leer = wieder "Box N", zu lang wird gekürzt)
        collection.rename_box(self.store, self.owner, 2, "  Meine   Drachen  ")
        collection.rename_box(self.store, self.owner, 3, "X" * 40)
        names = collection.box_names(self.store, self.owner)
        self.assertEqual(names[2], "Meine Drachen")
        self.assertEqual(len(names[3]), collection.NAME_MAX)
        collection.rename_box(self.store, self.owner, 2, "   ")
        self.assertEqual(collection.box_names(self.store, self.owner)[2], "Box 3")

    def test_switch_puts_partner_on_the_freed_place(self):
        self.store.add_pet(self.owner, koromon())
        for _ in range(21):
            collection.store_egg(self.store, self.owner, "ver1", MORNING)
        egg = next(p for p in collection.overview(self.store, self.owner, MORNING)["box"] if p["box"] == 1)
        collection.switch(self.store, self.owner, egg["id"], MORNING + 1)
        view = collection.overview(self.store, self.owner, MORNING + 1)
        self.assertEqual(next(p for p in view["box"] if p["name"] == "Koromon")["box"], 1)

    def _boxed_rookies(self, n):
        """n Agumon (Rookie) in der Sammlung, dazu ein aktives Ei."""
        from game import cheats
        for _ in range(n):
            p = koromon()
            cheats.apply(p, "become", {"line": "ver1", "dex": 29}, p["last"])      # Agumon
            p.update(hunger=2, in_box=True)
            self.store.add_pet(self.owner, p, active=False)
        self.store.add_pet(self.owner, P.new_egg("ver1", MORNING))
        return [p["id"] for p in collection.layout(self.store, self.owner)]

    def test_box_digimon_explore(self):
        from game import explore
        ids = self._boxed_rookies(4)
        now = MORNING + 60
        collection.send(self.store, self.owner, ids[0], "wald", 120, now)
        mon = self.store.pet_by_id(ids[0])
        hunger = mon["hunger"]
        # unterwegs: nicht aktiv setzen, nicht freilassen, nicht nochmal losschicken
        for action in (lambda: collection.switch(self.store, self.owner, ids[0], now),
                       lambda: collection.release(self.store, self.owner, ids[0]),
                       lambda: collection.send(self.store, self.owner, ids[0], "wald", 30, now),
                       lambda: collection.send(self.store, self.owner, ids[1], "vulkan", 30, now)):  # zu gefährlich
            with self.assertRaises(P.Refused):
                action()
        # höchstens 3 gleichzeitig
        collection.send(self.store, self.owner, ids[1], "kueste", 30, now)
        collection.send(self.store, self.owner, ids[2], "wald", 480, now)
        with self.assertRaises(P.Refused) as err:
            collection.send(self.store, self.owner, ids[3], "wald", 30, now)
        self.assertIn("3", str(err.exception))
        # vor der Zeit: nichts zurück
        items = []
        self.assertEqual(collection.claim_trips(self.store, self.owner, now + 20, items.append), [])
        # danach: Bericht, Funde, Platz für eine neue Reise
        reports = collection.claim_trips(self.store, self.owner, now + 121, items.append,
                                         rng=__import__("random").Random(3))
        self.assertEqual(len(reports), 2)                       # 30 Min + 2 Std sind um, 8 Std nicht
        self.assertTrue(all("ist zurück aus" in r for r in reports))
        self.assertTrue(all(i in explore.ITEMS for i in items))
        back = self.store.pet_by_id(ids[0])
        self.assertNotIn("box_trip", back)
        self.assertEqual(back["hunger"], hunger)                # in der Sammlung steht die Zeit still
        self.assertEqual(collection.claim_trips(self.store, self.owner, now + 200, items.append), [])  # nur einmal
        collection.send(self.store, self.owner, ids[3], "wald", 30, now + 200)
        view = collection.overview(self.store, self.owner, now + 210)
        trips = {p["id"]: p["trip"] for p in view["box"]}
        self.assertEqual(trips[ids[3]]["minutes_left"], 20)
        self.assertEqual(view["max_trips"], 3)
        # Übersicht "Zurück vom Erkunden": die Berichte bleiben stehen (mit englischer Fassung)
        self.assertEqual([r["text"] for r in view["trip_reports"]], [str(r) for r in reversed(reports)])
        self.assertIn("is back from", view["trip_reports"][0]["text"].en)
        self.assertEqual(view["trip_reports"][0]["t"], now + 121)
        # zurückrufen: ohne Funde
        collection.recall_trip(self.store, self.owner, ids[3], now + 210)
        self.assertNotIn("box_trip", self.store.pet_by_id(ids[3]))

    def test_eggs_cannot_explore(self):
        collection.store_egg(self.store, self.owner, "ver1", MORNING)
        egg = collection.layout(self.store, self.owner)[0]
        with self.assertRaises(P.Refused):
            collection.send(self.store, self.owner, egg["id"], "wald", 30, MORNING)

    def test_nicknames(self):
        p = koromon()
        with self.assertRaises(P.Refused):
            P.set_nickname(P.new_egg("ver1", MORNING), "Ei", MORNING)      # erst nach dem Schlüpfen
        P.set_nickname(p, "  Flammi \n\t der   Große  ", p["last"])
        self.assertEqual(p["name"], "Flammi der G")                    # Leerzeichen bereinigt, max. 12
        self.assertEqual(P.label(p), "Flammi der G (Koromon)")
        self.assertEqual(P.display_name(p), "Koromon")                  # Meldungen nennen weiter die Art
        self.assertEqual(P.view(p, p["last"])["nickname"], "Flammi der G")
        P.set_nickname(p, "koromon", p["last"])                         # = Art -> kein Spitzname
        self.assertIsNone(p["name"])
        P.set_nickname(p, "Bubu", p["last"])
        p["stage_since"] = p["last"] - P.STAGE_TIME["InTraining"]       # Digitation fällig (am Tag)
        P.advance(p, p["last"] + 1)                                     # Digitation behält den Namen
        self.assertNotEqual(P.display_name(p), "Koromon")
        self.assertEqual(p["name"], "Bubu")
        P.set_nickname(p, "", p["last"])
        self.assertIsNone(p["name"])

    def test_ranking_without_admins(self):
        admin = self.store.add_user("admin", "x", "y", True)
        player = self.store.add_user("Troyana", "x", "y", False)
        for uid, wins in ((admin, 50), (player, 3)):
            p = koromon()
            p.update(wins=wins, battles=wins)
            self.store.add_pet(str(uid), p)
        names = [r["name"] for r in collection.ranking(self.store)]
        self.assertEqual(names, ["Troyana"])

    def test_old_released_pets_come_back(self):
        old = koromon()
        old["released"] = old["last"]
        self.store.add_pet(self.owner, old, active=False)
        self.store.add_pet(self.owner, koromon())
        view = collection.overview(self.store, self.owner, MORNING + 60)
        self.assertEqual(len(view["box"]), 1)

    def test_dead_pets_are_memories(self):
        dead = koromon()
        P.advance(dead, dead["last"] + 3 * 24 * 60)
        self.store.add_pet(self.owner, dead)
        collection.new_egg(self.store, self.owner, MORNING)
        view = collection.overview(self.store, self.owner, MORNING)
        self.assertEqual(view["box"], [])
        self.assertEqual(view["memories"][0]["name"], "Koromon")


if __name__ == "__main__":
    unittest.main()
