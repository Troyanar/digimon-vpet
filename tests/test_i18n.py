"""Tests der zweisprachigen Texte (game/i18n.py, game/i18n_en.py)."""
import json
import random
import re
import string
import unittest
from datetime import datetime

from game import duel as duel_lib
from game import explore, i18n
from game import pet as P
from game.i18n import T, Text
from game.i18n_en import EN

MORNING = int(datetime(2026, 10, 22, 9, 0).timestamp() // 60)
# typische deutsche Reste, die in einer englischen Antwort nicht vorkommen dürfen
GERMAN = re.compile(r"[äöüÄÖÜß]|\b(ist|hat|Das|Ei|wieder|nicht|und|Licht)\b")


def english(obj):
    """Wie der Server antwortet, wenn das Gerät Englisch eingestellt hat."""
    return json.loads(json.dumps(i18n.localize(obj, "en"), ensure_ascii=False))


class TextTest(unittest.TestCase):
    def test_text_is_german_string_with_english(self):
        t = T("{name} isst Fleisch. Hunger +1", name="Agumon")
        self.assertIsInstance(t, str)
        self.assertEqual(t, "Agumon isst Fleisch. Hunger +1")
        self.assertEqual(t.en, "Agumon eats meat. Hunger +1")

    def test_missing_translation_stays_german(self):
        t = T("Gibt es nicht im Katalog {x}", x=1)
        self.assertEqual((t, t.en), ("Gibt es nicht im Katalog 1", "Gibt es nicht im Katalog 1"))

    def test_terms_inside_sentences_are_translated(self):
        t = T("In {area} ist es zu gefährlich – erst ab {stage}.", area=T("Urwald"), stage=T("Ultra"))
        self.assertEqual(t.en, "Jungle is too dangerous – Ultimate or higher only.")

    def test_combining_keeps_english(self):
        t = T("Licht an.") + " " + T("Licht aus.")
        self.assertEqual((t, t.en), ("Licht an. Licht aus.", "Lights on. Lights out."))
        t = "> " + T("Licht an.")
        self.assertEqual(t.en, "> Lights on.")
        j = i18n.join(", ", [T("Leckerbissen"), "Agumon", T("Glücksbringer")])
        self.assertEqual((j, j.en), ("Leckerbissen, Agumon, Glücksbringer", "Treat, Agumon, Lucky Charm"))

    def test_localize(self):
        obj = {"a": T("Licht an."), "b": [T("Licht aus."), 3, None, "frei"], "c": {"d": T("Ei")}}
        self.assertIs(i18n.localize(obj, "de"), obj)
        self.assertEqual(i18n.localize(obj, "en"), {"a": "Lights on.", "b": ["Lights out.", 3, None, "frei"],
                                                    "c": {"d": "Egg"}})
        self.assertNotIsInstance(i18n.localize(obj, "en")["a"], Text)

    def test_catalog_placeholders_match(self):
        def fields(s):
            return {f for _, f, _, _ in string.Formatter().parse(s) if f is not None}
        for de, en in EN.items():
            self.assertEqual(fields(de), fields(en), de)


class GameTextTest(unittest.TestCase):
    def test_refused_message_has_english(self):
        p = P.new_egg("ver1", MORNING)              # ein Ei macht keinen Dreck
        with self.assertRaises(P.Refused) as ctx:
            P.clean(p, MORNING)
        msg = i18n.text_of(ctx.exception)
        self.assertEqual(msg, "Hier ist schon alles sauber.")
        self.assertEqual(msg.en, "Everything is already clean.")

    def test_log_entry_stores_english(self):
        p = P.new_egg("ver1", MORNING)
        P.advance(p, MORNING + 5)
        entry = p["log"][-1]
        self.assertEqual(entry["text"], f"Das Ei ist geschlüpft: {P.display_name(p)}!")
        self.assertEqual(entry["en"], f"The egg has hatched: {P.display_name(p)}!")
        # nach dem Speichern (JSON) kommt der Eintrag wieder zweisprachig zurück
        p = json.loads(json.dumps(p))
        self.assertEqual(english(P.view(p, MORNING + 5))["log"][-1]["text"],
                         f"The egg has hatched: {P.display_name(p)}!")

    def test_view_in_english(self):
        egg = P.new_egg("ver1", MORNING)
        view = english(P.view(egg, MORNING))
        self.assertEqual((view["name"], view["stage_de"]), ("Digi-Egg", "Egg"))

        p = P.new_egg("ver1", MORNING)
        P.advance(p, MORNING + 5)
        _, msg = P.feed(p, "meat", MORNING + 5)
        self.assertEqual(english(msg), f"{P.display_name(p)} eats meat. Hunger +1")
        P._die(p, MORNING + 6, T("verhungert"))
        self.assertEqual(p["death_cause"], "verhungert")           # gespeichert wird deutsch
        p = json.loads(json.dumps(p))
        view = english(P.view(p, MORNING + 6))
        self.assertEqual(view["death_cause"], "starved")
        self.assertEqual(view["stage_de"], "Baby I")
        for entry in view["log"]:
            self.assertIsNone(GERMAN.search(entry["text"]), entry["text"])
        self.assertEqual(P.view(p, MORNING + 6)["death_cause"], "verhungert")

    def test_need_text(self):
        self.assertEqual(P.need_text("Vaccine/Data"), "ein Serum oder Daten-Digimon")
        self.assertEqual(english(P.need_text("Vaccine/Data")), "a Vaccine or Data Digimon")

    def test_explore_report_in_english(self):
        parts = [explore.egg_found("ver1", True), explore.egg_found("ver2", False), explore.ITEMS["snack"]["name"]]
        text = explore.report_text("Agumon", "wald", parts)
        # gefundene Eier heißen nur "Digi-Ei" – welche Sorte, verrät der Bericht nicht
        self.assertEqual(text, "Agumon ist zurück aus Urwald! Gefunden: ein Digi-Ei, "
                               "ein Digi-Ei (Sammlung voll – liegen gelassen), Leckerbissen.")
        self.assertEqual(text.en, "Agumon is back from Jungle! Found: a Digi-Egg, "
                                  "a Digi-Egg (collection full – left behind), Treat.")
        # nur Event-Eier verraten ihre Sorte
        self.assertEqual(explore.egg_found("halloween", True), "ein Digi-Ei Halloween")
        self.assertEqual(explore.egg_found("halloween", True).en, "a Digi-Egg Halloween")
        self.assertIsNone(GERMAN.search(english(explore.ITEMS["wunder"])["name"]))

    def test_duel_result_survives_saving(self):
        duel = {"id": 1, "status": "active", "a": 1, "b": 2,
                "data": {"names": {"a": "Mia", "b": "Tom"}, "created": 0, "round": 1, "rounds": [],
                         "shots": {}, "hp": {"a": 1, "b": 0}, "max": {"a": 3, "b": 3}}}
        duel_lib._finish(duel, {"a": None, "b": None}, "a", 10, random)
        duel["data"] = json.loads(json.dumps(duel["data"]))         # wie aus der Datenbank
        view = duel_lib.view(duel, 2, {}, 10)
        self.assertEqual(view["result"]["text"], "Mia gewinnt den Kampf!")
        self.assertEqual(english(view)["result"]["text"], "Mia wins the battle!")


if __name__ == "__main__":
    unittest.main()
