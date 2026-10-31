"""Tests für den Admin-Bereich und die Server-Regeln.  Starten mit:  python -m unittest"""
import tempfile
import unittest
from pathlib import Path

from game import accounts, admin, backup, explore, settings
from game import pet as P
from game.store import Store
from tests.test_battle import rookie
from tests.test_pet import MORNING, run


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        settings.load(self.store)

    def tearDown(self):
        settings.CURRENT.clear()
        settings.CURRENT.update(settings.DEFAULTS)

    def test_validation(self):
        with self.assertRaises(ValueError):
            settings.update(self.store, {"need_speed": 7})
        with self.assertRaises(ValueError):
            settings.update(self.store, {"registration": "jeder"})
        with self.assertRaises(ValueError):
            settings.update(self.store, {"quatsch": 1})
        settings.update(self.store, {"need_speed": 0.5, "announcement": "  Hallo!  "})
        self.assertEqual(settings.load(self.store)["announcement"], "Hallo!")     # bleibt gespeichert

    def test_no_death(self):
        settings.update(self.store, {"death": False})
        p = P.new_egg("ver1", MORNING)
        P.advance(p, MORNING + 5 * 24 * 60)
        self.assertTrue(p["alive"])

    def test_need_speed(self):
        normal = P.new_egg("ver1", MORNING)
        run(normal, MORNING, 20, every=1)
        slow = dict(normal, log=[])
        P.advance(normal, normal["last"] + 120)
        settings.update(self.store, {"need_speed": 0.5})
        P.advance(slow, slow["last"] + 120)
        self.assertGreater(slow["hunger"], normal["hunger"])

    def test_registration_modes(self):
        accounts.register(self.store, "Chef", "geheim123", None)
        settings.update(self.store, {"registration": "open"})
        accounts.register(self.store, "Tai", "geheim123", None)               # ohne Code
        settings.update(self.store, {"registration": "closed"})
        with self.assertRaises(accounts.AuthError):
            accounts.register(self.store, "Sora", "geheim123", accounts.invite_code(self.store))

    def test_maintenance_only_admins(self):
        accounts.register(self.store, "Chef", "geheim123", None)
        accounts.register(self.store, "Tai", "geheim123", accounts.invite_code(self.store))
        settings.update(self.store, {"maintenance": True})
        accounts.login(self.store, "Chef", "geheim123")
        with self.assertRaises(accounts.AuthError):
            accounts.login(self.store, "Tai", "geheim123")

    def test_explore_luck(self):
        from tests.test_battle import Always
        p = rookie()
        settings.update(self.store, {"explore_luck": 3.0})
        found = explore.roll(p, {"area": "wald", "minutes": 480}, Always(0.25))   # 0.25 < 0.30 Scherben-Chance (sonst 0.10)
        self.assertEqual(found["shards"], 6)


class AdminTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        settings.load(self.store)
        accounts.register(self.store, "Chef", "geheim123", None)
        accounts.register(self.store, "Tai", "geheim123", accounts.invite_code(self.store))
        self.chef = self.store.user_by_name("Chef")
        self.items = []
        self.store.add_pet("2", rookie())

    def act(self, name, action, **params):
        return admin.user_action(self.store, self.chef, name, action, params, MORNING,
                                 lambda owner, item, n: self.items.append((owner, item, n)))[0]

    def test_cannot_harm_self_or_last_admin(self):
        for action in ("remove_admin", "ban", "delete", "kick"):
            with self.assertRaises(P.Refused):
                self.act("Chef", action)

    def test_admin_rights(self):
        self.act("Tai", "make_admin")
        self.assertTrue(self.store.user_by_name("Tai")["is_admin"])
        self.act("Tai", "remove_admin")
        self.assertFalse(self.store.user_by_name("Tai")["is_admin"])

    def test_ban_blocks_login_and_session(self):
        token = accounts.login(self.store, "Tai", "geheim123")
        self.act("Tai", "ban")
        self.assertIsNone(self.store.user_by_session(token))
        with self.assertRaises(accounts.AuthError):
            accounts.login(self.store, "Tai", "geheim123")
        self.act("Tai", "unban")
        accounts.login(self.store, "Tai", "geheim123")

    def test_help_pet_and_gifts(self):
        pet = self.store.active_pet("2")
        pet.update(sick=True, sick_since=MORNING, hunger=0, cheated=False)
        self.store.save_pet(pet)
        self.act("Tai", "heal")
        self.act("Tai", "feed")
        pet = self.store.active_pet("2")
        self.assertFalse(pet["sick"])
        self.assertEqual(pet["hunger"], 4)
        self.assertFalse(pet.get("cheated"))
        self.act("Tai", "gift_item", item="charm", count=3)
        self.assertEqual(self.items, [("2", "charm", 3)])
        self.act("Tai", "gift_egg", line="ver2")
        self.assertEqual(self.store.all_pets("2")[0]["line"], "ver2")

    def test_revive(self):
        pet = self.store.active_pet("2")
        P.advance(pet, pet["last"] + 5 * 24 * 60)
        self.store.save_pet(pet)
        self.assertFalse(pet["alive"])
        self.act("Tai", "revive")
        self.assertTrue(self.store.active_pet("2")["alive"])

    def test_delete(self):
        self.act("Tai", "delete")
        self.assertIsNone(self.store.user_by_name("Tai"))
        self.assertEqual(self.store.all_pets("2"), [])

    def test_activity_log(self):
        self.store.log_activity("Chef", "hat etwas gemacht")
        self.assertEqual(self.store.activity()[0]["text"], "hat etwas gemacht")


class RestoreTest(unittest.TestCase):
    def test_backup_and_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_dir = backup.BACKUP_DIR
            backup.BACKUP_DIR = Path(tmp)
            store = Store(str(Path(tmp) / "live.db"))
            backup.use_store(store)
            try:
                accounts.register(store, "Chef", "geheim123", None)
                name = backup.make_backup(store, "test")
                accounts.register(store, "Tai", "geheim123", accounts.invite_code(store))
                self.assertEqual(store.user_count(), 2)
                safety = backup.restore(store, name)
                self.assertEqual(store.user_count(), 1)                 # Stand vom Backup
                backup.restore(store, safety)                           # gleiche Sekunde!
                self.assertEqual(store.user_count(), 2)                 # rückgängig gemacht
                with self.assertRaises(ValueError):
                    backup.restore(store, "../live.db")                 # kein Ausbruch aus backups/
                (Path(tmp) / "savegame-2026-01-01_00-00-00-auto.db").write_bytes(b"")
                self.assertTrue(all(b["name"].startswith("live-") for b in backup.list_backups()))
                with self.assertRaises(ValueError):                     # fremder Spielstand
                    backup.restore(store, "savegame-2026-01-01_00-00-00-auto.db")
            finally:
                store.db.close()
                backup.BACKUP_DIR = old_dir
                backup.PREFIX = "savegame"


if __name__ == "__main__":
    unittest.main()
