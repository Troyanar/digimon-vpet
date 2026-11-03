"""Neue Fusion über die Server-Routen mit isoliertem Test-Spielstand."""
import os
from pathlib import Path
import subprocess
import sys
import unittest


class JogressApiTest(unittest.TestCase):
    def test_solo_confirmation_and_two_friend_results(self):
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child"],
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def child():
    import tempfile
    import time
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["VPET_DB"] = str(Path(tmp) / "check.db")
        import server
        from game import friends, i18n, progress
        from game import pet as P
        from tests.test_social import become, find_dex
        store = server.store
        a = store.user_by_id(store.add_user("Tester", "hash", "salt", False))
        b = store.user_by_id(store.add_user("Friend", "hash", "salt", False))
        friends.add(store, a, friends.code(store, b["id"]))
        handler = server.Handler.__new__(server.Handler)
        handler.locked_out = lambda user: False
        handler.lang = lambda: "en"
        handler.send_json = lambda obj, status=200, **kwargs: (i18n.localize(obj, "en"), status)
        handler.send_error = lambda status: ({}, status)

        def call(user, step, body):
            handler.path = "/api/jogress/" + step
            handler.current_user = lambda: user
            handler.read_body = lambda: body
            return handler._post()

        def seed(owner, name, line, active=True):
            pet = become(line, find_dex(name))
            now = server.clock.now()
            P.shift_times(pet, now - pet["last"])
            pet["last"] = now
            pet.update(no_sleep=True, asleep=False)
            if not active:
                pet.update(in_box=True, box=0, name="Ice")
            return store.add_pet(str(owner["id"]), pet, active=active)

        p = seed(a, "WarGreymon", "ver1")
        q = seed(a, "MetalGarurumon", "ver2", False)
        to = find_dex("Omnimon")
        body = {"to": to, "partner_id": q["id"], "basis_id": q["id"], "active_id": p["id"]}
        assert call(a, "box", body)[1] == 400  # alter Browser darf nichts verbrauchen
        body["confirmed"] = True
        assert call(a, "box", {**body, "active_id": 999})[1] == 400
        assert len(store.all_pets(str(a["id"]))) == 2
        result, status = call(a, "box", body)
        assert status == 200, result
        assert result["pet"]["id"] == q["id"] and result["pet"]["dex"] == to
        assert result["pet"]["nickname"] == "Ice"
        assert len(store.all_pets(str(a["id"]))) == 1
        assert call(a, "box", body)[1] == 400  # derselbe Klick wirkt nie zweimal
        assert progress.stats(store, str(a["id"]))["jogress"] == 1

        p = seed(a, "WarGreymon", "ver1")
        q = seed(b, "MetalGarurumon", "ver2")
        server.LAST_SEEN[b["id"]] = time.time()
        ask = {"name": b["name"], "to": to, "active_id": p["id"], "confirmed": True}
        assert call(a, "ask", ask)[1] == 200
        assert call(b, "answer", {"accept": True})[1] == 400
        assert store.active_pet(str(a["id"]))["dex"] != to
        # Eine Ablehnung darf für niemanden einen Erfolg zählen.
        assert call(b, "answer", {"accept": False})[1] == 200
        assert progress.stats(store, str(a["id"]))["jogress"] == 1
        assert progress.stats(store, str(b["id"]))["jogress"] == 0
        assert call(a, "ask", ask)[1] == 200
        result, status = call(b, "answer", {"accept": True, "confirmed": True})
        assert status == 200, result
        assert "Both Digimon are now Omnimon" in result["message"]
        assert store.active_pet(str(a["id"]))["dex"] == to
        assert store.active_pet(str(b["id"]))["dex"] == to
        assert progress.stats(store, str(a["id"]))["jogress"] == 2
        assert progress.stats(store, str(b["id"]))["jogress"] == 1
        assert to in progress.owned(store, str(a["id"]))
        assert to in progress.owned(store, str(b["id"]))
        assert call(b, "answer", {"accept": True, "confirmed": True})[1] == 400
        store.db.close()


if __name__ == "__main__":
    child() if "--child" in sys.argv else unittest.main()
