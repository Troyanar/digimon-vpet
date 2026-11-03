"""Push-Ereignisse, Gerätebindung, Wiederholungen und Schlüssel ohne echte Zustellung."""
import base64
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from game import push
from game.i18n import localize
from game.store import Store


def snapshot():
    return {"pet": {"id": 1, "name": "Agumon", "dex": 29, "stage": "Child", "alive": True,
                    "sick": False, "frozen": False, "calls": [], "totem": False,
                    "returned": False}, "trips": []}


class EventTest(unittest.TestCase):
    def test_new_call_once_and_again_after_resolving(self):
        before = snapshot()
        now = copy.deepcopy(before)
        now["pet"]["calls"] = [{"what": "hunger"}]
        self.assertEqual(push.messages(before, now)[0]["tag"], "call")
        self.assertEqual(push.messages(now, now), [])
        self.assertEqual(push.messages(now, before), [])
        self.assertEqual(len(push.messages(before, now)), 1)

    def test_hatch_evolve_and_partner_switch(self):
        before, now = snapshot(), snapshot()
        before["pet"].update(stage="Egg", dex=None)
        self.assertEqual(localize(push.messages(before, now), "en")[0]["title"], "The egg has hatched!")
        before = snapshot()
        now["pet"].update(name="Greymon", dex=42)
        self.assertEqual(push.messages(before, now)[0]["tag"], "evolve")
        now["pet"]["id"] = 2
        self.assertEqual(push.messages(before, now), [])
        now["pet"].update(id=1, stage="Egg")
        self.assertEqual(push.messages(before, now), [])

    def test_sick_death_totem_and_frozen(self):
        for change, tag in [({"sick": True}, "sick"), ({"alive": False}, "death")]:
            before, now = snapshot(), snapshot()
            now["pet"].update(change)
            self.assertEqual(push.messages(before, now)[0]["tag"], tag)
        before, now = snapshot(), snapshot()
        before["pet"]["totem"] = True
        now["pet"]["frozen"] = True
        self.assertEqual(push.messages(before, now)[0]["tag"], "totem")
        now["pet"].update(sick=True, calls=[{"what": "hunger"}])
        self.assertEqual(push.messages(snapshot(), now), [])

    def test_both_exploration_returns_and_no_old_events(self):
        before, now = snapshot(), snapshot()
        now["pet"]["returned"] = True
        now["trips"] = ["2:1234"]
        self.assertEqual([n["tag"] for n in push.messages(before, now)], ["return", "box-return"])
        self.assertEqual(push.messages(now, now), [])
        self.assertEqual(push.messages({}, snapshot()), [])


@unittest.skipUnless(push.webpush, "Push-Paket optional; siehe game/push-requirements.txt")
class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "check.db")
        uid = self.store.add_user("Tester", "hash", "salt", False)
        self.user = self.store.user_by_id(uid)
        self.store.add_session("test-token", uid)
        self.snap = snapshot()
        self.service = push.Service(self.store, lambda user: copy.deepcopy(self.snap))
        key = push.ec.generate_private_key(push.ec.SECP256R1()).public_key().public_bytes(
            push.serialization.Encoding.X962, push.serialization.PublicFormat.UncompressedPoint)
        enc = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
        self.sub = {"endpoint": "https://web.push.apple.com/test", "keys": {"p256dh": enc(key), "auth": enc(b"a" * 16)}}

    def tearDown(self):
        self.store.db.close()
        self.tmp.cleanup()

    def subscribe(self):
        self.service.subscribe(self.user, "test-token", self.sub)

    def test_reject_unsafe_endpoints_and_invalid_keys(self):
        for endpoint in ["http://push.apple.com/x", "https://push.apple.com.evil.example/x",
                         "https://localhost/x", "https://push.apple.com:444/x",
                         "https://user@push.apple.com/x", "https://push.apple.com/x#fragment"]:
            with self.assertRaises(ValueError):
                push.validate({**self.sub, "endpoint": endpoint})
        with self.assertRaises(ValueError):
            push.validate({**self.sub, "keys": {"p256dh": "x", "auth": "x"}})
        self.assertEqual(push.validate(self.sub), self.sub)

    def test_key_persists_across_restarts(self):
        key = self.service.public_key()
        again = push.Service(self.store, lambda _: self.snap)
        self.assertEqual(again.public_key(), key)
        self.assertTrue(self.service.path.exists())

    def test_first_subscription_is_baseline_then_one_notification(self):
        self.subscribe()
        with patch.object(self.service, "send", return_value=True) as send:
            self.service.tick()
            send.assert_not_called()
            self.snap["pet"]["sick"] = True
            self.service.tick()
            self.service.tick()
            self.assertEqual(send.call_count, 1)

    def test_transient_failure_retries_and_gone_device_is_removed(self):
        self.subscribe()
        self.snap["pet"]["sick"] = True
        with patch.object(self.service, "send", side_effect=[None, True, False]) as send:
            self.service.tick()
            self.service.tick()
            self.service.tick()
            self.assertEqual(send.call_count, 2)
            self.snap["pet"]["alive"] = False
            self.service.tick()
            self.assertFalse(self.service.devices())

    def test_logout_expired_session_banned_and_deleted_user_stop_push(self):
        for action in (lambda: self.store.delete_session("test-token"),
                       lambda: self.store.db.execute("UPDATE sessions SET created=0"),
                       lambda: self.store.set_flag(self.user["id"], "banned", True)):
            self.store.set_flag(self.user["id"], "banned", False)
            self.store.delete_session("test-token")
            self.store.add_session("test-token", self.user["id"])
            self.subscribe()
            action()
            with patch.object(self.service, "send") as send:
                self.service.tick()
                send.assert_not_called()
                self.assertFalse(self.service.devices())
        self.store.delete_session("test-token")
        self.store.set_flag(self.user["id"], "banned", False)
        self.store.add_session("test-token", self.user["id"])
        self.subscribe()
        self.store.delete_user(self.user["id"])
        self.service.tick()
        self.assertFalse(self.service.devices())

    def test_devices_cannot_be_removed_by_other_users_and_rebind_is_explicit(self):
        self.subscribe()
        uid = self.store.add_user("Other", "hash", "salt", False)
        other = self.store.user_by_id(uid)
        self.service.remove(other, self.sub["endpoint"])
        self.assertEqual(len(self.service.devices()), 1)
        self.store.add_session("other-token", uid)
        self.service.subscribe(other, "other-token", self.sub)
        self.assertEqual([d["owner"] for d in self.service.devices().values()], [uid])
        self.service.remove(other, self.sub["endpoint"])
        self.assertFalse(self.service.devices())

    def test_eight_device_limit(self):
        for i in range(8):
            self.sub["endpoint"] = "https://web.push.apple.com/test" + str(i)
            self.subscribe()
        self.sub["endpoint"] += "extra"
        with self.assertRaises(ValueError):
            self.subscribe()

    def test_real_encryption_without_network_and_english_payload(self):
        self.subscribe()
        device = next(iter(self.service.devices().values()))
        self.snap["pet"]["sick"] = True
        # Echte Bibliothek, echte Schlüssel/Verschlüsselung; nur der HTTP-Versand ist ersetzt.
        with patch("requests.Session.request") as request:
            request.return_value.status_code = 201
            self.assertTrue(self.service.send(device, push.messages(snapshot(), self.snap), "en"))
            args = request.call_args.kwargs
            self.assertTrue(args["data"])
        with patch.object(push, "webpush") as sender:
            self.service.send(device, push.messages(snapshot(), self.snap), "en")
            payload = json.loads(sender.call_args.args[1])
            self.assertEqual(payload["title"], "Agumon is sick!")
            self.assertEqual(payload["body"], "Give it medicine quickly.")

    def test_disabling_during_send_does_not_restore_device(self):
        self.subscribe()
        self.snap["pet"]["sick"] = True
        def send(*args):
            self.service.remove(self.user, self.sub["endpoint"])
            return True
        with patch.object(self.service, "send", side_effect=send):
            self.service.tick()
        self.assertFalse(self.service.devices())

    def test_sender_removes_expired_subscription_and_retries_server_errors(self):
        self.subscribe()
        device = next(iter(self.service.devices().values()))
        self.snap["pet"]["sick"] = True
        notes = push.messages(snapshot(), self.snap)
        for status, expected in [(410, False), (404, False), (503, None)]:
            from unittest.mock import Mock
            error = push.WebPushException("unavailable", response=Mock(status_code=status))
            with patch.object(push, "webpush", side_effect=error):
                self.assertIs(self.service.send(device, notes, "en"), expected)
