"""Tests für Konten und Einladungscodes.  Starten mit:  python -m unittest"""
import unittest

from game import accounts
from game.store import Store


class AccountTest(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")

    def test_first_user_needs_no_invite_and_is_admin(self):
        token = accounts.register(self.store, "Mario", "geheim123", None)
        user = self.store.user_by_session(token)
        self.assertEqual(user["name"], "Mario")
        self.assertTrue(user["is_admin"])

    def test_second_user_needs_invite(self):
        accounts.register(self.store, "Mario", "geheim123", None)
        with self.assertRaises(accounts.AuthError):
            accounts.register(self.store, "Tai", "geheim123", "FALSCH")
        code = accounts.invite_code(self.store)
        token = accounts.register(self.store, "Tai", "geheim123", code.lower())
        self.assertFalse(self.store.user_by_session(token)["is_admin"])

    def test_new_invite_code_invalidates_old(self):
        accounts.register(self.store, "Mario", "geheim123", None)
        old = accounts.invite_code(self.store)
        accounts.new_invite_code(self.store)
        with self.assertRaises(accounts.AuthError):
            accounts.register(self.store, "Tai", "geheim123", old)

    def test_login(self):
        accounts.register(self.store, "Mario", "geheim123", None)
        self.assertTrue(accounts.login(self.store, "mario", "geheim123"))   # Name ohne Groß/Klein
        with self.assertRaises(accounts.AuthError):
            accounts.login(self.store, "Mario", "falsch!!")
        with self.assertRaises(accounts.AuthError):
            accounts.login(self.store, "Niemand", "geheim123")

    def test_rules(self):
        with self.assertRaises(accounts.AuthError):
            accounts.register(self.store, "ab", "geheim123", None)        # Name zu kurz
        with self.assertRaises(accounts.AuthError):
            accounts.register(self.store, "Mario", "123", None)            # Passwort zu kurz
        accounts.register(self.store, "Mario", "geheim123", None)
        code = accounts.invite_code(self.store)
        with self.assertRaises(accounts.AuthError):
            accounts.register(self.store, "MARIO", "geheim123", code)      # Name vergeben

    def test_logout(self):
        token = accounts.register(self.store, "Mario", "geheim123", None)
        self.store.delete_session(token)
        self.assertIsNone(self.store.user_by_session(token))

    def test_change_password_logs_out_other_devices(self):
        phone = accounts.register(self.store, "Mario", "geheim123", None)
        pc = accounts.login(self.store, "Mario", "geheim123")
        user_id = self.store.user_by_session(pc)["id"]
        with self.assertRaises(accounts.AuthError):
            accounts.change_password(self.store, user_id, "falsch!!", "neues123", pc)
        accounts.change_password(self.store, user_id, "geheim123", "neues123", pc)
        self.assertIsNotNone(self.store.user_by_session(pc))       # dieses Gerät bleibt
        self.assertIsNone(self.store.user_by_session(phone))       # anderes ist abgemeldet
        accounts.login(self.store, "Mario", "neues123")

    def test_admin_reset(self):
        accounts.register(self.store, "Mario", "geheim123", None)
        tai = accounts.register(self.store, "Tai", "vergessen", accounts.invite_code(self.store))
        temp = accounts.reset_password(self.store, "tai")
        self.assertEqual(len(temp), 8)
        self.assertIsNone(self.store.user_by_session(tai))
        accounts.login(self.store, "Tai", temp)
        with self.assertRaises(accounts.AuthError):
            accounts.login(self.store, "Tai", "vergessen")
        with self.assertRaises(accounts.AuthError):
            accounts.reset_password(self.store, "Niemand")

    def test_first_user_adopts_old_pet(self):
        self.store.add_pet("local", {"name": "alt"})
        token = accounts.register(self.store, "Mario", "geheim123", None)
        user = self.store.user_by_session(token)
        self.assertEqual(self.store.active_pet(str(user["id"]))["name"], "alt")


if __name__ == "__main__":
    unittest.main()
