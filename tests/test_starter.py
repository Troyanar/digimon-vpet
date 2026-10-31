"""Tests für den Fragenkatalog beim ersten Start.  Starten mit:  python -m unittest"""
import random
import unittest

from game import data, i18n, starter
from game.i18n_en import EN
from game.store import Store


def all_for(kind):
    """Antworten, die möglichst viele Punkte für `kind` geben (je Frage die beste Antwort)."""
    answers = []
    for q, (_, options) in enumerate(starter.QUESTIONS[:starter.QUESTIONS_ASKED]):
        best = max(range(len(options)), key=lambda a: options[a][1].get(kind, 0))
        answers.append([q, best])
    return answers


class StarterTest(unittest.TestCase):
    def test_types_cover_every_egg_once(self):
        eggs = [line for t in starter.TYPES.values() for line in t["eggs"]]
        self.assertEqual(sorted(eggs), sorted(data.NORMAL_LINES))      # Event-Eier nicht

    def test_every_type_can_win(self):
        # mit passenden Antworten aus dem ganzen Pool gewinnt jeder Typ eindeutig
        for kind in starter.TYPES:
            answers = []
            for q, (_, options) in enumerate(starter.QUESTIONS):
                best = max(range(len(options)), key=lambda a: options[a][1].get(kind, 0))
                answers.append([q, best])
            got, line = starter.evaluate(answers)
            self.assertEqual(got, kind)
            self.assertIn(line, starter.TYPES[kind]["eggs"])

    def test_questions_are_random_and_complete(self):
        qs = starter.questions(random.Random(1))
        self.assertEqual(len(qs), starter.QUESTIONS_ASKED)
        self.assertEqual(len({q["id"] for q in qs}), starter.QUESTIONS_ASKED)
        for q in qs:
            self.assertGreaterEqual(len(q["answers"]), 2)

    def test_bad_answers(self):
        good = all_for("brave")
        for bad in (None, [], good[:2], good + [good[0]],          # zu wenige / doppelt
                    [[0, 99]] * 6, [["0", 1]] * 6, [[999, 0]] + good[1:]):
            with self.assertRaises(ValueError):
                starter.evaluate(bad)

    def test_pending_flag(self):
        store = Store(":memory:")
        self.assertFalse(starter.pending(store, "1"))
        starter.start(store, "1")
        self.assertTrue(starter.pending(store, "1"))
        self.assertFalse(starter.pending(store, "2"))
        starter.finish(store, "1")
        self.assertFalse(starter.pending(store, "1"))

    def test_everything_has_english(self):
        texts = [t[k] for t in starter.TYPES.values() for k in ("name", "text")]
        for question, options in starter.QUESTIONS:
            texts.append(question)
            texts += [a for a, _ in options]
        missing = [str(t) for t in texts if str(t) not in EN]
        self.assertEqual(missing, [])
        view = i18n.localize(starter.result_view("calm", "ver2"), "en")
        self.assertEqual(view["name"], "calm")
        self.assertEqual(view["egg"], "Digi-Egg Version 2")


if __name__ == "__main__":
    unittest.main()
