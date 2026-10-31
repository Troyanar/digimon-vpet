"""Legt ein Admin-Konto an oder setzt sein Passwort neu (und hebt eine Sperre auf).

Aufruf (Server vorher beenden):
    python tools/admin_account.py <name>              (fragt das Passwort verdeckt ab)
    python tools/admin_account.py <name> <passwort>

Das Passwort steht absichtlich nicht im Code: wer den Code sieht, soll nicht
automatisch das Admin-Passwort kennen. Ohne Passwort auf der Kommandozeile
landet es auch nicht im Befehlsverlauf.
"""
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game import accounts                     # noqa: E402
from game.store import Store                  # noqa: E402


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    name = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) == 3 else getpass.getpass("Passwort: ")
    if not accounts.NAME_RE.match(name):
        sys.exit("Name: 3–20 Zeichen, nur Buchstaben, Zahlen, - und _.")
    if not accounts.MIN_PASSWORD <= len(password) <= accounts.MAX_PASSWORD:
        sys.exit(f"Passwort: mindestens {accounts.MIN_PASSWORD} Zeichen.")
    store = Store()
    pw_hash, salt = accounts.new_password_hash(password)
    user = store.user_by_name(name)
    if user:
        store.set_password(user["id"], pw_hash, salt)
        store.set_flag(user["id"], "is_admin", True)
        store.set_flag(user["id"], "banned", False)
        store.delete_user_sessions(user["id"])
        print(f"Konto '{user['name']}' ist Admin (nicht gesperrt), Passwort neu gesetzt.")
    else:
        user_id = store.add_user(name, pw_hash, salt, is_admin=True)
        print(f"Admin-Konto '{name}' angelegt (Nr. {user_id}).")


if __name__ == "__main__":
    main()
