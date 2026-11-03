"""Test-Spielstand mit einem fertigen Admin-Testkonto anlegen (für Prüf-Server und Screenshots).

    python tools/dev/make_test_db.py <pfad/zur/test.db> [--pet]

Legt das Konto "Tester" (Admin, 2000 Bits, Sprache Deutsch) mit dem festen Login-Token
"testtoken-tester" an – damit kann man ohne Passwort per Cookie
"vpet_session=testtoken-tester" spielen (siehe api.py / screenshot.py). Mit --pet bekommt
"Tester" ein waches, sattes Agumon (Rookie) als aktives Digimon, sonst ein Digi-Ei.
Gibt es "Tester" schon, wird nur --pet ausgeführt. NIE auf savegame.db anwenden.
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

from game import collection, shop  # noqa: E402
from game import pet as P  # noqa: E402
from game.store import Store  # noqa: E402

TOKEN = "testtoken-tester"


def main():
    if len(sys.argv) < 2 or os.path.basename(sys.argv[1]) == "savegame.db":
        sys.exit(__doc__)
    store = Store(sys.argv[1])
    user = store.user_by_name("Tester")
    now = int(time.time() // 60)
    if not user:
        uid = store.add_user("Tester", "x", "y", True)       # kein echtes Passwort: Login nur per Token
        store.add_session(TOKEN, uid)
        collection.new_egg(store, str(uid), now, line="ver1")
        shop.add(store, str(uid), 2000)
        store.set_meta(f"lang:{uid}", "de")
        user = store.user_by_name("Tester")
    if "--pet" in sys.argv:
        from test_battle import rookie                      # Agumon, Hunger/Kraft voll
        pet = rookie()
        P.shift_times(pet, now - pet["last"])               # Uhren auf jetzt
        pet["last"] = now
        pet["asleep"], pet["light"] = False, True
        store.add_pet(str(user["id"]), pet)                 # wird aktiv, das alte kommt nicht weg
    store.db.commit()
    print(f"ok - Konto Tester, Cookie vpet_session={TOKEN}")


if __name__ == "__main__":
    main()
