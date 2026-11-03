"""Push-Routen mit echtem Spielstand, aber ohne Netzwerk und ohne Live-Daten."""
import os
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

class PushApiTest(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("pywebpush"), "Push-Paket optional")
    def test_push_routes_and_background_snapshot(self):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child"],
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def child():
    import base64
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    # Im Kindprozess game.store erst NACH VPET_DB importieren.
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["VPET_DB"] = str(Path(tmp) / "check.db")
        import server
        from tests.test_battle import rookie
        from game import pet as P, i18n, push
        store = server.store
        uid = store.add_user("Tester", "hash", "salt", False)
        store.add_session("token", uid)
        user = store.user_by_id(uid)
        now = server.clock.now()
        pet = rookie()
        P.shift_times(pet, now - pet["last"])
        pet["last"] = now
        store.add_pet(str(uid), pet)
        handler = server.Handler.__new__(server.Handler)
        handler.current_user = lambda: user
        handler.session_token = lambda: "token"
        handler.locked_out = lambda u: False
        handler.lang = lambda: "en"
        handler.send_json = lambda data, status=200, **kwargs: (i18n.localize(data, "en"), status)

        def call(path, body=None):
            handler.path = path
            handler.read_body = lambda: body
            return handler._get() if body is None else handler._post()

        assert call("/api/push")[0]["key"]
        assert call("/api/push", {"endpoint": "https://localhost/test"})[1] == 400
        key = push.ec.generate_private_key(push.ec.SECP256R1()).public_key().public_bytes(
            push.serialization.Encoding.X962, push.serialization.PublicFormat.UncompressedPoint)
        enc = lambda data: base64.urlsafe_b64encode(data).decode().rstrip("=")
        sub = {"endpoint": "https://web.push.apple.com/api-test",
               "keys": {"p256dh": enc(key), "auth": enc(b"a" * 16)}}
        assert call("/api/push", sub)[1] == 200
        assert call("/api/push")[0]["endpoints"] == [sub["endpoint"]]
        notes = []
        def fake_send(device, messages, lang):
            notes.extend(i18n.localize(messages, lang))
            return True
        server.push_service.send = fake_send
        assert call("/api/push/test", {"endpoint": sub["endpoint"]})[1] == 200
        assert notes[-1]["title"] == "Notifications are on"
        assert call("/api/push/test", {"endpoint": sub["endpoint"]})[1] == 429
        store.set_meta(f"lang:{uid}", "en")
        pet = store.active_pet(str(uid))
        pet["sick"] = True
        store.save_pet(pet)
        server.push_service.tick()
        assert notes[-1]["title"] == "Agumon is sick!"
        count = len(notes)
        server.push_service.tick()
        assert len(notes) == count
        pet = store.active_pet(str(uid))
        pet["expedition"] = {"area": "wald", "start": now - 30, "end": now, "minutes": 30}
        pet["last"] = now - 1
        store.save_pet(pet)
        server.push_service.tick()
        assert notes[-1]["tag"] == "return"
        pet = store.active_pet(str(uid))
        assert pet["expedition_return"] and pet["returned"]
        assert call("/api/push/off", {"endpoint": sub["endpoint"]})[1] == 200
        assert not call("/api/push")[0]["endpoints"]
        assert call("/api/push", sub)[1] == 200
        assert call("/api/logout", {})[1] == 200
        server.push_service.tick()
        assert not server.push_service.devices()
        handler.current_user = lambda: None
        assert call("/api/push")[1] == 401
        assert call("/api/push", sub)[1] == 401
        store.db.close()


if __name__ == "__main__":
    if "--child" in sys.argv:
        child()
    else:
        unittest.main()
