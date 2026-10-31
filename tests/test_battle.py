"""Tests für Kämpfe gegen wilde Digimon.  Starten mit:  python -m unittest"""
import random
import unittest

from game import battle, cheats, data
from game import pet as P
from tests.test_pet import MORNING, run


class Always:
    """Zufall zum Festlegen: random() liefert immer `value`."""
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value

    def choice(self, seq):
        return seq[0]

    def randint(self, a, b):
        return a


class Pick(Always):
    """Wie Always, wählt aber bei choice() den ersten der `picks`, der zur Auswahl steht."""
    def __init__(self, value, *picks):
        super().__init__(value)
        self.picks = picks

    def choice(self, seq):
        return next((x for x in self.picks if x in seq), seq[0])


def rookie(strength=4, trainings=0, power=0, speed=0, defense=0):
    p = P.new_egg("ver1", MORNING)
    run(p, MORNING, 20, every=1)
    cheats.apply(p, "become", {"line": "ver1", "dex": 29}, p["last"])      # Agumon
    p.update(hunger=4, strength=strength, trainings=trainings)
    p["skills"] = {"power": power, "speed": speed, "defense": defense}
    return p


def start(p, rng):
    battle.scout(p, p["last"], rng)
    battle.fight(p, p["last"])
    return p["battle"]


def battle_once(p, quality, rng):
    """Ganzer Kampf mit festem Schuss (alte Form "quality"); weicht immer aus."""
    now = p["last"]
    p["hunger"] = p["strength"] = 4
    battle.scout(p, now, rng)
    battle.fight(p, now)
    p["strength"] = max(p["strength"], 1)
    while True:
        r = battle.shot(p, quality, now, rng)
        if not r["over"]:
            r = battle.evade(p, [True] * len(r["incoming"]), now, rng)
        if r["over"]:
            return r


def realistic_battle(p, rng, charge):
    """Ganzer Kampf wie ein echter Spieler: Höhe zufällig (trifft die Lücke also in
    50 %), lädt `charge` (von, bis), Spezialattacke sobald die Leiste voll ist,
    weicht in 50 % aus (+2 % pro Tempo-Punkt, das Zeitfenster wird größer)."""
    now = p["last"]
    p["hunger"] = 4
    battle.scout(p, now, rng)
    battle.fight(p, now)
    dodge_rate = 0.5 + 0.02 * p["skills"]["speed"]
    while True:
        if p["battle"]["my_gauge"] >= battle.SPECIAL_MAX:
            shot = {"special": True, "mash": rng.uniform(0.5, 1.0)}
        else:
            shot = {"aim": rng.choice(battle.SIDES), "charge": rng.uniform(*charge)}
        r = battle.shot(p, shot, now, rng)
        if not r["over"]:
            r = battle.evade(p, [rng.random() < dodge_rate for _ in r["incoming"]], now, rng)
        if r["over"]:
            return r


class BattleTest(unittest.TestCase):
    def test_babies_cannot_fight(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 20, every=1)                       # Koromon
        with self.assertRaises(P.Refused):
            battle.scout(p, p["last"])

    def test_opponent_has_same_stage_and_fight_costs(self):
        p = rookie()
        battle.scout(p, p["last"])
        self.assertEqual(data.DIGIMON[p["scout"]["dex"]]["stage"], "Rookie")
        battle.fight(p, p["last"])
        self.assertEqual((p["hunger"], p["strength"]), (3, 3))
        self.assertNotIn("scout", p)
        with self.assertRaises(P.Refused):
            battle.flee(p, p["last"])                      # mitten im Kampf

    def test_win_counts_and_loses_weight(self):
        p = rookie()
        p["weight"] = 30
        r = battle_once(p, 1.0, Always(0.0))               # alles trifft, Gegner zuerst tot
        self.assertTrue(r["won"])
        self.assertEqual((p["battles"], p["wins"], p["battles_stage"], p["wins_stage"]), (1, 1, 1, 1))
        self.assertLess(p["weight"], 30)
        self.assertTrue(r["egg_line"])                     # 0.0 < Ei-Chance
        self.assertNotIn("battle", p)

    def test_loss_can_injure(self):
        p = rookie()
        rng = Always(0.0)
        battle.scout(p, p["last"], rng)
        battle.fight(p, p["last"])
        p["battle"]["opp_hp"] = 99                         # unbesiegbarer Gegner
        while True:
            r = battle.shot(p, 0.0, p["last"], rng)
            if r["over"]:
                break
        self.assertFalse(r["won"])
        self.assertTrue(p["injured"])
        self.assertEqual(p["wins"], 0)

    def test_round_limit_lives_decide_and_tie_is_draw(self):
        """Nach MAX_ROUNDS Runden entscheiden die Leben; gleich viele = unentschieden (kein Verlust)."""
        self.assertEqual(battle.MAX_ROUNDS, 25)
        for mine, theirs, won, draw in ((2, 2, False, True), (3, 1, True, False), (1, 2, False, False)):
            p = rookie()
            rng = Always(0.0)
            b = start(p, rng)
            b["round"] = battle.MAX_ROUNDS
            b["my_hp"], b["opp_hp"] = mine, theirs
            r = battle._end(p, b, {}, p["last"], rng)
            self.assertEqual((r["won"], r["draw"]), (won, draw))
            self.assertIn("Nach 25 Runden ist Schluss", r["message"])
            self.assertIn("after 25 rounds", r["message"].en)
            if draw:
                self.assertIn("unentschieden", r["message"])
                self.assertFalse(r["injured"])                         # Unentschieden verletzt nicht
                self.assertEqual((p["battles"], p["wins"]), (1, 0))

    def test_timeout(self):
        p = rookie()
        battle.scout(p, p["last"])
        with self.assertRaises(P.Refused):
            battle.fight(p, p["last"] + battle.TIMEOUT + 1)

    def test_attribute_triangle(self):
        self.assertEqual(battle.attr_bonus("Vaccine", "Virus"), 10)
        self.assertEqual(battle.attr_bonus("Virus", "Vaccine"), -10)
        self.assertEqual(battle.attr_bonus("Data", "Free"), 0)

    def win_rate(self, charge=(0.8, 1.0), n=600, **pet):
        rng = random.Random(42)
        wins = 0
        for _ in range(n):
            p = rookie(**pet)
            wins += realistic_battle(p, rng, charge)["won"]
        return wins / n

    def test_good_care_reaches_ultra_rate_bad_care_does_not(self):
        # 20 Trainings, davon 15 Erfolge auf alle drei Arten verteilt
        mixed = self.win_rate(strength=4, trainings=20, power=5, speed=5, defense=5)
        power = self.win_rate(strength=4, trainings=20, power=10, speed=3, defense=2)
        untrained = self.win_rate(strength=4, trainings=0)
        weak = self.win_rate(strength=1, trainings=0, charge=(0.0, 0.0))     # schlapp + lädt nicht
        self.assertGreater(mixed, 0.80)        # 12 von 15 ist machbar
        self.assertGreater(power, 0.80)
        self.assertLess(untrained, mixed)
        self.assertLess(weak, 0.55)
        print(f"\n  Siegquote gemischt trainiert: {mixed:.0%}, Kraft-Fokus: {power:.0%}, "
              f"untrainiert: {untrained:.0%}, schlecht: {weak:.0%}")

    def test_skills_in_battle(self):
        p = rookie()
        base_power, base_hp = battle.power(p), battle.max_hp(p)
        p["skills"] = {"power": 10, "speed": 10, "defense": 10}
        self.assertEqual(battle.power(p), base_power + 10)
        self.assertEqual(battle.max_hp(p), base_hp + 1)
        self.assertAlmostEqual(battle.dodge(p), 0.12)
        self.assertAlmostEqual(battle.injury_chance(p), 0.05)

    def test_old_quality_form_still_works(self):
        self.assertEqual(battle.parse_shot(0.9), {"aim": "high", "charge": 0.9, "special": False, "mash": 0.0})
        self.assertEqual(battle.parse_shot({"quality": 5})["charge"], 1.0)
        self.assertEqual(battle.parse_shot({"aim": "low", "charge": 9})["charge"], 2.0)
        self.assertEqual(battle.parse_shot({"aim": "quer", "charge": "nan"}), battle.parse_shot(0))
        self.assertTrue(battle.parse_shot({"special": True, "mash": 0.5})["special"])
        self.assertFalse(battle.parse_shot({"special": "ja"})["special"])

    def test_wins_unlock_ultimate(self):
        p = rookie()
        cheats.apply(p, "become", {"line": "ver1", "dex": 93}, p["last"])   # Greymon
        p.update(battles_stage=15, wins_stage=12)
        self.assertEqual(P.next_form(p)["to"], 220)                          # MetalGreymon
        self.assertEqual(P.view(p, p["last"])["battle_goal"], {"battles": 15, "wins": 12})


class NewFeaturesTest(unittest.TestCase):
    """Kampfsystem 3.0: Persönlichkeit, Höhe/Deckung, Laden, Spezialattacke, Ausweichen."""

    def roll(self, shot, value, **kw):
        # gleich starke Digimon ohne Attribut-Bonus: Grund-Trefferchance 0,40 + 0,30 × min(charge, 1)
        return battle.roll_attack(battle.parse_shot(shot), 50, 50, 0, Always(value), **kw)

    def test_personality_armored_has_four_lives(self):
        p = rookie()
        text = battle.scout(p, p["last"], Pick(0.0, "armored"))
        self.assertEqual(p["scout"]["personality"], "armored")
        self.assertIn("gepanzert", text)
        self.assertIn("armored", text.en)
        battle.fight(p, p["last"])
        self.assertEqual((p["battle"]["opp_hp"], p["battle"]["opp_max"]), (4, 4))
        view = battle.view(p)["battle"]
        self.assertEqual(view["opp_max"], 4)
        self.assertEqual(view["personality"]["key"], "armored")
        self.assertEqual(view["personality"]["name"].en, "armored")

    def test_personality_default_with_always(self):
        p = rookie()
        battle.scout(p, p["last"], Always(0.0))
        self.assertEqual(p["scout"]["personality"], "normal")
        self.assertEqual(battle.view(p)["scout"]["personality"]["name"], "ruhig")

    def test_gap_and_guard(self):
        gap = self.roll({"aim": "high", "charge": 1.0}, 0.6, guard="low")       # 0,70 + 0,20
        self.assertTrue(gap["gap"] and gap["hit"])
        self.assertEqual(gap["guard"], "low")
        guarded = self.roll({"aim": "high", "charge": 1.0}, 0.6, guard="high")  # 0,70 - 0,20
        self.assertFalse(guarded["gap"] or guarded["hit"])
        # im Kampf: der Gegner deckt per Zufall eine Seite
        p = rookie()
        start(p, Always(0.0))
        r = battle.shot(p, {"aim": "low", "charge": 1.0}, p["last"], Pick(0.0, "high"))
        self.assertEqual((r["guard"], r["gap"], r["aim"]), ("high", True, "low"))

    def test_sly_guards_last_side(self):
        p = rookie()
        battle.scout(p, p["last"], Pick(0.0, "sly"))
        battle.fight(p, p["last"])
        p["battle"]["last_aim"] = "low"
        r = battle.shot(p, {"aim": "low", "charge": 1.0}, p["last"], Pick(0.0, "sly", "high"))
        self.assertEqual(r["guard"], "low")                  # 0.0 < 70 %: deckt die letzte Seite
        self.assertFalse(r["gap"])

    def test_overcharge_can_be_interrupted(self):
        shot = {"aim": "high", "charge": 1.5}                # Risiko 0,6 × 0,5 = 0,30
        self.assertTrue(self.roll(shot, 0.2)["interrupted"])
        ok = self.roll(shot, 0.4)
        self.assertFalse(ok["interrupted"])
        self.assertTrue(ok["hit"])                           # 0,70 + 0,15
        self.assertTrue(self.roll(shot, 0.4, risk=0.2)["interrupted"])   # "flink"
        self.assertEqual(self.roll(shot, 0.2)["damage"], 0)
        # im Kampf: Schuss fällt aus, der Gegner greift trotzdem an
        p = rookie()
        start(p, Always(0.0))
        r = battle.shot(p, {"aim": "high", "charge": 1.5}, p["last"], Always(0.1))
        self.assertTrue(r["interrupted"])
        self.assertFalse(r["my_hit"])
        self.assertEqual(r["opp_hp"], 3)
        self.assertEqual(r["phase"], "dodge")
        self.assertEqual(len(r["incoming"]), 1)

    def test_mega_shot_does_two_damage(self):
        mega = self.roll({"aim": "high", "charge": 2.0}, 0.7)  # nicht unterbrochen (0,7 > 0,6)
        self.assertTrue(mega["mega"] and mega["power"] and mega["hit"])
        self.assertEqual(mega["damage"], 2)
        self.assertEqual(self.roll({"aim": "high", "charge": 1.0}, 0.0)["damage"], 1)
        p = rookie()
        start(p, Always(0.0))
        r = battle.shot(p, {"aim": "low", "charge": 2.0}, p["last"], Pick(0.7, "high"))
        self.assertEqual((r["damage"], r["opp_hp"]), (2, 1))

    def test_special_gauge_and_special_attack(self):
        p = rookie()
        b = start(p, Always(0.0))
        with self.assertRaises(P.Refused):                   # Leiste noch leer
            battle.shot(p, {"special": True, "mash": 1.0}, p["last"], Always(0.0))
        r = battle.shot(p, 1.0, p["last"], Always(0.0))
        self.assertEqual((r["my_gauge"], r["opp_gauge"]), (1, 1))    # Treffer: beide +1
        battle.evade(p, [True], p["last"], Always(0.0))
        b["my_gauge"] = battle.SPECIAL_MAX
        b["opp_hp"] = 3
        r = battle.shot(p, {"special": True, "mash": 0.0}, p["last"], Always(0.4))   # Chance 0,50
        self.assertTrue(r["special"] and r["my_hit"])
        self.assertIsNone(r["guard"])                        # nicht zu decken
        self.assertEqual((r["damage"], r["opp_hp"], r["my_gauge"]), (2, 1, 0))
        self.assertFalse(self.roll({"special": True, "mash": 0.0}, 0.6)["hit"])
        self.assertTrue(self.roll({"special": True, "mash": 1.0}, 0.9)["hit"])        # 0,95

    def test_opponent_special_cannot_be_dodged(self):
        p = rookie()
        b = start(p, Always(0.0))
        b["opp_gauge"] = battle.SPECIAL_MAX
        b["opp_hp"] = 99
        r = battle.shot(p, 1.0, p["last"], Always(0.0))
        self.assertEqual(r["incoming"], [{"side": "high", "strong": False, "special": True}])
        self.assertEqual(b["opp_gauge"], 0)
        r = battle.evade(p, [True], p["last"], Always(0.0))
        self.assertEqual((r["opp_hits"], r["dodged"], r["damage_taken"]), ([True], [False], 2))
        self.assertEqual(r["my_hp"], 1)

    def test_dodge_avoids_damage(self):
        p = rookie()
        b = start(p, Always(0.0))
        b["opp_hp"] = 99
        r = battle.shot(p, 1.0, p["last"], Always(0.0))
        self.assertTrue(r["incoming"][0]["strong"])          # 0.0 < 15 %: starker Angriff
        r = battle.evade(p, [True], p["last"], Always(0.0))
        self.assertEqual((r["opp_hits"], r["dodged"], r["damage_taken"], r["my_hp"]), ([False], [True], 0, 3))
        self.assertEqual(r["phase"], "done")
        self.assertNotIn("incoming", b)
        with self.assertRaises(P.Refused):                   # nichts mehr auszuweichen
            battle.evade(p, [True], p["last"], Always(0.0))
        battle.shot(p, 1.0, p["last"], Always(0.0))
        r = battle.evade(p, [False], p["last"], Always(0.0))
        self.assertEqual((r["opp_hits"], r["damage_taken"], r["my_hp"]), ([True], 2, 1))

    def test_aggressive_shoots_twice(self):
        p = rookie()
        battle.scout(p, p["last"], Pick(0.0, "aggressive"))
        battle.fight(p, p["last"])
        p["battle"]["opp_hp"] = 99
        r = battle.shot(p, 1.0, p["last"], Pick(0.0, "low"))
        self.assertEqual(len(r["incoming"]), 2)
        r = battle.evade(p, [True], p["last"], Always(0.0))   # zweite Angabe fehlt = nicht ausgewichen
        self.assertEqual(r["dodged"], [True, False])
        self.assertEqual(r["opp_hits"], [False, True])

    def test_open_incoming_counts_as_not_dodged(self):
        p = rookie()
        b = start(p, Always(0.0))
        b["opp_hp"] = 99
        battle.shot(p, 1.0, p["last"], Always(0.0))
        self.assertTrue(battle.view(p)["battle"]["incoming"])     # nach Neuladen sichtbar
        r = battle.shot(p, 1.0, p["last"], Always(0.0))          # ohne auszuweichen weiter
        self.assertEqual(r["late"]["opp_hits"], [True])
        self.assertEqual(r["late"]["damage_taken"], 2)
        self.assertEqual(b["round"], 2)
        r = battle.shot(p, 1.0, p["last"], Always(0.0))          # noch mal: jetzt k.o.
        self.assertTrue(r["over"])
        self.assertFalse(r["won"])
        self.assertEqual(r["my_hp"], 0)

    def test_battle_can_end_while_dodging(self):
        p = rookie()
        b = start(p, Always(0.0))
        b["opp_hp"], b["my_hp"] = 99, 1
        battle.shot(p, 1.0, p["last"], Always(0.0))
        r = battle.evade(p, [False], p["last"], Always(0.0))
        self.assertTrue(r["over"])
        self.assertFalse(r["won"])
        self.assertIn("bits", r)
        self.assertIn("verloren", r["message"])
        self.assertNotIn("battle", p)

    def test_view_fields_and_json(self):
        import json
        p = rookie()
        start(p, Always(0.0))
        view = battle.view(p)["battle"]
        for key in ("my_gauge", "opp_gauge", "personality", "special_name", "opp_special_name", "opp_max", "incoming"):
            self.assertIn(key, view)
        self.assertEqual(view["special_name"], "Baby Flame")      # Agumon, erste Attacke im Digidex
        self.assertIsNone(view["incoming"])
        r = battle.shot(p, {"aim": "low", "charge": 1.2}, p["last"], Always(0.5))
        for key in ("phase", "aim", "guard", "gap", "interrupted", "mega", "special", "damage", "incoming",
                    "my_gauge", "opp_gauge", "my_hp", "opp_hp", "over", "my_hit", "power_shot"):
            self.assertIn(key, r)
        json.dumps([r, battle.view(p)])
        r = battle.evade(p, [False], p["last"], Always(0.5))
        for key in ("phase", "opp_hits", "dodged", "damage_taken", "my_hp", "opp_hp", "my_gauge", "opp_gauge", "over"):
            self.assertIn(key, r)
        json.dumps(r)

    def test_special_name_fallback(self):
        self.assertEqual(battle.special_name(-1), "Spezialattacke")
        self.assertEqual(battle.special_name(-1).en, "Special Attack")


if __name__ == "__main__":
    unittest.main()
