"""Fragenkatalog beim ersten Start (wie bei Pokémon Mystery Dungeon).

Neue Konten bekommen ihr erstes Digi-Ei nicht zufällig: Erst beantwortet man ein
paar Fragen (QUESTIONS_ASKED aus dem Pool), jede Antwort gibt Punkte für einen oder
zwei Persönlichkeitstypen. Der Typ mit den meisten Punkten gewinnt (Gleichstand:
Zufall), und man bekommt ein zufälliges Ei, das zu diesem Typ passt. Zusammen
decken die Typen alle Eier ab – jedes Ei kann also herauskommen.

Offen ist der Fragenkatalog, solange meta "starter:<owner>" gesetzt ist (bei der
Registrierung). Bestehende Konten bekommen ihn nie.
"""
import random

from . import data
from .i18n import T

QUESTIONS_ASKED = 6
MIN_ANSWERS = 5

# Persönlichkeitstypen -> passende Eier (nach den Rookies der Linie ausgesucht)
TYPES = {
    "brave": {
        "name": T("mutig"),
        "text": T("Du stellst dich jeder Herausforderung und gehst voran, wenn andere zögern. Manchmal stürmst "
                  "du los, bevor du nachdenkst – aber wenn es brenzlig wird, ist auf dich Verlass."),
        "eggs": ["ver1", "sakumon", "doru20", "veemon", "fufumon"],          # Agumon, Dracomon, Dorumon, Veemon …
    },
    "calm": {
        "name": T("ruhig"),
        "text": T("Du bleibst gelassen, auch wenn es stürmt. Du hörst gut zu und denkst nach, bevor du handelst. "
                  "Deine Freunde schätzen dich als Ruhepol."),
        "eggs": ["ver2", "zerimon", "gomamon"],                              # Gabumon, Gomamon, Syakomon …
    },
    "gentle": {
        "name": T("sanft"),
        "text": T("Du kümmerst dich gern um andere und liebst die Natur. Mit Geduld und einem großen Herzen "
                  "bringst du alles zum Wachsen."),
        "eggs": ["ver4", "nyokimon", "wormmon", "petitmon", "ver6"],         # Palmon, Floramon, Wormmon, Lalamon …
    },
    "clever": {
        "name": T("schlau"),
        "text": T("Du willst wissen, wie die Dinge funktionieren, und findest für jedes Problem eine Lösung. "
                  "Rätsel, Technik und neue Ideen sind genau dein Ding."),
        "eggs": ["ver5", "mokumon", "choromon", "algomoni", "pururumon"],    # Hagurumon, Tentomon, Keramon …
    },
    "mysterious": {
        "name": T("geheimnisvoll"),
        "text": T("Du gehst deinen eigenen Weg, liebst Überraschungen und bist ein kleines bisschen frech. "
                  "Nicht jeder sieht gleich, was alles in dir steckt."),
        "eggs": ["ver3", "impmon", "cotsucomon", "cocomon", "kuramon", "dokimon"],   # DemiDevimon, Impmon, Dracmon …
    },
    "cheerful": {
        "name": T("fröhlich"),
        "text": T("Mit deiner guten Laune steckst du alle an, und neue Freunde findest du überall. "
                  "Mit dir wird es nie langweilig!"),
        "eggs": ["salamon", "tsubumon", "puttimon", "chibickmon", "ketomon"],  # Salamon, Lunamon, Guilmon, Lopmon …
    },
}

# Fragen-Pool: (Frage, [(Antwort, {Typ: Punkte}), …])
QUESTIONS = [
    (T("Ein Freund ist traurig. Was machst du?"), [
        (T("Ich bringe ihn zum Lachen."), {"cheerful": 2}),
        (T("Ich höre ihm einfach zu."), {"calm": 2, "gentle": 1}),
        (T("Ich finde heraus, was los ist, und löse das Problem."), {"clever": 2}),
        (T("Ich nehme ihn mit auf ein Abenteuer."), {"brave": 2}),
    ]),
    (T("Im Wald findest du eine dunkle Höhle. Was tust du?"), [
        (T("Rein da, sofort!"), {"brave": 2}),
        (T("Erst mal baue ich mir eine Taschenlampe."), {"clever": 2}),
        (T("Ich warte versteckt, ob etwas herauskommt."), {"mysterious": 2}),
        (T("Lieber nicht – draußen ist es so schön."), {"gentle": 1, "calm": 1}),
    ]),
    (T("Wo bist du am liebsten?"), [
        (T("In einer Arena, wo etwas los ist"), {"brave": 2}),
        (T("An einem ruhigen Strand"), {"calm": 2}),
        (T("In einem Garten voller Blumen"), {"gentle": 2}),
        (T("In einer Werkstatt voller Geräte"), {"clever": 2}),
    ]),
    (T("Welche Tageszeit magst du am liebsten?"), [
        (T("Den frühen Morgen, wenn alles erwacht"), {"gentle": 1, "cheerful": 1}),
        (T("Den Mittag, wenn die Sonne brennt"), {"brave": 2}),
        (T("Den Abend am Wasser"), {"calm": 2}),
        (T("Die Nacht"), {"mysterious": 2}),
    ]),
    (T("Bei einem Spiel liegst du weit hinten. Was denkst du?"), [
        (T("Jetzt erst recht!"), {"brave": 2}),
        (T("Ich brauche eine bessere Taktik."), {"clever": 2}),
        (T("Egal – Hauptsache, es macht Spaß!"), {"cheerful": 2}),
        (T("Ich habe noch einen Trick im Ärmel …"), {"mysterious": 2}),
    ]),
    (T("Jemand verrät dir ein Geheimnis. Was machst du?"), [
        (T("Ich behalte es für immer für mich."), {"calm": 2}),
        (T("Ich sammle Geheimnisse. Das ist schon mein drittes heute."), {"mysterious": 2}),
        (T("Ich überlege, wie ich helfen kann."), {"gentle": 2}),
        (T("Ich platze fast – aber ich halte durch!"), {"cheerful": 2}),
    ]),
    (T("Du bekommst ein Geschenk. Was soll drin sein?"), [
        (T("Ein Bausatz für einen Roboter"), {"clever": 2}),
        (T("Samen für eine ganz seltene Pflanze"), {"gentle": 2}),
        (T("Eine Karte zu einem versteckten Schatz"), {"mysterious": 1, "brave": 1}),
        (T("Karten für ein großes Fest mit Freunden"), {"cheerful": 2}),
    ]),
    (T("Wie würden dich deine Freunde beschreiben?"), [
        (T("Mutig und ehrlich"), {"brave": 2}),
        (T("Entspannt und zuverlässig"), {"calm": 2}),
        (T("Lieb und geduldig"), {"gentle": 2}),
        (T("Witzig und ein bisschen laut"), {"cheerful": 2}),
        (T("Schwer zu durchschauen"), {"mysterious": 2}),
    ]),
    (T("Ein Gewitter zieht auf. Was machst du?"), [
        (T("Ich beobachte die Blitze. Wie funktionieren die eigentlich?"), {"clever": 2}),
        (T("Ich kuschle mich ein und lese ein Buch."), {"calm": 2}),
        (T("Ich renne lachend durch den Regen!"), {"cheerful": 1, "brave": 1}),
        (T("Ich mag die Stimmung – ein bisschen unheimlich, ein bisschen schön."), {"mysterious": 2}),
    ]),
    (T("Welches Tier passt am besten zu dir?"), [
        (T("Ein Löwe"), {"brave": 2}),
        (T("Ein Delfin"), {"calm": 1, "cheerful": 1}),
        (T("Eine Eule"), {"clever": 1, "mysterious": 1}),
        (T("Ein Hase"), {"gentle": 2}),
    ]),
    (T("Du hast einen ganzen Tag frei. Was machst du?"), [
        (T("Etwas Neues ausprobieren – gern auch etwas Wildes"), {"brave": 2}),
        (T("Ausschlafen und den Tag genießen"), {"calm": 2}),
        (T("Etwas bauen oder tüfteln"), {"clever": 2}),
        (T("Mit allen Freunden etwas unternehmen"), {"cheerful": 2}),
    ]),
    (T("Ihr spielt Theater. Welche Rolle willst du?"), [
        (T("Den Helden, der alle rettet"), {"brave": 2}),
        (T("Den geheimnisvollen Fremden"), {"mysterious": 2}),
        (T("Den klugen Erfinder"), {"clever": 2}),
        (T("Die gute Fee, die allen hilft"), {"gentle": 2}),
    ]),
    (T("Jemand ist gemein zu einem kleineren Kind. Was tust du?"), [
        (T("Ich gehe sofort dazwischen."), {"brave": 2}),
        (T("Ich tröste das Kind."), {"gentle": 2}),
        (T("Ich hole Hilfe und erkläre ruhig, was passiert ist."), {"calm": 2}),
        (T("Ich spiele dem Fiesling später einen Streich."), {"mysterious": 2}),
    ]),
    (T("Was ist dir am wichtigsten?"), [
        (T("Stärker werden"), {"brave": 2}),
        (T("Frieden und Ruhe"), {"calm": 2}),
        (T("Neues lernen"), {"clever": 2}),
        (T("Spaß mit Freunden"), {"cheerful": 2}),
        (T("Frei sein"), {"mysterious": 2}),
    ]),
]


def _key(owner):
    return f"starter:{owner}"


def start(store, owner):
    """Nach der Registrierung: Fragenkatalog statt Zufalls-Ei."""
    store.set_meta(_key(owner), True)


def pending(store, owner):
    return bool(store.get_meta(_key(owner), False))


def questions(rng=random):
    """Eine zufällige Auswahl Fragen (für den Browser: ids + Texte)."""
    picked = rng.sample(range(len(QUESTIONS)), QUESTIONS_ASKED)
    return [{"id": i, "text": QUESTIONS[i][0], "answers": [a for a, _ in QUESTIONS[i][1]]} for i in picked]


def evaluate(answers, rng=random):
    """answers: [[Frage-id, Antwort-Nr.], …] -> (Typ, Ei-Linie). ValueError bei Unsinn."""
    if not isinstance(answers, list) or not MIN_ANSWERS <= len(answers) <= len(QUESTIONS):
        raise ValueError(T("Bitte beantworte alle Fragen."))
    score = {t: 0 for t in TYPES}
    seen = set()
    for item in answers:
        if not (isinstance(item, list) and len(item) == 2 and all(type(x) is int for x in item)):
            raise ValueError(T("Bitte beantworte alle Fragen."))
        q, a = item
        if not 0 <= q < len(QUESTIONS) or q in seen or not 0 <= a < len(QUESTIONS[q][1]):
            raise ValueError(T("Bitte beantworte alle Fragen."))
        seen.add(q)
        for kind, points in QUESTIONS[q][1][a][1].items():
            score[kind] += points
    best = max(score.values())
    kind = rng.choice([t for t, s in score.items() if s == best])
    eggs = [line for line in TYPES[kind]["eggs"] if line in data.LINES] or list(data.NORMAL_LINES)
    return kind, rng.choice(eggs)


def finish(store, owner):
    store.set_meta(_key(owner), False)


def result_view(kind, line):
    t = TYPES[kind]
    return {"key": kind, "name": t["name"], "text": t["text"], "egg": data.line_name(line)}
