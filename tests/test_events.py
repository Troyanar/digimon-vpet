"""Tests für Events (Halloween, Pumpkinmon-Ei), Reset-Kristall und Erfolge.
Starten mit:  python -m unittest"""
import random
import unittest
from datetime import datetime

from game import battle, data, events, explore, progress, shop
from game import pet as P
from game.store import Store
from tests.test_battle import Always, rookie


def minute(month, day, hour=12):
    return int(datetime(2026, month, day, hour, 0).timestamp() // 60)


def named(name):
    return next(dex for dex in data.PLAYABLE if data.DIGIMON[dex]["name"] == name)


class EventTest(unittest.TestCase):
    def test_halloween_dates(self):
        self.assertIsNone(events.current(minute(10, 24)))
        self.assertEqual(events.current(minute(10, 25)), "halloween")
        self.assertEqual(events.current(minute(11, 2, 20)), "halloween")
        self.assertIsNone(events.current(minute(11, 3)))
        self.assertEqual(events.current(minute(7, 1), forced="halloween"), "halloween")

    def test_every_event_has_story_and_rewards(self):
        for key, ev in events.EVENTS.items():
            self.assertGreaterEqual(len(ev.get("story", [])), 2, key)          # kleine Story für den Event-Tab
            info = events.details(key, minute(*ev["start"]))
            self.assertTrue(info["rewards"], key)
            self.assertTrue(info["ghosts"], key)
        self.assertIsNone(events.details(None, minute(10, 25)))

    def test_halloween_details(self):
        info = events.details("halloween", minute(10, 25))
        self.assertEqual((info["from"], info["until"], info["days_left"]), ("25.10.", "02.11.", 9))
        self.assertEqual(events.details("halloween", minute(11, 2))["days_left"], 1)
        names = [data.DIGIMON[d]["name"] for d in info["egg"]["chain"]]
        self.assertEqual(names[-2:], ["Pumpkinmon", "NoblePumpkinmon"])
        self.assertTrue(any("30 %" in str(r) for r in info["rewards"]))         # Bonbon nach Geister-Sieg

    def test_ghosts_match_stage(self):
        for stage in ("Rookie", "Champion", "Ultimate", "Mega"):
            ghosts = events.ghosts("halloween", stage)
            self.assertTrue(ghosts, stage)
            self.assertTrue(all(data.DIGIMON[g]["stage"] == stage for g in ghosts))
        self.assertIn(named("Pumpkinmon"), events.ghosts("halloween", "Ultimate"))
        self.assertEqual(events.ghosts(None, "Rookie"), [])

    def test_ghost_battle_pays_double(self):
        p = rookie(strength=4, trainings=20, power=10)
        now = p["last"]
        battle.scout(p, now, Always(0.0), event="halloween")
        self.assertEqual(p["scout"]["ghost"], "halloween")
        battle.fight(p, now)
        result = {}
        while not result.get("over"):
            result = battle.shot(p, 1.0, now, Always(0.0))
            if not result["over"]:                           # immer ausweichen
                result = battle.evade(p, [True] * len(result["incoming"]), now, Always(0.0))
        self.assertTrue(result["won"] and result["ghost"] and result["candy"])
        self.assertEqual(result["bits"], 2 * shop.WILD_WIN["Rookie"])

    def test_no_ghosts_without_event(self):
        p = rookie()
        battle.scout(p, p["last"], Always(0.0))
        self.assertNotIn("ghost", p["scout"])

    def test_trip_bonus(self):
        self.assertEqual(events.trip_bonus(None), {"eggs": [], "items": []})
        found = events.trip_bonus("halloween", Always(0.0))
        self.assertEqual(found, {"eggs": ["halloween"], "items": ["candy"]})

    def test_candy_trade_for_halloween_egg(self):
        bag, eggs = {"candy": 14}, []
        add = lambda item, n: bag.__setitem__(item, bag.get(item, 0) + n)
        store_egg = lambda line: eggs.append(line) or True
        with self.assertRaises(shop.ShopError):
            shop.trade_candy("egg", None, bag, add, store_egg)                 # kein Event
        with self.assertRaises(shop.ShopError):
            shop.trade_candy("egg", "halloween", bag, add, store_egg)          # 14 < 15
        bag["candy"] = 16
        shop.trade_candy("egg", "halloween", bag, add, store_egg)
        self.assertEqual((bag["candy"], eggs), (1, ["halloween"]))
        with self.assertRaises(shop.ShopError):                                # Sammlung voll
            shop.trade_candy("egg", "halloween", {"candy": 20}, add, lambda line: False)
        self.assertEqual(shop.candy_offers(None), [])
        self.assertEqual(shop.candy_offers("halloween")[0]["cost"], 15)

    def test_candy_only_in_shop_during_event(self):
        store = Store(":memory:")
        shop.add(store, "1", 100)
        with self.assertRaises(shop.ShopError):
            shop.buy(store, "1", "candy", 1, lambda *a: None)
        shop.buy(store, "1", "candy", 1, lambda *a: None, event="halloween")
        self.assertIn("candy", [i["key"] for i in shop.catalog("halloween")])
        self.assertNotIn("candy", [i["key"] for i in shop.catalog()])


class PumpkinLineTest(unittest.TestCase):
    CHAIN = ["Yuramon", "Tanemon", "Candlemon", "Bakemon", "Pumpkinmon", "NoblePumpkinmon"]

    def test_pumpkinmon_only_in_the_event_egg(self):
        for name in ("Pumpkinmon", "NoblePumpkinmon"):
            dex = named(name)
            self.assertEqual({e["line"] for e in data.EVOLUTIONS if dex in (e["to"], e["from"])}, {"halloween"})
            self.assertIn(dex, data.EVENT_ONLY)
            self.assertNotIn(dex, data.WILD)                      # kein normaler wilder Gegner
        self.assertNotIn(named("Bakemon"), data.EVENT_ONLY)       # Bakemon gibt es auch so

    def test_event_egg_is_special(self):
        self.assertEqual(data.EVENT_LINES, {"halloween": "halloween"})
        self.assertNotIn("halloween", data.NORMAL_LINES)
        self.assertNotIn("halloween", explore.LINE_AREA)
        self.assertEqual(events.event_egg("halloween"), "halloween")

    def test_fixed_chain_no_matter_the_care(self):
        p = P.new_egg("halloween", minute(10, 26, 9))
        P.advance(p, p["last"] + 2)
        names = [data.DIGIMON[p["dex"]]["name"]]
        for _ in range(5):
            # schlecht versorgt: viele Pflegefehler, nie trainiert, überfüttert, keine Kämpfe
            p.update(mistakes=7, trainings=0, overfeeds=5, battles_stage=0, wins_stage=0)
            evo = P.next_form(p)
            self.assertIsNotNone(evo, names)
            P._evolve(p, evo, p["last"])
            names.append(data.DIGIMON[p["dex"]]["name"])
        self.assertEqual(names, self.CHAIN)
        self.assertEqual(P.next_form(p), None)                    # NoblePumpkinmon ist die Endstufe

    def test_never_a_random_or_battle_egg(self):
        rng = random.Random(4)
        p = rookie()
        explore._reset(p, p["last"], rng)
        self.assertIn(p["line"], data.NORMAL_LINES)
        bakemon = named("Bakemon")
        lines = sorted({e["line"] for e in data.EVOLUTIONS if e["to"] == bakemon} - set(data.EVENT_LINES))
        self.assertTrue(lines)
        self.assertNotIn("halloween", lines)


class ResetTest(unittest.TestCase):
    def test_reset_crystal(self):
        p = rookie()
        now = p["last"]
        p.update(name="Flammi", wins=7, battles=9, mistakes_total=6)
        anim, _ = explore.use_item(p, "reset", now)
        self.assertEqual(anim, "reset")
        self.assertEqual(p["stage"], "Egg")
        self.assertIsNone(p["dex"])
        self.assertEqual((p["name"], p["wins"], p["battles"]), ("Flammi", 7, 9))   # bleibt
        self.assertEqual(p["mistakes_total"], 0)                                    # neues Leben
        self.assertIn(named("Agumon"), p["forms"])                                  # Sammlung bleibt
        with self.assertRaises(P.Refused):
            explore.use_item(p, "reset", now)                                       # schon ein Ei

    def test_reset_needs_everstone_off(self):
        p = rookie()
        explore.use_item(p, "everstone", p["last"])
        with self.assertRaises(P.Refused):
            explore.use_item(p, "reset", p["last"])

    def test_reset_only_in_shop(self):
        self.assertIn("reset", shop.PRICES)
        self.assertNotIn("reset", explore.ITEM_ODDS)


class ProgressTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")

    def test_forms_and_collection(self):
        p = rookie()                                   # Botamon -> Koromon -> (Cheat) Agumon
        self.store.add_pet("1", p)
        have = progress.sync(self.store, "1")
        self.assertIn(named("Agumon"), have)
        self.assertIn(named("Koromon"), have)

    def test_forms_rebuilt_from_old_diary(self):
        old = {"line": "ver1", "dex": named("Greymon"), "stage": "Champion", "log": [
            {"t": 1, "text": "Das Ei ist geschlüpft: Botamon!"},
            {"t": 2, "text": "Botamon hat sich zu Koromon entwickelt!"},
            {"t": 3, "text": "Agumon hat Numemon besiegt! +10 Bits"}]}
        P.upgrade(old)
        self.assertEqual(old["forms"], [named("Botamon"), named("Koromon"), named("Greymon")])

    def test_achievements_pay_once(self):
        self.store.add_pet("1", rookie())
        new = progress.check(self.store, "1")
        keys = {a["key"] for a in new}
        self.assertTrue({"hatch", "rookie"} <= keys)
        self.assertNotIn("mega", keys)
        bits = shop.balance(self.store, "1")
        self.assertEqual(bits, sum(a["reward"] for a in new))
        self.assertEqual(progress.check(self.store, "1"), [])          # nicht doppelt
        progress.count(self.store, "1", "ghosts", 5)
        self.assertEqual([a["key"] for a in progress.check(self.store, "1")], ["ghosts5"])
        view = progress.view(self.store, "1")
        self.assertEqual(view["total"], len(data.PLAYABLE))
        self.assertTrue(next(a for a in view["achievements"] if a["key"] == "ghosts5")["done"])


if __name__ == "__main__":
    unittest.main()
