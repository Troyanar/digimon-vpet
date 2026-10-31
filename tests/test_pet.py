"""Tests der Pflege-Simulation.  Starten mit:  python -m unittest"""
import unittest
from datetime import datetime

from game import pet as P

# 22.10.2026, 09:00 Uhr Ortszeit (in Spielminuten)
MORNING = int(datetime(2026, 10, 22, 9, 0).timestamp() // 60)


def care(p, minute):
    """Ein perfekter Pfleger: füttert, trainiert, putzt, macht abends Licht aus und morgens an."""
    if not p["alive"] or p["stage"] == "Egg":
        return
    if p["asleep"] and p.get("nap"):
        P.toggle_light(p, minute)          # Morgen: es döst im Dunkeln -> Licht an weckt es
    if p["asleep"]:
        if p["light"]:
            P.toggle_light(p, minute)
        return
    if p["hunger"] < 4:
        P.feed(p, "meat", minute)
    if p["strength"] < 4:
        P.feed(p, "protein", minute)
    if p["poop"]:
        P.clean(p, minute)
    if p["sick"] or p["injured"]:
        P.medicine(p, minute)


def run(p, start, minutes, every=5, trainer=None):
    for m in range(start, start + minutes, every):
        P.advance(p, m)
        care(p, m)
        if trainer:
            trainer(p, m)
    P.advance(p, start + minutes)


class PetTest(unittest.TestCase):
    def test_hatch_and_baby_stages(self):
        p = P.new_egg("ver1", MORNING)
        P.advance(p, MORNING + 2)
        self.assertEqual(p["stage"], "Fresh")
        self.assertEqual(P.display_name(p), "Botamon")
        run(p, MORNING + 2, 15, every=1)
        self.assertEqual(P.display_name(p), "Koromon")

    # Koromon braucht 12 h; um 21:00 schläft es ein und entwickelt sich
    # deshalb erst nach dem Aufwachen um 8:00 am nächsten Morgen.
    NEXT_MORNING = 24 * 60 + 10

    def test_good_care_gives_agumon(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 12 * 60, every=5)
        self.assertEqual(P.display_name(p), "Koromon")   # schläft vor der Entwicklung ein
        run(p, MORNING + 12 * 60, self.NEXT_MORNING - 12 * 60, every=5)
        self.assertTrue(p["alive"])
        self.assertEqual(P.display_name(p), "Agumon")
        self.assertEqual(p["mistakes_total"], 0)

    def test_neglect_gives_betamon(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 20, every=1)          # Koromon
        # jeder ignorierte Ruf ist ein Pflegefehler: zweimal vernachlässigen
        P.advance(p, MORNING + 3 * 60)
        self.assertEqual(p["mistakes"], 2)    # Hunger + Kraft ignoriert
        run(p, MORNING + 3 * 60, 10, every=5)
        P.advance(p, MORNING + 5 * 60)
        self.assertEqual(p["mistakes"], 4)
        run(p, MORNING + 5 * 60, self.NEXT_MORNING - 5 * 60, every=5)
        self.assertEqual(P.display_name(p), "Betamon")

    def test_much_training_gives_greymon(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, self.NEXT_MORNING, every=5)
        self.assertEqual(P.display_name(p), "Agumon")

        def trainer(pet, m):
            if not pet["asleep"] and pet["stage"] == "Rookie" and pet["trainings"] < 20:
                P.train(pet, True, m)
        run(p, MORNING + self.NEXT_MORNING, 2 * 24 * 60, every=5, trainer=trainer)
        self.assertEqual(P.display_name(p), "Greymon")

    def grow_champion(self, line, trainings):
        """Perfekte Pflege bis zum Champion, als Rookie `trainings` Trainings."""
        p = P.new_egg(line, MORNING)

        def trainer(pet, m):
            if not pet["asleep"] and pet["stage"] == "Rookie" and pet["trainings"] < trainings:
                P.train(pet, True, m)
        run(p, MORNING, self.NEXT_MORNING + 2 * 24 * 60, every=5, trainer=trainer)
        return p

    def test_impmon_line_towards_beelzemon(self):
        p = self.grow_champion("impmon", 20)
        self.assertTrue(p["alive"])
        self.assertEqual(P.display_name(p), "Wizardmon")       # -> Baalmon -> Beelzemon

    def test_salamon_line_towards_lilithmon(self):
        p = self.grow_champion("salamon", 0)
        self.assertEqual(P.display_name(p), "Devimon")        # -> LadyDevimon -> Lilithmon

    def test_new_rookies(self):
        for line, rookie in [("gomamon", "Gomamon"), ("veemon", "Veemon"), ("wormmon", "Wormmon")]:
            p = P.new_egg(line, MORNING)
            run(p, MORNING, self.NEXT_MORNING, every=5)
            self.assertEqual(P.display_name(p), rookie)

    def test_anime_path_leomon(self):
        """Leomon wird bei perfekter Pflege zu GrapLeomon -> BanchoLeomon (Anime),
        sonst bleibt der alte V-Pet-Weg (Megadramon)."""
        from game import data
        dex = {v["name"]: k for k, v in data.PLAYABLE.items()}
        p = {"line": "ver4", "dex": dex["Leomon"], "mistakes": 0, "trainings": 16, "overfeeds": 0,
             "battles_stage": 15, "wins_stage": 12, "skills": {s: 0 for s in P.SKILLS}}
        self.assertEqual(data.DIGIMON[P.next_form(p)["to"]]["name"], "GrapLeomon")
        p["mistakes"] = 1
        self.assertEqual(data.DIGIMON[P.next_form(p)["to"]]["name"], "Megadramon")
        p.update(dex=dex["GrapLeomon"], mistakes=0, battles_stage=0, wins_stage=0)
        self.assertEqual(data.DIGIMON[P.next_form(p)["to"]]["name"], "BanchoLeomon")

    def test_no_free_stage_jumps(self):
        """Wer eine Stufe überspringt (z. B. Rookie -> Mega), muss dafür kämpfen. (Armor-Formen
        sind eine eigene Endstufe neben Champion – dafür braucht es ein Armor-Ei.)"""
        from game import data
        for e in data.EVOLUTIONS:
            if e["from"] is None or "item" in e["rule"]:
                continue
            jump = P.STAGES.index(e["stage"]) - P.STAGES.index(data.DIGIMON[e["from"]]["stage"])
            if e["stage"] in ("Ultimate", "Mega") and data.DIGIMON[e["from"]]["stage"] == "Champion":
                jump -= 1                                  # "Armor" liegt dazwischen, zählt nicht
            if jump > 1:
                self.assertTrue(P.needs_battles(e["rule"]), e)

    def test_every_line_grows_up(self):
        """Jede Linie: Ei schlüpft und wird bei guter Pflege mindestens Champion."""
        from game import data
        stuck = []
        for line in data.LINES:
            p = self.grow_champion(line, 20)
            # Stufensprünge (Keramon X: Rookie -> Mega) brauchen Kämpfe – das zählt nicht als hängen
            waits_for_battles = p["alive"] and p["stage"] == "Rookie" and P._blocked_by_battles(p)
            if not p["alive"] or (P.STAGES.index(p["stage"]) < P.STAGES.index("Champion") and not waits_for_battles):
                stuck.append(f"{line}: {P.display_name(p)} ({p['stage']}, lebt={p['alive']})")
        self.assertEqual(stuck, [])

    def test_or_and_battle_rules(self):
        p = P.new_egg("ver1", MORNING)
        p.update(mistakes=1, trainings=0, overfeeds=0, battles_stage=0, wins_stage=0)
        self.assertTrue(P._rule_ok(p, {"any": [{"cm": [5, None]}, {"cm": [0, 1]}]}))
        self.assertFalse(P._rule_ok(p, {"any": [{"cm": [5, None]}, {"tr": [3, None]}]}))
        self.assertFalse(P._rule_ok(p, {"btl": [4, None]}))
        p["battles_stage"], p["wins_stage"] = 4, 2
        self.assertTrue(P._rule_ok(p, {"cm": [0, 2], "btl": [4, None]}))
        self.assertTrue(P._rule_ok(p, {"wins": [2, None]}))
        self.assertFalse(P._rule_ok(p, {"jogress": "Vaccine/Data"}))
        self.assertTrue(P.needs_battles({"any": [{"btl": [4, None]}, {"jogress": "Virus"}]}))
        self.assertFalse(P.needs_battles({"any": [{"btl": [4, None]}, {"cm": [0, 2]}]}))

    def test_sleep_and_light(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 13 * 60, every=5)     # bis 22:00, Agumon (Schlafen 21:00)
        self.assertTrue(p["asleep"])
        self.assertFalse(p["light"])
        with self.assertRaises(P.Refused):
            P.feed(p, "meat", MORNING + 13 * 60)

    def test_light_left_on_is_mistake(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 12 * 60 + 30, every=5)  # 21:30 -> Koromon schläft schon
        p["light"] = True
        before = p["mistakes_total"]
        P.advance(p, p["last"] + 15)
        self.assertEqual(p["mistakes_total"], before + 1)

    def test_starving_kills(self):
        p = P.new_egg("ver1", MORNING)
        P.advance(p, MORNING + 3 * 24 * 60)
        self.assertFalse(p["alive"])

    def test_poop_makes_sick_and_medicine_cures(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 20, every=1)           # Koromon
        p["poop"] = 3
        p["poop_tick"] = P.POOP_EVERY["InTraining"] - 1
        P.advance(p, p["last"] + 1)
        self.assertTrue(p["sick"])
        P.medicine(p, p["last"])
        self.assertFalse(p["sick"])

    def test_box_freezes_time(self):
        p = P.new_egg("ver1", MORNING)
        run(p, MORNING, 20, every=1)
        p["in_box"] = True
        hunger = p["hunger"]
        P.advance(p, MORNING + 10 * 60)
        self.assertEqual(p["hunger"], hunger)
        self.assertTrue(p["alive"])


if __name__ == "__main__":
    unittest.main()
