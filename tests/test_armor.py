"""Tests für die Armor-Digitation (Armor-Eier aus dem Rucksack).  Starten mit:  python -m unittest"""
import json
import random
import unittest
from pathlib import Path

from game import cheats, data, explore
from game import pet as P
from tests.test_pet import MORNING, run


def num(name):
    return next(dex for dex, d in data.PLAYABLE.items() if d["name"] == name)


def as_digimon(name):
    """Ein waches, gesundes Digimon in einer Linie, in der es vorkommt."""
    dex = num(name)
    line = next(e["line"] for e in data.EVOLUTIONS if e["to"] == dex)
    p = P.new_egg(line, MORNING)
    run(p, MORNING, 20, every=1)
    cheats.apply(p, "become", {"line": line, "dex": dex}, p["last"])
    p.update(hunger=4, strength=4)
    return p


class ArmorDataTest(unittest.TestCase):
    def test_every_armor_egg_has_a_use(self):
        self.assertEqual(len(data.ARMOR_ITEMS), 9)
        for key in data.ARMOR_ITEMS:
            self.assertTrue(any(e["rule"].get("item") == key for e in data.EVOLUTIONS), key)
            self.assertIn(key, explore.ITEMS)
            self.assertGreater(explore.ITEM_ODDS[key], 0)

    def test_anime_pairs(self):
        expected = {("Veemon", "Flamedramon"), ("Veemon", "Raidramon"), ("Veemon", "Magnamon"),
                    ("Hawkmon", "Halsemon"), ("Hawkmon", "Shurimon"), ("Armadillomon", "Digmon"),
                    ("Armadillomon", "Submarimon"), ("Patamon", "Pegasusmon"), ("Salamon", "Nefertimon"),
                    ("Gatomon", "Nefertimon")}
        found = {(data.DIGIMON[e["from"]]["name"], data.DIGIMON[e["to"]]["name"])
                 for e in data.EVOLUTIONS if "item" in e["rule"]}
        self.assertEqual(found, expected)

    def test_armor_forms_are_final(self):
        # Armor-Formen haben ihre eigene Stufe "Armor" und digitieren nicht weiter
        forms = {e["to"] for e in data.EVOLUTIONS if "item" in e["rule"]}
        self.assertEqual(len(forms), 9)
        for dex in forms:
            self.assertEqual(data.DIGIMON[dex]["stage"], "Armor", data.DIGIMON[dex]["name"])
            self.assertFalse(any(e["from"] == dex for e in data.EVOLUTIONS), data.DIGIMON[dex]["name"])
        self.assertEqual({e["stage"] for e in data.EVOLUTIONS if "item" in e["rule"]}, {"Armor"})
        self.assertFalse(any(d["stage"] == "Armor" for dex, d in data.PLAYABLE.items() if dex not in forms))

    def test_hawkmon_hatches_from_an_egg(self):
        hawk = num("Hawkmon")
        reach = {}
        for e in data.EVOLUTIONS:
            reach.setdefault(e["line"], set()).add(e["to"])
        self.assertTrue(any(hawk in r for r in reach.values()))

    def test_armor_never_happens_by_itself(self):
        p = as_digimon("Veemon")
        for mistakes in (0, 5):
            for trainings in (0, 20):
                p.update(mistakes=mistakes, trainings=trainings)
                evo = P.next_form(p)
                self.assertNotIn("item", evo["rule"])

    def test_names_like_german_dub(self):
        names = {d["name"] for d in data.PLAYABLE.values()}
        self.assertTrue({"Armadillomon", "Halsemon", "Pegasusmon"} <= names)
        self.assertFalse({"Armadimon", "Holsmon", "Pegasmon"} & names)


class ArmorUseTest(unittest.TestCase):
    def test_courage_makes_flamedramon(self):
        p = as_digimon("Veemon")
        anim, msg = explore.use_item(p, "mut", p["last"])
        self.assertEqual(anim, "armor")
        self.assertEqual(P.display_name(p), "Flamedramon")
        self.assertEqual(p["stage"], "Armor")
        self.assertEqual(p["battles_stage"], 0)
        self.assertIn("Armor-Ei des Mutes", msg)

    def test_wrong_egg_is_refused(self):
        p = as_digimon("Veemon")
        with self.assertRaises(P.Refused) as err:
            explore.use_item(p, "liebe", p["last"])
        self.assertIn("Hawkmon", str(err.exception))
        self.assertEqual(P.display_name(p), "Veemon")

    def test_sick_digimon_cannot(self):
        p = as_digimon("Patamon")
        p["sick"], p["sick_since"] = True, p["last"]
        with self.assertRaises(P.Refused):
            explore.use_item(p, "hoffnung", p["last"])
        self.assertEqual(P.display_name(p), "Patamon")

    def test_light_works_for_gatomon_too(self):
        for name in ("Salamon", "Gatomon"):
            p = as_digimon(name)
            explore.use_item(p, "licht", p["last"])
            self.assertEqual(P.display_name(p), "Nefertimon")

    def test_miracles_makes_magnamon(self):
        p = as_digimon("Veemon")
        explore.use_item(p, "wunder", p["last"])
        self.assertEqual((P.display_name(p), p["stage"]), ("Magnamon", "Armor"))

    def test_armor_form_lives_on_but_never_evolves(self):
        p = as_digimon("Veemon")
        explore.use_item(p, "mut", p["last"])
        p.update(mistakes=0, battles_stage=15, wins_stage=12)
        self.assertIsNone(P.next_form(p))
        P.advance(p, p["last"] + 5 * 24 * 60)          # Tage später: immer noch Flamedramon
        self.assertEqual(P.display_name(p), "Flamedramon")
        view = P.view(p, p["last"])
        self.assertIsNone(view["evolve_in"])
        self.assertEqual(view["stage_de"], "Armor")

    def test_armor_form_can_battle_and_explore(self):
        from game import battle
        p = as_digimon("Patamon")
        explore.use_item(p, "hoffnung", p["last"])
        self.assertIn("Armor", battle.BATTLE_STAGES)
        self.assertTrue(explore.unlocked(p, "stadt"))     # wie Champion
        self.assertFalse(explore.unlocked(p, "vulkan"))   # Ultra-Gebiete noch nicht

    def test_options_show_what_fits(self):
        p = as_digimon("Armadillomon")
        self.assertEqual(set(explore.armor_options(p)), {"wissen", "zuverlaessigkeit"})

    def test_found_while_exploring(self):
        rng = random.Random(1)
        found = {explore._pick_item(rng) for _ in range(5000)}
        self.assertTrue(set(data.ARMOR_ITEMS) <= found)


class CheatTest(unittest.TestCase):
    def test_always_day_wakes_and_keeps_awake(self):
        p = as_digimon("Veemon")
        night = MORNING + 14 * 60                      # 23:00
        P.advance(p, night)
        self.assertTrue(p["asleep"])
        self.assertTrue(cheats.set_day(p, True))
        self.assertFalse(p["asleep"])
        P.advance(p, night + 60)
        self.assertFalse(p["asleep"])
        self.assertFalse(cheats.set_day(p, True))     # schon an -> nichts zu tun
        cheats.set_day(p, False)
        P.advance(p, night + 61)
        self.assertTrue(p["asleep"])

    def test_item_amount(self):
        self.assertEqual(cheats.amount(5), 5)
        self.assertEqual(cheats.amount(500), 99)
        with self.assertRaises(P.Refused):
            cheats.amount("viele")


class VersionTest(unittest.TestCase):
    def test_every_changelog_entry_has_a_version(self):
        log = json.loads((Path(__file__).resolve().parent.parent / "static" / "changelog.json").read_text(encoding="utf8"))
        versions = [e["version"] for e in log]
        self.assertEqual(len(set(versions)), len(versions))
        for v in versions:
            parts = v.split(".")
            self.assertIn(len(parts), (2, 3), v)
            self.assertTrue(all(x.isdigit() for x in parts), v)
        # neueste zuerst
        key = lambda v: tuple(int(x) for x in v.split(".")) + (0,) * (3 - len(v.split(".")))
        self.assertEqual(versions, sorted(versions, key=key, reverse=True))


if __name__ == "__main__":
    unittest.main()
