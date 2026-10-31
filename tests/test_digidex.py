"""Tests für die Digidex-Daten (static/digidex.json).  Starten mit:  python -m unittest"""
import json
import re
import unittest
from pathlib import Path

from game import data

DEX = json.loads((Path(__file__).resolve().parent.parent / "static" / "digidex.json").read_text(encoding="utf8"))


class DigidexTest(unittest.TestCase):
    def test_entries_belong_to_game_digimon(self):
        self.assertTrue(set(map(int, DEX)) <= set(data.PLAYABLE))
        self.assertGreater(len(DEX), 0.9 * len(data.PLAYABLE))           # fast alle haben einen Eintrag

    def test_texts_are_german_and_use_game_terms(self):
        for dex, entry in DEX.items():
            text = entry["description"]
            self.assertNotIn("Impfstoff", text)
            # Attackennamen dürfen englisch sein ("Burning the Dragon") – ganze englische Sätze nicht
            outside_quotes = re.sub(r"„[^“]*“", "", text)
            english = len(re.findall(r"\b(the|and|which|with|its|is)\b", outside_quotes))
            self.assertLess(english, 3, data.DIGIMON[int(dex)]["name"])
        described = sum(1 for e in DEX.values() if e["description"])
        self.assertGreater(described, 0.95 * len(DEX))

    def test_digimon_names_as_in_game(self):
        """Alte / japanische Namen der Digi-API sind durch die Spielnamen ersetzt (tools/build_digidex.py)."""
        en = json.loads((Path(__file__).resolve().parent.parent / "static" / "digidex_en.json").read_text(encoding="utf8"))
        old = re.compile(r"\b(Growmons?|EBEmon|DORUgoramon|Queenbeemon|Tyranomon|Cockatrimon|Metal Garurumon|Holy Angemon)\b")
        for texts in (DEX, en):
            for dex, entry in texts.items():
                self.assertIsNone(old.search(entry["description"]), data.DIGIMON[int(dex)]["name"])
        # Arten und Attacken bleiben, wie sie sind
        self.assertIn("Demon-species", " ".join(e["description"] for e in en.values()))
        self.assertIn("Gokumon", " ".join(e["description"] for e in DEX.values()))


if __name__ == "__main__":
    unittest.main()
