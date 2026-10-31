"""Zweisprachige Texte (Deutsch / Englisch).

Im Code stehen alle Texte weiter auf Deutsch. ``T("…")`` macht daraus einen
``Text``: ein ganz normaler (deutscher) String, der zusätzlich seine englische
Fassung in ``.en`` mitträgt. Die Übersetzungen stehen in game/i18n_en.py –
Schlüssel ist die deutsche Vorlage MIT Platzhaltern:

    T("{name} isst Fleisch. Hunger +1", name=name)
    -> deutsch: "Agumon isst Fleisch. Hunger +1", .en: "Agumon eats meat. Hunger +1"

Erst beim Senden an den Browser wird die Sprache gewählt (``localize``, im
Server per Cookie "vpet_lang"). Fehlt eine Übersetzung, bleibt es deutsch.

Wichtig: f-Strings und ``" ".join`` machen aus einem Text wieder einen rein
deutschen String – Texte deshalb mit ``T(…)``, ``+`` oder ``join`` zusammensetzen.
"""
from .i18n_en import EN

LANGS = ("de", "en")


class Text(str):
    """Deutscher Text (der str-Wert) mit englischer Fassung in ``.en``."""

    def __new__(cls, de, en=None):
        obj = super().__new__(cls, de)
        obj.en = str(de) if en is None else str(en)
        return obj

    def __add__(self, other):
        return Text(str.__add__(self, str(other)), self.en + en_of(other))

    def __radd__(self, other):
        return Text(str(other) + str(self), en_of(other) + self.en)

    def in_lang(self, lang):
        return self.en if lang == "en" else str(self)


def en_of(value):
    """Die englische Fassung (bei normalen Strings: der String selbst)."""
    return value.en if isinstance(value, Text) else str(value)


def T(template, **args):
    """Text aus einer deutschen Vorlage – englisch aus EN (sonst die deutsche Vorlage)."""
    en_template = EN.get(template, template)
    if not args:
        return Text(template, en_template)
    return Text(template.format(**args), en_template.format(**{k: en_of(v) for k, v in args.items()}))


def join(sep, parts):
    """Wie ``sep.join(parts)``, behält aber die englische Fassung."""
    parts = list(parts)
    return Text(str(sep).join(str(p) for p in parts), en_of(sep).join(en_of(p) for p in parts))


def stored(entry_text, entry_en=None):
    """Gespeicherten Text (z. B. Tagebuch: "text" + "en") wieder zum Text machen."""
    return Text(entry_text, entry_en if entry_en is not None else EN.get(entry_text, entry_text))


def text_of(error):
    """Die Meldung einer Exception – als Text, falls sie einer ist (``str(e)`` verliert .en)."""
    if error.args and isinstance(error.args[0], str):
        return error.args[0]
    return str(error)


def localize(obj, lang):
    """Alle Texte in einer Antwort (dicts/Listen beliebig tief) in die gewünschte Sprache."""
    if lang != "en":
        return obj
    if isinstance(obj, Text):
        return obj.en
    if isinstance(obj, dict):
        return {k: localize(v, lang) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [localize(v, lang) for v in obj]
    return obj
