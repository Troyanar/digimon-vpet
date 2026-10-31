"""Jeder Text im Code muss eine englische Fassung haben.  Starten mit:  python -m unittest

Server: jedes T("…") mit festem Text in server.py und game/*.py steht in game/i18n_en.py (EN).
Browser: jedes tr("…") mit festem Text in static/game.js, hilfe.js, rules.js steht in einer
der Dateien static/i18n/en-*.js. Neue Texte also immer gleich mit übersetzen.
"""
import ast
import re
import unittest
from pathlib import Path

from game.i18n_en import EN

ROOT = Path(__file__).resolve().parent.parent
JS_KEY = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*:', re.M)          # "deutsch": … in en-*.js
JS_TR = re.compile(r'\btr\(\s*"((?:[^"\\]|\\.)*)"\s*([,)+])')      # tr("deutsch" …


def _js_unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def server_templates():
    """(Datei, Zeile, Text) für jedes T("…") mit festem Text."""
    for path in [ROOT / "server.py", *sorted((ROOT / "game").glob("*.py"))]:
        if path.name == "i18n_en.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "T"
                    and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                yield path.name, node.lineno, node.args[0].value


def browser_keys():
    keys = set()
    for path in (ROOT / "static" / "i18n").glob("en-*.js"):
        keys |= {_js_unescape(k) for k in JS_KEY.findall(path.read_text(encoding="utf8"))}
    return keys


def browser_texts():
    """(Datei, Text) für jedes tr("…") mit festem, nicht zusammengesetztem Text."""
    for name in ("game.js", "hilfe.js", "rules.js"):
        for text, after in JS_TR.findall((ROOT / "static" / name).read_text(encoding="utf8")):
            if after != "+":                            # tr("a" + b) prüft man von Hand
                yield name, _js_unescape(text)


class CompleteTest(unittest.TestCase):
    def test_every_server_text_has_english(self):
        missing = sorted({f"{f}:{line}: {text}" for f, line, text in server_templates() if text not in EN})
        self.assertEqual(missing, [], "Diese T()-Texte fehlen in game/i18n_en.py")

    def test_every_browser_text_has_english(self):
        keys = browser_keys()
        missing = sorted({f"{f}: {text}" for f, text in browser_texts() if text not in keys})
        self.assertEqual(missing, [], "Diese tr()-Texte fehlen in static/i18n/en-*.js")


if __name__ == "__main__":
    unittest.main()
