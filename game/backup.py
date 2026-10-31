"""Automatische Backups des Spielstands (Ordner backups/).

Wiederherstellen: am einfachsten im Admin-Bereich ("Einspielen"). Von Hand:
Server beenden, die gewünschte Datei aus backups/ nach savegame.db kopieren,
Server starten.
"""
import re
import sqlite3
import time
from pathlib import Path

BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups"
EVERY = 6 * 3600                # automatisch alle 6 Stunden
# so viele Backups bleiben je Art erhalten – getrennt gezählt, damit z. B. viele
# Neustarts nicht die automatischen Backups verdrängen
KEEP = {"auto": 28, "start": 5, "manuell": 20, "vor-einspielen": 5}
KEEP_OTHER = 10
# Name des Spielstands (savegame / testgame ...): jeder Spielstand sieht nur seine
# eigenen Backups – so landet nie ein Test-Stand im echten Spiel
PREFIX = "savegame"


def use_store(store):
    global PREFIX
    PREFIX = Path(str(store.db_path)).stem if store.db_path != ":memory:" else "memory"


def _pattern():
    # PREFIX-JJJJ-MM-TT_hh-mm-ss-art(-n).db
    return re.compile(rf"^{re.escape(PREFIX)}-\d{{4}}-\d\d-\d\d_\d\d-\d\d-\d\d-([a-z-]+?)(?:-\d+)?\.db$")


def _label(path):
    m = _pattern().match(path.name)
    return m.group(1) if m else None


def make_backup(store, label="auto", protect=None):
    """Kopiert die Datenbank sicher (auch während der Server läuft).
    `protect`: eine Datei, die beim Aufräumen auf keinen Fall gelöscht wird."""
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    name = f"{PREFIX}-{stamp}-{label}.db"
    n = 2
    while (BACKUP_DIR / name).exists():          # nie ein vorhandenes Backup überschreiben
        name = f"{PREFIX}-{stamp}-{label}-{n}.db"
        n += 1
    target = sqlite3.connect(BACKUP_DIR / name)
    try:
        with store.lock:
            store.db.backup(target)
    finally:
        target.close()
    _prune(protect)
    return name


def _mine():
    """Backups dieses Spielstands (Datum steht im Namen -> nach Namen sortierbar)."""
    if not BACKUP_DIR.exists():
        return []
    return sorted(f for f in BACKUP_DIR.glob(f"{PREFIX}-*.db") if _label(f))


def _prune(protect=None):
    by_label = {}
    for f in _mine():
        by_label.setdefault(_label(f), []).append(f)
    for label, files in by_label.items():
        for old in files[:-KEEP.get(label, KEEP_OTHER)]:
            if protect and old.resolve() == Path(protect).resolve():
                continue
            try:
                old.unlink()
            except OSError:              # z. B. gerade geöffnet – beim nächsten Mal
                pass


def path_for(name):
    """Sicherer Pfad zu einem Backup (nur eigene Dateien direkt in backups/)."""
    if not isinstance(name, str):
        raise ValueError("Dieses Backup gibt es nicht.")
    path = (BACKUP_DIR / name).resolve()
    if path.parent != BACKUP_DIR.resolve() or path not in [f.resolve() for f in _mine()]:
        raise ValueError("Dieses Backup gibt es nicht.")
    return path


def restore(store, name):
    """Spielt ein Backup ein. Vorher wird der aktuelle Stand gesichert, damit
    man das Einspielen rückgängig machen kann. Danach wird der Stand auf die
    aktuelle Version gebracht (auch alte Backups funktionieren)."""
    source = path_for(name)
    check = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    try:
        if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Das Backup ist beschädigt.")
        tables = {r[0] for r in check.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"pets", "users", "meta"} <= tables:
            raise ValueError("Das ist kein Spielstand.")
        with store.lock:
            safety = make_backup(store, "vor-einspielen", protect=source)
            check.backup(store.db)
            store.migrate()
    finally:
        check.close()
    return safety


def delete(name):
    path_for(name).unlink()


def list_backups():
    return [{"name": f.name, "size_kb": round(f.stat().st_size / 1024), "time": int(f.stat().st_mtime)}
            for f in reversed(_mine())]
