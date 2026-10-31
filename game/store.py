"""Speicherung in einer SQLite-Datei (savegame.db)."""
import hashlib
import json
import os
import sqlite3
import threading
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / os.environ.get("VPET_DB", "savegame.db")


def _upgrade(pet):
    """Digimon aus älteren Versionen um neue Felder ergänzen (sonst KeyError)."""
    from . import pet as petlib          # spät importieren: store soll ohne Spiel-Logik laden
    return petlib.upgrade(pet)


SESSION_DAYS = 90          # so lange bleibt man angemeldet


def token_hash(token):
    """Sitzungen werden nur als Prüfsumme gespeichert – ein heruntergeladenes
    Backup enthält so keine gültigen Anmeldungen."""
    return hashlib.sha256(str(token).encode("utf8")).hexdigest()


class Store:
    def __init__(self, path=DB_PATH):
        self.lock = threading.RLock()
        self.db_path = path
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.migrate()

    def migrate(self):
        """Tabellen anlegen bzw. ältere Spielstände (auch eingespielte Backups)
        auf den aktuellen Stand bringen."""
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 0,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                pw_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS duels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                a INTEGER NOT NULL,
                b INTEGER NOT NULL,
                status TEXT NOT NULL,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                a INTEGER NOT NULL,
                b INTEGER NOT NULL,
                status TEXT NOT NULL,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time INTEGER NOT NULL,
                who TEXT NOT NULL,
                text TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created INTEGER NOT NULL
            );
        """)
        # ältere Spielstände um neue Spalten erweitern
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(users)")}
        if "banned" not in columns:
            self.db.execute("ALTER TABLE users ADD COLUMN banned INTEGER NOT NULL DEFAULT 0")
        if "last_seen" not in columns:
            self.db.execute("ALTER TABLE users ADD COLUMN last_seen INTEGER NOT NULL DEFAULT 0")
        self.db.executescript("""
            CREATE INDEX IF NOT EXISTS pets_owner ON pets (owner, active);
            CREATE INDEX IF NOT EXISTS duels_a ON duels (a);
            CREATE INDEX IF NOT EXISTS duels_b ON duels (b);
            CREATE INDEX IF NOT EXISTS requests_a ON requests (kind, a);
            CREATE INDEX IF NOT EXISTS requests_b ON requests (kind, b);
        """)
        # abgelaufene Sitzungen und alte (unverschlüsselte) Sitzungen entfernen
        self.db.execute("DELETE FROM sessions WHERE created < ? OR length(token) != 64",
                        (int(time.time()) - SESSION_DAYS * 86400,))
        self.db.commit()

    # ------------------------------------------------------------ meta
    def get_meta(self, key, default=None):
        row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_meta(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES (?, ?)", (key, json.dumps(value)))
        self.db.commit()

    # ------------------------------------------------------------ Konten
    def user_count(self):
        return self.db.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def add_user(self, name, pw_hash, salt, is_admin):
        cur = self.db.execute(
            "INSERT INTO users (name, pw_hash, salt, is_admin, created) VALUES (?, ?, ?, ?, ?)",
            (name, pw_hash, salt, int(is_admin), int(time.time())))
        self.db.commit()
        return cur.lastrowid

    def user_by_name(self, name):
        row = self.db.execute(
            "SELECT id, name, pw_hash, salt, is_admin, banned FROM users WHERE name=?", (name,)).fetchone()
        return dict(zip(("id", "name", "pw_hash", "salt", "is_admin", "banned"), row)) if row else None

    def users_detail(self):
        rows = self.db.execute("SELECT id, name, is_admin, banned, created, last_seen FROM users ORDER BY id")
        return [dict(zip(("id", "name", "is_admin", "banned", "created", "last_seen"), r)) for r in rows]

    def set_flag(self, user_id, column, value):
        assert column in ("is_admin", "banned")
        self.db.execute(f"UPDATE users SET {column}=? WHERE id=?", (int(bool(value)), user_id))
        self.db.commit()

    def admin_count(self):
        return self.db.execute("SELECT COUNT(*) FROM users WHERE is_admin=1 AND banned=0").fetchone()[0]

    def touch(self, user_id, now):
        """'Zuletzt aktiv' speichern (höchstens einmal pro Minute schreiben)."""
        self.db.execute("UPDATE users SET last_seen=? WHERE id=? AND last_seen < ?", (int(now), user_id, int(now) - 60))
        self.db.commit()

    def delete_user(self, user_id):
        """Konto mit allen Digimon, Sitzungen und offenen Angeboten löschen."""
        self.db.execute("DELETE FROM pets WHERE owner=?", (str(user_id),))
        self.db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        self.db.execute("UPDATE requests SET status='cancelled' WHERE (a=? OR b=?) AND status IN ('pending','countered')",
                        (user_id, user_id))
        self.db.execute("UPDATE duels SET status='aborted' WHERE (a=? OR b=?) AND status IN ('pending','active')",
                        (user_id, user_id))
        self.db.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.db.commit()

    # ------------------------------------------------------------ Protokoll
    def log_activity(self, who, text):
        self.db.execute("INSERT INTO activity (time, who, text) VALUES (?, ?, ?)", (int(time.time()), who, text))
        self.db.execute("DELETE FROM activity WHERE id <= (SELECT MAX(id) - 1000 FROM activity)")
        self.db.commit()

    def activity(self, limit=100):
        rows = self.db.execute("SELECT time, who, text FROM activity ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(zip(("time", "who", "text"), r)) for r in rows]

    def counts(self):
        one = lambda sql: self.db.execute(sql).fetchone()[0]
        return {
            "users": one("SELECT COUNT(*) FROM users"),
            "pets": one("SELECT COUNT(*) FROM pets"),
            "duels": one("SELECT COUNT(*) FROM duels WHERE status='done'"),
            "trades": one("SELECT COUNT(*) FROM requests WHERE kind='trade' AND status='done'"),
            "jogress": one("SELECT COUNT(*) FROM requests WHERE kind='jogress' AND status='done'"),
        }

    def user_by_id(self, user_id):
        row = self.db.execute(
            "SELECT id, name, pw_hash, salt, is_admin, banned FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(zip(("id", "name", "pw_hash", "salt", "is_admin", "banned"), row)) if row else None

    def set_password(self, user_id, pw_hash, salt):
        self.db.execute("UPDATE users SET pw_hash=?, salt=? WHERE id=?", (pw_hash, salt, user_id))
        self.db.commit()

    def delete_user_sessions(self, user_id, keep=None):
        """Meldet einen Spieler überall ab (außer optional in der Sitzung `keep`)."""
        self.db.execute("DELETE FROM sessions WHERE user_id=? AND token IS NOT ?",
                        (user_id, token_hash(keep) if keep else None))
        self.db.commit()

    def all_users(self):
        return [dict(zip(("id", "name", "is_admin"), row))
                for row in self.db.execute("SELECT id, name, is_admin FROM users")]

    def add_session(self, token, user_id):
        self.db.execute("INSERT INTO sessions VALUES (?, ?, ?)", (token_hash(token), user_id, int(time.time())))
        self.db.commit()

    def user_by_session(self, token):
        if not isinstance(token, str):
            return None
        row = self.db.execute("""
            SELECT u.id, u.name, u.is_admin FROM sessions s JOIN users u ON u.id = s.user_id
            WHERE s.token=? AND u.banned=0 AND s.created > ?""",
            (token_hash(token), int(time.time()) - SESSION_DAYS * 86400)).fetchone()
        return dict(zip(("id", "name", "is_admin"), row)) if row else None

    def delete_session(self, token):
        self.db.execute("DELETE FROM sessions WHERE token=?", (token_hash(token),))
        self.db.commit()

    def adopt_local_pets(self, user_id):
        """Digimon aus der Zeit vor dem Login gehören dem ersten Konto."""
        self.db.execute("UPDATE pets SET owner=? WHERE owner='local'", (str(user_id),))
        self.db.commit()

    # ------------------------------------------------------------ Kämpfe gegen Freunde
    def add_duel(self, a, b, data):
        cur = self.db.execute("INSERT INTO duels (a, b, status, data) VALUES (?, ?, 'pending', ?)",
                              (a, b, json.dumps(data)))
        self.db.commit()
        return self.get_duel(cur.lastrowid)

    def get_duel(self, duel_id):
        row = self.db.execute("SELECT id, a, b, status, data FROM duels WHERE id=?", (duel_id,)).fetchone()
        if not row:
            return None
        return {"id": row[0], "a": row[1], "b": row[2], "status": row[3], "data": json.loads(row[4])}

    def latest_duel(self, user_id):
        """Der neueste Kampf, an dem der Spieler beteiligt ist."""
        row = self.db.execute("SELECT id FROM duels WHERE a=? OR b=? ORDER BY id DESC LIMIT 1",
                              (user_id, user_id)).fetchone()
        return self.get_duel(row[0]) if row else None

    def save_duel(self, duel):
        self.db.execute("UPDATE duels SET status=?, data=? WHERE id=?",
                        (duel["status"], json.dumps(duel["data"]), duel["id"]))
        self.db.commit()

    # ------------------------------------------------------------ Tausch & Jogress-Anfragen
    def add_request(self, kind, a, b, data):
        cur = self.db.execute("INSERT INTO requests (kind, a, b, status, data) VALUES (?, ?, ?, 'pending', ?)",
                              (kind, a, b, json.dumps(data)))
        self.db.commit()
        return self.get_request(cur.lastrowid)

    def get_request(self, req_id):
        row = self.db.execute("SELECT id, kind, a, b, status, data FROM requests WHERE id=?", (req_id,)).fetchone()
        if not row:
            return None
        return dict(zip(("id", "kind", "a", "b", "status"), row[:5]), data=json.loads(row[5]))

    def requests_for(self, user_id, kind, statuses, limit=200):
        marks = ",".join("?" * len(statuses))
        rows = self.db.execute(
            f"SELECT id FROM requests WHERE kind=? AND (a=? OR b=?) AND status IN ({marks}) "
            f"ORDER BY id DESC LIMIT ?", (kind, user_id, user_id, *statuses, limit)).fetchall()
        return [self.get_request(r[0]) for r in rows]

    def save_request(self, req):
        self.db.execute("UPDATE requests SET status=?, data=? WHERE id=?",
                        (req["status"], json.dumps(req["data"]), req["id"]))
        self.db.commit()

    def pet_by_id(self, pet_id):
        row = self.db.execute("SELECT id, owner, active, data FROM pets WHERE id=?", (pet_id,)).fetchone()
        if not row:
            return None
        pet = _upgrade(json.loads(row[3]))
        pet["id"], pet["owner"], pet["active"] = row[0], row[1], bool(row[2])
        return pet

    def move_pet(self, pet_id, new_owner):
        self.db.execute("UPDATE pets SET owner=?, active=0 WHERE id=?", (new_owner, pet_id))
        self.db.commit()

    # ------------------------------------------------------------ Digimon
    def active_pet(self, owner):
        row = self.db.execute(
            "SELECT id, data FROM pets WHERE owner=? AND active=1", (owner,)).fetchone()
        if not row:
            return None
        pet = _upgrade(json.loads(row[1]))
        pet["id"] = row[0]
        return pet

    def add_pet(self, owner, pet, active=True):
        if active:
            self.db.execute("UPDATE pets SET active=0 WHERE owner=?", (owner,))
        cur = self.db.execute("INSERT INTO pets (owner, active, data) VALUES (?, ?, ?)",
                              (owner, int(active), json.dumps(pet)))
        self.db.commit()
        pet["id"] = cur.lastrowid
        return pet

    def save_pet(self, pet, active=None):
        body = {k: v for k, v in pet.items() if k not in ("id", "active", "owner")}
        self.db.execute("UPDATE pets SET data=? WHERE id=?", (json.dumps(body), pet["id"]))
        if active is not None:
            self.db.execute("UPDATE pets SET active=? WHERE id=?", (int(active), pet["id"]))
        self.db.commit()

    def all_pets(self, owner):
        """Alle Digimon eines Spielers (aktiv, Sammlung, verstorben), neueste zuerst."""
        out = []
        for pet_id, active, data in self.db.execute(
                "SELECT id, active, data FROM pets WHERE owner=? ORDER BY id DESC", (owner,)):
            pet = _upgrade(json.loads(data))
            pet["id"], pet["active"] = pet_id, bool(active)
            out.append(pet)
        return out

    def every_pet(self):
        """Alle Digimon aller Spieler (z. B. nach dem Einspielen eines Backups)."""
        out = []
        for pet_id, owner, active, data in self.db.execute("SELECT id, owner, active, data FROM pets"):
            pet = _upgrade(json.loads(data))
            pet["id"], pet["owner"], pet["active"] = pet_id, owner, bool(active)
            out.append(pet)
        return out

    def delete_pet(self, owner, pet_id):
        self.db.execute("DELETE FROM pets WHERE owner=? AND id=?", (owner, pet_id))
        self.db.commit()
