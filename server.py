"""Digimon V-Pet -- Server.

Starten:  python server.py      (oder Doppelklick auf start.bat)
Dann im Browser: http://localhost:8000

Zum Testen kann die Zeit beschleunigt werden, z. B. 60x schneller:
    set VPET_SPEED=60
    python server.py

Weitere Einstellungen (Umgebungsvariablen), vor allem fürs Online-Stellen:
    VPET_HOST=0.0.0.0     auf welcher Adresse lauschen (Standard: nur dieser PC)
    VPET_SECURE=1         Cookie nur über HTTPS senden (online immer setzen!)
    VPET_TRUST_PROXY=1    hinter einem Reverse-Proxy: echte Besucher-IP aus X-Forwarded-For
    VPET_PUBLIC=1         erstes Konto wird nicht automatisch Admin (Admin per Werkzeug anlegen)
    VPET_TZ=Europe/Berlin Zeitzone fürs Spiel (Schlafenszeiten)
"""
import hashlib
import json
import math
import mimetypes
import os
import random
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from game import accounts, backup, battle, cheats, collection, data, explore, pet as petlib
from game import admin, decor, events, friends, i18n, progress, settings, shop, social, starter, themes, wishlist
from game import duel as duel_lib
from game import store as store_lib
from game.i18n import T
from game.store import Store

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")        # Windows-Registry liefert sonst evtl. text/plain

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
PORT = int(os.environ.get("VPET_PORT", "8000"))
HOST = os.environ.get("VPET_HOST", "127.0.0.1")
SPEED = float(os.environ.get("VPET_SPEED", "1"))
SECURE = bool(os.environ.get("VPET_SECURE"))
TRUST_PROXY = bool(os.environ.get("VPET_TRUST_PROXY"))
COOKIE = "vpet_session"
LANG_COOKIE = "vpet_lang"            # Sprache des Geräts ("de"/"en"), setzt static/i18n.js
MAX_BODY = 64 * 1024                 # größere Anfragen braucht das Spiel nie


class BadRequest(Exception):
    """Ungültige Anfrage – wird als 400 beantwortet."""


def as_int(value, default=None):
    """Zahl aus einer Anfrage lesen (ohne Absturz bei Text, Listen, unendlich ...)."""
    if value is None and default is not None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise BadRequest(T("Ungültige Zahl."))
    try:
        number = float(value)
    except ValueError:
        raise BadRequest(T("Ungültige Zahl."))
    if not math.isfinite(number) or abs(number) > 2 ** 53:
        raise BadRequest(T("Ungültige Zahl."))
    return int(number)


def as_text(value):
    return value if isinstance(value, str) else ""


# ---------------------------------------------------------------- Passwort-Raten bremsen
LOGIN_FAILS = {}          # ("ip"/"name", wert) -> [Zeitpunkte fehlgeschlagener Versuche]
FAIL_WINDOW = 15 * 60
FAIL_LIMIT = {"ip": 30, "name": 8}
fails_lock = threading.Lock()


def _fail_keys(ip, name):
    return [("ip", ip), ("name", as_text(name).strip().lower())]


def login_blocked(ip, name):
    """Sekunden, die noch gewartet werden muss (0 = darf versuchen)."""
    now = time.time()
    with fails_lock:
        for key in _fail_keys(ip, name):
            times = [t for t in LOGIN_FAILS.get(key, []) if now - t < FAIL_WINDOW]
            LOGIN_FAILS[key] = times
            if len(times) >= FAIL_LIMIT[key[0]]:
                return int(FAIL_WINDOW - (now - times[0])) + 1
    return 0


def login_failed(ip, name):
    with fails_lock:
        for key in _fail_keys(ip, name):
            LOGIN_FAILS.setdefault(key, []).append(time.time())
        if len(LOGIN_FAILS) > 10000:           # nicht endlos wachsen lassen
            LOGIN_FAILS.clear()

store = Store()
settings.load(store)
shop.load(store)                       # Admin-Preise + festgelegter Daily Steal
backup.use_store(store)
STARTED = time.time()


def _version():
    """Fingerabdruck aller Spieldateien – ändert sich mit jedem Update. Der Browser
    vergleicht ihn und bietet dann "Neu laden" an."""
    h = hashlib.sha1()
    files = [ROOT / "server.py", ROOT / "data" / "digimon.json"]
    files += sorted((ROOT / "game").glob("*.py")) + sorted(p for p in (ROOT / "static").rglob("*") if p.is_file())
    for p in files:
        h.update(p.relative_to(ROOT).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


VERSION = _version()


def _release():
    """Versionsnummer für Menschen (z. B. "1.8") = neuester Eintrag im Changelog."""
    try:
        return json.loads((ROOT / "static" / "changelog.json").read_text(encoding="utf8"))[0]["version"]
    except (OSError, ValueError, LookupError):
        return None


RELEASE = _release()


class Clock:
    """Spielzeit in Minuten. Bei VPET_SPEED > 1 läuft sie schneller; der
    Vorsprung wird gespeichert, damit die Zeit nach einem Neustart nicht
    rückwärts läuft."""

    def __init__(self):
        self.reload()

    def reload(self):
        """(Neu) aus dem Spielstand laden – auch nach dem Einspielen eines Backups."""
        self.start = time.time()
        self.offset = store.get_meta("clock_offset", 0.0)

    def now(self):
        real = time.time()
        game = real + self.offset + (real - self.start) * (SPEED - 1)
        return int(game // 60)

    def save(self):
        real = time.time()
        store.set_meta("clock_offset", self.offset + (real - self.start) * (SPEED - 1))


clock = Clock()


def restored_pets_wait(taken):
    """Nach dem Einspielen eines Backups: die Zeit zwischen Backup und jetzt soll
    für die Digimon nicht vergangen sein – sonst verhungern sie alle "nachträglich".
    `taken`: Zeitpunkt des Backups (echte Sekunden)."""
    gap = clock.now() - int((taken + clock.offset) // 60)
    if gap <= 0:
        return
    with store.lock:
        for pet in store.every_pet():
            petlib.shift_times(pet, gap)
            store.save_pet(pet)

ACTIONS = {
    "feed": lambda p, body, m: petlib.feed(p, body.get("food"), m),
    "train": lambda p, body, m: petlib.train(p, bool(body.get("success")), m, body.get("kind", "power")),
    "clean": lambda p, body, m: petlib.clean(p, m),
    "light": lambda p, body, m: petlib.toggle_light(p, m),
    "medicine": lambda p, body, m: petlib.medicine(p, m),
}


def new_random_egg(owner, now):
    """Welches Ei man bekommt, entscheidet der Zufall."""
    line = random.choice(data.NORMAL_LINES)
    return store.add_pet(owner, petlib.new_egg(line, now))


def inventory(owner):
    return store.get_meta(f"inventory:{owner}", {})


def add_item(owner, item, amount=1):
    inv = inventory(owner)
    inv[item] = inv.get(item, 0) + amount
    if inv[item] <= 0:
        inv.pop(item)
    store.set_meta(f"inventory:{owner}", inv)


def account_lang(owner):
    """Gespeicherte Sprache des Kontos (None = noch nie gewählt)."""
    return store.get_meta(f"lang:{owner}", None)


def current_event(now):
    """Laufendes Event (z. B. "halloween") – oder per Admin-Cheat erzwungen (meta "event_force")."""
    return events.current(now, store.get_meta("event_force", None))


def always_day(owner):
    """Cheat "Immer Tag" (nur Admin): die Digimon dieses Kontos schlafen nicht."""
    return bool(store.get_meta(f"always_day:{owner}", False))


def can_get_free_egg(owner):
    return collection.can_get_free_egg(store, owner)


LAST_SEEN = {}          # Konto-ID -> Zeitpunkt der letzten Anfrage (wer ist online?)
ONLINE_FOR = 20         # Sekunden


def is_online(user_id):
    return time.time() - LAST_SEEN.get(user_id, 0) < ONLINE_FOR


def duel_pets(duel, now):
    """Die aktiven Digimon beider Seiten, auf den aktuellen Stand gerechnet."""
    pets = {}
    for side in ("a", "b"):
        pet = store.active_pet(str(duel[side]))
        if pet:
            petlib.advance(pet, now)
        pets[side] = pet
    return pets


def save_duel(duel, pets):
    result = duel["data"].get("result")
    if duel["status"] == "done" and result and not duel["data"].get("logged"):
        names = duel["data"]["names"]
        store.log_activity(names["a"], f"Kampf gegen {names['b']}: {result['text']}")
        for side, bits in duel["data"].get("bits", {}).items():     # Bits genau einmal gutschreiben
            shop.add(store, str(duel[side]), bits)
        winner = result.get("winner")
        if winner in ("a", "b"):                                    # für die Erfolge
            progress.count(store, str(duel[winner]), "pvp_wins")
            progress.count(store, str(duel[winner]), "wins")
        duel["data"]["logged"] = True
    store.save_duel(duel)
    for pet in pets.values():
        if pet:
            store.save_pet(pet)


def in_open_duel(user):
    duel = store.latest_duel(user["id"])
    return bool(duel and duel["status"] in duel_lib.OPEN)


def duel_state(user, now):
    """Aktueller Kampf gegen Freunde aus Sicht von `user` (Zeitüberschreitungen inklusive)."""
    duel = store.latest_duel(user["id"])
    if not duel:
        return None
    pets = duel_pets(duel, now)
    if duel["status"] in duel_lib.OPEN:
        duel_lib.tick(duel, pets, time.time())
        save_duel(duel, pets)
    return duel_lib.view(duel, user["id"], pets, time.time())


def current_state(user):
    now = clock.now()
    if SPEED != 1:
        clock.save()
    owner = str(user["id"])
    duel_view = duel_state(user, now)        # zuerst: kann auch das eigene Digimon ändern
    pet = store.active_pet(owner)
    report = None
    day = always_day(owner)
    event = current_event(now)
    if pet:
        cheats.set_day(pet, day)             # Cheat "Immer Tag" gilt für jedes Digimon des Kontos
        petlib.advance(pet, now)
        # zurück vom Erkunden? Funde verteilen (genau einmal) – während eines Events mit Extras
        report = explore.claim(pet, now,
                               store_egg=lambda line: collection.store_egg(store, owner, line, now),
                               add_item=lambda item: add_item(owner, item),
                               add_bits=lambda n: shop.add(store, owner, n),
                               extra=events.trip_bonus(event) if pet.get("expedition_return") else None)
        if report:
            progress.count(store, owner, "trips")
        store.save_pet(pet)
    # Digimon aus der Sammlung zurück vom Erkunden? (wilde Digimon folgen ihnen nicht)
    box_reports = collection.claim_trips(store, owner, now, add_item=lambda item: add_item(owner, item),
                                         add_bits=lambda n: shop.add(store, owner, n),
                                         extra=lambda: events.trip_bonus(event))
    if box_reports:
        progress.count(store, owner, "trips", len(box_reports))
    # Sammel-Fortschritt + Erfolge (neu geschaffte bringen Bits)
    new_achievements = progress.check(store, owner)
    armor = explore.armor_options(pet) if pet else {}
    return {
        "now": now,
        "speed": SPEED,
        "user": {"name": user["name"], "admin": bool(user["is_admin"])},
        "pet": {**petlib.view(pet, now), **battle.view(pet), **explore.view(pet, now)} if pet else None,
        "report": report,
        "box_reports": box_reports,
        # fits: dieses Armor-Ei passt zum aktiven Digimon
        "inventory": [{"key": k, "count": inventory(owner).get(k, 0), **v, "fits": k in armor, "sell": shop.sell_price(k)}
                      for k, v in explore.ITEMS.items()],
        "areas": explore.areas_for(pet) if pet else [],
        "box_count": len(collection.boxed(store, owner)),
        "free_egg": can_get_free_egg(owner),
        "duel": duel_view,
        "jogress": social.jogress_view(store, user, time.time()),
        "jogress_possible": bool(pet and petlib.jogress_options(pet)),
        "trades_todo": sum(t["todo"] != "wait" for t in social.trades_view(store, user)),
        "announcement": settings.CURRENT["announcement"],
        "maintenance": settings.CURRENT["maintenance"],
        "version": VERSION,
        "release": RELEASE,
        "always_day": day,
        "wishlist": wishlist.get(store, owner),
        "lang": account_lang(owner),
        "bits": shop.balance(store, owner),
        # neues Konto: erst der Fragenkatalog, dann das erste Ei
        "starter": not pet and starter.pending(store, owner),
        "event": events.view(event),
        "event_forced": bool(store.get_meta("event_force", None)),
        "theme": themes.colors(themes.active(store, owner)),       # V-Pet-Design (Farben)
        "decor": decor.visible(store, owner, event),                # Deko, die das Display zeigt
        "achievements_new": new_achievements,
        "dex_count": len(progress.owned(store, owner)),
        "dex_total": len(progress.COLLECTABLE),
    }


def admin_prices():
    """Admin: alle Shop-Preise (Standard / aktuell) und der Daily Steal (heute, festgelegt?)."""
    events_of = {item: ev for ev, items in shop.EVENT_PRICES.items() for item in items}
    rows = [{"key": k, "group": "items", "name": explore.ITEMS[k]["name"], "default": d, "price": shop.price_of(k),
             "unit": "Bits", "event": events_of.get(k)} for k, d in shop.default_prices().items()]
    # Designs und Deko: Bits oder (Event-Sachen) Anzahl Event-Items
    defaults = shop.all_defaults()
    for group, table, cost in (("themes", themes.THEMES, themes.cost), ("decor", decor.DECOR, decor.cost)):
        prefix = "theme" if group == "themes" else "decor"
        for k, t in table.items():
            full = f"{prefix}:{k}"
            if full not in defaults:
                continue                                       # Gratis-Design „Klassisch“
            rows.append({"key": full, "group": group, "name": t["name"], "default": defaults[full],
                         "price": cost(k), "event": t.get("event"),
                         "unit": f"× {explore.ITEMS[t['item']]['name']}" if t.get("item") else "Bits"})
    today = shop.daily_steal(clock.now())
    return {"prices": rows, "discount": round(shop.STEAL_DISCOUNT * 100),
            "daily": {"pin": shop.DAILY_PIN["item"] or "auto", "today": today,
                      "today_name": explore.ITEMS[today]["name"], "regular": shop.price_of(today),
                      "price": shop.steal_price(today)},
            "daily_items": [{"key": k, "name": explore.ITEMS[k]["name"]} for k in shop.PRICES]}


def event_view(user):
    """Event-Tab: Story, Belohnungen, Geister, Event-Ei + Shop-Angebote."""
    owner = str(user["id"])
    key = current_event(clock.now())
    info = events.details(key, clock.now())
    if not info:
        return {"event": None}
    item, item_name = info["item"], info["item_name"]
    offers = []
    for it in shop.EVENT_PRICES.get(key, {}):
        offers.append({"text": T("{item} kaufen: {n} Bits", item=explore.ITEMS[it]["name"], n=shop.price_of(it)),
                       "tab": "items"})
    for o in shop.CANDY_OFFERS.get(key, {}).values():
        offers.append({"text": T("{n}× {item} → {egg}", n=o["cost"], item=explore.ITEMS[o["item"]]["name"],
                                 egg=data.line_name(o["egg"])), "tab": "items"})
    have_themes = themes.owned(store, owner)
    for k, t in themes.THEMES.items():
        if t.get("event") == key:
            offers.append({"text": T("{n}× {item} → Design „{name}“", n=themes.cost(k), item=explore.ITEMS[t["item"]]["name"],
                                     name=t["name"]), "tab": "themes", "owned": k in have_themes})
    have_decor = decor.owned(store, owner)
    for k, d in decor.DECOR.items():
        if d.get("event") == key:
            offers.append({"text": T("{n}× {item} → Deko „{name}“ (während des Events gratis an)", n=decor.cost(k),
                                     item=explore.ITEMS[d["item"]]["name"], name=d["name"]),
                           "tab": "themes", "owned": k in have_decor})
    if item and shop.sell_price(item):
        offers.append({"text": T("{item} verkaufen: {n} Bits pro Stück (im Rucksack)", item=item_name,
                                 n=shop.sell_price(item))})
    return {"event": {**info, "offers": offers}}


def friends_view(user):
    """Eigener Freundescode + Freundesliste (nur Name und online – sonst nichts)."""
    owner = str(user["id"])
    rows = [{"name": u["name"], "online": is_online(u["id"])} for u in friends.users(store, owner)]
    rows.sort(key=lambda r: (not r["online"], r["name"].lower()))
    return {"code": friends.code(store, owner), "friends": rows}


def jogress_menu(user, pet, now):
    """Welche Fusionen gehen gerade, und mit wem (Sammlung / Freunde)?"""
    owner = str(user["id"])
    box = [p for p in collection.boxed(store, owner) if p.get("dex") and not p.get("box_trip")]
    online_friends = []
    for other in friends.users(store, owner):
        if is_online(other["id"]):
            fp = store.active_pet(str(other["id"]))
            if fp:
                petlib.advance(fp, now)
                store.save_pet(fp)
                online_friends.append((other, fp))
    seen, out = set(), []
    for evo, need in petlib.jogress_options(pet):
        key = (evo["to"], str(need))
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "to": evo["to"], "to_name": data.DIGIMON[evo["to"]]["name"],
            "to_stage": petlib.stage_name(evo["stage"]), "need": petlib.need_text(need),
            "box": [{"id": p["id"], "name": petlib.display_name(p)} for p in box if petlib.partner_fits(need, pet, p)],
            "friends": [{"name": u["name"], "partner": petlib.display_name(fp)}
                        for u, fp in online_friends if petlib.partner_fits(need, pet, fp)],
        })
    return out


class Handler(BaseHTTPRequestHandler):
    timeout = 30                         # hängende Verbindungen nicht ewig offen halten

    def log_message(self, fmt, *args):   # Konsole ruhig halten
        pass

    # ------------------------------------------------------------ Fehler abfangen
    def do_GET(self):
        self._safely(self._get)

    def do_POST(self):
        self._safely(self._post)

    def _safely(self, handler):
        """Kein Fehler darf eine Anfrage ohne Antwort lassen."""
        try:
            handler()
        except BadRequest as e:
            self.send_json({"error": i18n.text_of(e) or T("Ungültige Anfrage")}, 400)
        except (ConnectionError, TimeoutError):
            pass                         # Besucher ist weg
        except Exception:                # noqa: BLE001 – unerwartet: protokollieren, 500 senden
            traceback.print_exc()
            try:
                self.send_json({"error": T("Da ist auf dem Server etwas schiefgegangen.")}, 500)
            except Exception:            # noqa: BLE001 – Antwort war evtl. schon halb gesendet
                pass

    def client_ip(self):
        if TRUST_PROXY:
            forwarded = self.headers.get("X-Forwarded-For", "")
            if forwarded:
                return forwarded.split(",")[-1].strip()   # vom eigenen Proxy angehängt
        return self.client_address[0]

    def is_https(self):
        return SECURE or (TRUST_PROXY and self.headers.get("X-Forwarded-Proto", "") == "https")

    # ------------------------------------------------------------ Antworten
    def lang(self):
        """Sprache dieses Geräts (Cookie von static/i18n.js). Fehlt das Cookie – Safari & Co.
        löschen Cookies aus JavaScript nach ein paar Tagen –, gilt die Sprache des Kontos.
        Standard Deutsch."""
        value = self.cookie(LANG_COOKIE)
        if value in i18n.LANGS:
            return value
        token = self.session_token()
        user = store.user_by_session(token) if token else None
        value = account_lang(str(user["id"])) if user else None
        return value if value in i18n.LANGS else "de"

    def send_json(self, obj, status=200, cookie=None):
        # zweisprachige Texte (game/i18n.py) in der Sprache des Geräts
        body = json.dumps(i18n.localize(obj, self.lang()), ensure_ascii=False).encode("utf8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if cookie is not None:
            age = store_lib.SESSION_DAYS * 86400 if cookie else 0
            secure = "; Secure" if self.is_https() else ""
            self.send_header("Set-Cookie",
                             f"{COOKIE}={cookie}; Path=/; HttpOnly; SameSite=Strict; Max-Age={age}{secure}")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        if not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        """JSON-Objekt aus der Anfrage – klein und wirklich ein Objekt."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            raise BadRequest(T("Ungültige Anfrage"))
        if length < 0 or length > MAX_BODY:
            raise BadRequest(T("Anfrage zu groß"))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            raise BadRequest(T("Ungültige Anfrage"))
        if not isinstance(body, dict):
            raise BadRequest(T("Ungültige Anfrage"))
        return body

    # ------------------------------------------------------------ Anmeldung
    def cookie(self, name):
        """Ein Cookie selbst heraussuchen (SimpleCookie verwirft bei fremden,
        ungewöhnlichen Cookies auf derselben Domain gleich alle)."""
        for part in (self.headers.get("Cookie") or "").split(";"):
            key, _, value = part.strip().partition("=")
            if key == name and value:
                return value
        return None

    def session_token(self):
        return self.cookie(COOKIE)

    def current_user(self):
        token = self.session_token()
        user = store.user_by_session(token) if token else None
        if user:
            LAST_SEEN[user["id"]] = time.time()
            store.touch(user["id"], time.time())
        return user

    def locked_out(self, user):
        """Wartungsmodus: nur Admins dürfen spielen. Sendet die Antwort und liefert True."""
        if settings.CURRENT["maintenance"] and not user["is_admin"]:
            self.send_json({"error": T("Wartungsarbeiten – bitte später wieder versuchen."), "maintenance": True}, 503)
            return True
        return False

    def send_download(self, path):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def admin_get(self, user, path):
        """GET /api/admin/... (nur Admins)."""
        if path == "/api/admin/overview":
            size = round(Path(store.db_path).stat().st_size / 1024) if Path(store.db_path).exists() else 0
            online = sum(is_online(u["id"]) for u in store.users_detail())
            return self.send_json(admin.overview(store, online, STARTED, size, backup.list_backups()))
        if path == "/api/admin/users":
            return self.send_json({"users": admin.users(store, clock.now(), is_online)})
        if path == "/api/admin/settings":
            return self.send_json({"settings": settings.CURRENT, "allowed": {
                k: v for k, v in settings.ALLOWED.items() if isinstance(v, list)},
                "invite": accounts.invite_code(store),
                "lines": [{"key": k, "name": v["name"]} for k, v in data.LINES.items()],
                "items": [{"key": k, "name": v["name"]} for k, v in explore.ITEMS.items()]})
        if path == "/api/admin/prices":
            return self.send_json(admin_prices())
        if path == "/api/admin/activity":
            return self.send_json({"activity": store.activity(150), "diary": admin.recent_diary(store)})
        if path == "/api/admin/backups":
            return self.send_json({"backups": backup.list_backups()})
        return self.send_error(404)

    def backup_download(self):
        """Backup herunterladen – Rechte unter der Sperre prüfen, die (evtl.
        langsame) Übertragung danach, damit das Spiel solange weiterläuft."""
        from urllib.parse import parse_qs, urlparse
        with store.lock:
            user = self.current_user()
            if not user or not user["is_admin"]:
                return self.send_json({"error": T("Nur für Admins.")}, 403)
            name = parse_qs(urlparse(self.path).query).get("name", [""])[0]
            try:
                path = backup.path_for(name)
            except ValueError as e:
                return self.send_json({"error": i18n.text_of(e)}, 404)
        self.send_download(path)

    def admin_post(self, user, path, body):
        """POST /api/admin/... (nur Admins)."""
        now = clock.now()
        try:
            if path == "/api/admin/user":
                message, extra = admin.user_action(store, user, body.get("name"), body.get("action"),
                                                   body, now, add_item)
                store.log_activity(user["name"], f"Admin: {message}" if "Passwort" not in message
                                   else f"Admin: Passwort von {body.get('name')} zurückgesetzt")
                return self.send_json({"message": message, **extra,
                                       "users": admin.users(store, now, is_online)})
            if path == "/api/admin/settings":
                before = dict(settings.CURRENT)
                new = settings.update(store, body.get("changes") or {})
                changed = [k for k in new if new[k] != before[k]]
                if changed:
                    store.log_activity(user["name"], "Admin: Einstellungen geändert: " + ", ".join(changed))
                return self.send_json({"message": "Gespeichert.", "settings": new})
            if path == "/api/admin/prices":
                prices = body.get("prices") or {}
                if not isinstance(prices, dict):
                    raise ValueError("Ungültige Preise.")
                shop.set_prices(store, prices, as_text(body.get("daily")) or "auto")
                store.log_activity(user["name"], "Admin: Shop-Preise / Daily Steal geändert")
                return self.send_json({"message": "Gespeichert – gilt sofort im Shop.", **admin_prices()})
            if path == "/api/admin/backup/restore":
                taken = backup.path_for(body.get("name")).stat().st_mtime
                safety = backup.restore(store, body.get("name"))
                # Speicher des Servers an den eingespielten Stand anpassen
                settings.load(store)
                shop.load(store)
                clock.reload()
                restored_pets_wait(taken)
                LAST_SEEN.clear()
                # alte Anmeldungen aus dem Backup gelten nicht (gesperrte/zurückgesetzte
                # Spieler kämen sonst wieder rein) – nur der Admin bleibt angemeldet
                store.db.execute("DELETE FROM sessions")
                store.db.commit()
                again = store.user_by_name(user["name"])
                cookie = None
                if again and again["is_admin"]:
                    cookie = accounts.start_session(store, again["id"])
                store.log_activity(user["name"], f"Admin: Backup {body.get('name')} eingespielt "
                                                 f"(vorheriger Stand gesichert als {safety})")
                return self.send_json({"message": f"Backup eingespielt. Der vorherige Stand liegt in {safety}. "
                                                  "Alle Spieler müssen sich neu anmelden.", "reload": True},
                                      cookie=cookie)
            if path == "/api/admin/backup/delete":
                backup.delete(body.get("name"))
                store.log_activity(user["name"], f"Admin: Backup {body.get('name')} gelöscht")
                return self.send_json({"message": "Backup gelöscht.", "backups": backup.list_backups()})
            if path == "/api/admin/invite/new":
                code = accounts.new_invite_code(store)
                store.log_activity(user["name"], "Admin: neuer Einladungscode")
                return self.send_json({"code": code})
        except petlib.Refused as e:
            return self.send_json({"error": i18n.text_of(e)}, 400)
        except (ValueError, TypeError) as e:
            return self.send_json({"error": str(e) or "Ungültige Anfrage"}, 400)
        except OSError as e:             # Datei gesperrt/fehlt (Backups)
            return self.send_json({"error": f"Datei-Fehler: {e.strerror or e}"}, 500)
        return self.send_error(404)

    # ------------------------------------------------------------ GET
    def _get(self):
        path = self.path.split("?")[0]
        if path == "/api/admin/backup/download":
            return self.backup_download()
        if path.startswith("/api/"):
            with store.lock:
                user = self.current_user()
                if path == "/api/me":
                    return self.send_json({
                        "user": {"name": user["name"], "admin": bool(user["is_admin"])} if user else None,
                        # online (VPET_PUBLIC) gibt es kein "erstes Konto ohne Code"
                        "first_user": store.user_count() == 0 and not os.environ.get("VPET_PUBLIC"),
                        "registration": settings.CURRENT["registration"],
                        "maintenance": settings.CURRENT["maintenance"],
                        "announcement": settings.CURRENT["announcement"],
                        "version": VERSION,
                        "release": RELEASE,
                        "lang": account_lang(str(user["id"])) if user else None,
                    })
                if not user:
                    return self.send_json({"error": T("Bitte melde dich an.")}, 401)
                if self.locked_out(user):
                    return
                if path.startswith("/api/admin/"):
                    if not user["is_admin"]:
                        return self.send_json({"error": T("Nur für Admins.")}, 403)
                    return self.admin_get(user, path)
                if path == "/api/state":
                    return self.send_json(current_state(user))
                if path == "/api/players":
                    # deine Freunde: online? Partner? kampfbereit? – WARUM einer nicht kann (z. B. wann
                    # sein Digimon vom Erkunden zurück ist), verraten wir nicht
                    now = clock.now()
                    out = []
                    for other in friends.users(store, str(user["id"])):
                        pet = store.active_pet(str(other["id"]))
                        if pet:
                            petlib.advance(pet, now)
                            store.save_pet(pet)          # sonst wird jedes Mal neu gerechnet
                        try:
                            duel_lib._ready(pet, other["name"])
                            ready = True
                        except petlib.Refused:
                            ready = False
                        out.append({"name": other["name"], "online": is_online(other["id"]),
                                    "partner": petlib.display_name(pet) if pet and pet.get("alive") else None,
                                    "stage_de": petlib.stage_name(pet["stage"]) if pet else None,
                                    "ready": ready, "why": None if ready else T("kann gerade nicht kämpfen")})
                    out.sort(key=lambda p: (not p["online"], p["name"].lower()))
                    return self.send_json({"players": out})
                if path == "/api/jogress":
                    pet = store.active_pet(str(user["id"]))
                    if not pet:
                        return self.send_json({"options": []})
                    petlib.advance(pet, clock.now())
                    store.save_pet(pet)
                    return self.send_json({"options": jogress_menu(user, pet, clock.now())})
                if path == "/api/friends":
                    return self.send_json(friends_view(user))
                if path == "/api/event":
                    return self.send_json(event_view(user))
                if path == "/api/trades":
                    return self.send_json({"trades": social.trades_view(store, user)})
                if path == "/api/wishlist":
                    return self.send_json({"wishlist": wishlist.get(store, str(user["id"]))})
                if path == "/api/backups":
                    if not user["is_admin"]:
                        return self.send_json({"error": T("Nur für den Admin.")}, 403)
                    return self.send_json({"backups": backup.list_backups()})
                if path == "/api/ranking":
                    return self.send_json({"ranking": collection.ranking(store)})
                if path == "/api/box":
                    return self.send_json(collection.overview(store, str(user["id"]), clock.now()))
                if path == "/api/shop":
                    event = current_event(clock.now())
                    return self.send_json({"shop": shop.catalog(event, clock.now()), "bits": shop.balance(store, str(user["id"])),
                                           "candy_offers": shop.candy_offers(event)})
                if path == "/api/themes":
                    event = current_event(clock.now())
                    return self.send_json({"themes": themes.catalog(store, str(user["id"]), event),
                                           "decor": decor.catalog(store, str(user["id"]), event)})
                if path == "/api/progress":
                    # Sammel-Fortschritt (Digidex) und alle Erfolge
                    return self.send_json(progress.view(store, str(user["id"])))
                if path == "/api/starter":
                    # Fragenkatalog fürs erste Ei: eine zufällige Auswahl an Fragen
                    if not starter.pending(store, str(user["id"])):
                        return self.send_json({"error": T("Den Fragenkatalog hast du schon beantwortet.")}, 400)
                    return self.send_json({"questions": starter.questions()})
                if path == "/api/invite":
                    if not user["is_admin"]:
                        return self.send_json({"error": T("Nur für den Admin.")}, 403)
                    return self.send_json({"code": accounts.invite_code(store)})
            return self.send_error(404)
        if path == "/data/digimon.json":
            return self.send_file(ROOT / "data" / "digimon.json")
        if path == "/":
            path = "/index.html"
        target = (STATIC / path.lstrip("/")).resolve()
        if STATIC.resolve() not in target.parents:
            return self.send_error(404)
        self.send_file(target)

    # ------------------------------------------------------------ Anmelden / Registrieren
    def auth(self, path, body):
        """Anmelden und Registrieren. Das (absichtlich langsame) Passwort-Rechnen
        läuft OHNE die Datenbank-Sperre, damit falsche Versuche nicht das Spiel
        für alle anhalten. Wiederholte Fehlversuche werden gebremst."""
        ip, name = self.client_ip(), body.get("name")
        wait = login_blocked(ip, name)
        if wait:
            return self.send_json({"error": T("Zu viele Versuche. Bitte in {n} Minuten noch einmal probieren.",
                                              n=wait // 60 + 1)}, 429)
        try:
            if path == "/api/register":
                with store.lock:
                    clean_name = accounts.register_check(store, name, body.get("password"), body.get("invite"))
                pw_hash, salt = accounts.new_password_hash(body.get("password"))
                with store.lock:
                    token = accounts.register_finish(store, clean_name, pw_hash, salt)
            else:
                with store.lock:
                    user = accounts.login_lookup(store, name)
                if not accounts.password_ok(user, body.get("password")):
                    raise accounts.AuthError(T("Name oder Passwort falsch."))
                with store.lock:
                    token = accounts.login_finish(store, user)
        except accounts.AuthError as e:
            login_failed(ip, name)
            if path == "/api/login":
                time.sleep(0.3)          # ohne Sperre – bremst nur diesen Versuch
            return self.send_json({"error": i18n.text_of(e)}, 400)
        with store.lock:
            user = store.user_by_session(token)
            owner = str(user["id"])
            if path == "/api/register":
                store.log_activity(user["name"], "hat ein Konto erstellt")
                if body.get("lang") in i18n.LANGS:      # Sprache, in der man sich registriert hat
                    store.set_meta(f"lang:{user['id']}", body["lang"])
                if not store.active_pet(owner):
                    starter.start(store, owner)          # erstes Ei per Fragenkatalog (game/starter.py)
            elif not store.active_pet(owner) and not starter.pending(store, owner):
                new_random_egg(owner, clock.now())
        return self.send_json({"ok": True}, cookie=token)

    # ------------------------------------------------------------ POST
    def _post(self):
        path = self.path.split("?")[0]
        body = self.read_body()
        if path in ("/api/register", "/api/login"):
            return self.auth(path, body)
        with store.lock:
            now = clock.now()

            if path == "/api/logout":
                token = self.session_token()
                if token:
                    store.delete_session(token)
                return self.send_json({"ok": True}, cookie="")

            user = self.current_user()
            if not user:
                return self.send_json({"error": T("Bitte melde dich an.")}, 401)
            if self.locked_out(user):
                return
            if path.startswith("/api/admin/"):
                if not user["is_admin"]:
                    return self.send_json({"error": T("Nur für Admins.")}, 403)
                if path != "/api/admin/reset":          # alter Weg aus den Einstellungen
                    return self.admin_post(user, path, body)
            owner = str(user["id"])

            if path == "/api/password":
                try:
                    accounts.change_password(store, user["id"], body.get("old"), body.get("new"),
                                             self.session_token())
                except accounts.AuthError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": T("Passwort geändert. Andere Geräte wurden abgemeldet.")})

            if path == "/api/lang":
                # Sprache fürs Konto merken – gilt dann auf allen Geräten
                lang = as_text(body.get("lang"))
                if lang not in i18n.LANGS:
                    return self.send_json({"error": T("Diese Sprache gibt es nicht.")}, 400)
                store.set_meta(f"lang:{owner}", lang)
                return self.send_json({"lang": lang})

            if path == "/api/wishlist":
                try:
                    dex = as_int(body.get("dex"), 0)
                    wanted = wishlist.toggle(store, owner, dex, bool(body.get("on")))
                except ValueError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                pet = store.active_pet(owner)
                if not body.get("on") and pet and pet.get("goal") == dex:
                    pet.pop("goal")                       # von der Merkliste genommen -> kein Ziel mehr
                    store.save_pet(pet)
                return self.send_json({"wishlist": wanted})

            if path == "/api/goal":
                # Ziel für das aktive Digimon (Merkliste pro Digimon); dex = null -> kein Ziel
                pet = store.active_pet(owner)
                if not pet or not pet.get("dex"):
                    return self.send_json({"error": T("Dafür brauchst du ein geschlüpftes Digimon.")}, 400)
                try:
                    dex = None if body.get("dex") is None else as_int(body.get("dex"))
                    message = wishlist.set_goal(store, owner, pet, dex)
                except ValueError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.save_pet(pet)
                return self.send_json({"message": message, **current_state(user)})

            if path in ("/api/admin/reset", "/api/backup"):
                if not user["is_admin"]:
                    return self.send_json({"error": T("Nur für den Admin.")}, 403)
                if path == "/api/backup":
                    return self.send_json({"message": f"Backup gespeichert: {backup.make_backup(store, 'manuell')}",
                                           "backups": backup.list_backups()})
                try:
                    temp = accounts.reset_password(store, body.get("name"))
                except accounts.AuthError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"password": temp,
                                       "message": f"Neues Passwort für {body.get('name')}: {temp}"})

            if path in ("/api/friends/add", "/api/friends/remove", "/api/friends/newcode"):
                try:
                    if path.endswith("add"):
                        message = friends.add(store, user, as_text(body.get("code")))
                        store.log_activity(user["name"], f"Freund: {message}")
                    elif path.endswith("remove"):
                        message = friends.remove(store, user, as_text(body.get("name")))
                    else:
                        friends.new_code(store, owner)
                        message = T("Neuer Freundescode – der alte gilt nicht mehr.")
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, **friends_view(user)})

            if path == "/api/friends/profile":
                # was ein Freund für Digimon hat – friends.profile prüft, dass ihr befreundet seid
                try:
                    view = friends.profile(store, user, as_text(body.get("name")))
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                other = store.user_by_name(view["name"])
                return self.send_json({"profile": {**view, "online": is_online(other["id"])}})

            if path.startswith("/api/trade/"):
                step = path.rsplit("/", 1)[1]
                try:
                    req_id = as_int(body.get("id"), 0)
                    if step == "offer":
                        target = store.user_by_name(as_text(body.get("name")))
                        friends.check(store, user, target)
                        message = social.offer(store, user, target, as_int(body.get("pet_id"), 0), body.get("gift") is True)
                    elif step == "gift":
                        message = social.accept_gift(store, user, req_id)
                    elif step == "counter":
                        message = social.counter(store, user, req_id, as_int(body.get("pet_id"), 0))
                    elif step == "confirm":
                        message = social.confirm(store, user, req_id)
                    elif step == "decline":
                        message = social.decline(store, user, req_id)
                    else:
                        return self.send_error(404)
                except (TypeError, ValueError):
                    return self.send_json({"error": T("Ungültige Anfrage")}, 400)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                if step in ("gift", "confirm"):
                    store.log_activity(user["name"], f"Tausch: {message}")
                return self.send_json({"message": message, "trades": social.trades_view(store, user),
                                       "collection": collection.overview(store, owner, now),
                                       **current_state(user)})

            if path.startswith("/api/jogress/"):
                step = path.rsplit("/", 1)[1]
                real = time.time()
                try:
                    pet = store.active_pet(owner)
                    if pet:
                        petlib.advance(pet, now)
                    if step == "box":
                        partner = social._boxed_pet(store, as_int(body.get("partner_id"), 0), user["id"])
                        if not pet or not partner:
                            raise petlib.Refused(T("Dieser Partner ist nicht in deiner Sammlung."))
                        collection._trip_check(partner)          # gerade beim Erkunden?
                        message = petlib.jogress(pet, as_int(body.get("to"), 0), partner, None, now)
                        store.save_pet(pet)
                    elif step == "ask":
                        target = store.user_by_name(as_text(body.get("name")))
                        friends.check(store, user, target)
                        if not is_online(target["id"]):
                            raise petlib.Refused(T("Dein Freund ist gerade nicht online."))
                        partner = store.active_pet(str(target["id"]))
                        if partner:
                            petlib.advance(partner, now)
                        if not pet:
                            raise petlib.Refused(T("Du hast gerade kein Digimon."))
                        petlib._awake_check(pet)
                        message = social.jogress_ask(store, user, target, pet, as_int(body.get("to"), 0),
                                                     partner, real)
                    elif step == "answer":
                        reqs = [r for r in store.requests_for(user["id"], "jogress", ("pending",))
                                if r["b"] == user["id"]]
                        if not reqs:
                            raise petlib.Refused(T("Es gibt keine offene Anfrage."))
                        pets = {"a": store.active_pet(str(reqs[0]["a"])), "b": pet}
                        if pets["a"]:
                            petlib.advance(pets["a"], now)
                        message = social.jogress_answer(store, user, bool(body.get("accept")), pets, real)
                        for p in pets.values():
                            if p:
                                store.save_pet(p)
                    else:
                        return self.send_error(404)
                except (TypeError, ValueError):
                    return self.send_json({"error": T("Ungültige Anfrage")}, 400)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                if step in ("box", "answer") and "Jogress" in message:
                    store.log_activity(user["name"], message.replace("Geschafft! ", ""))
                    # Erfolg „Zwei werden eins“: zählt für den, dessen Digimon digitiert ist
                    progress.count(store, owner if step == "box" else str(reqs[0]["a"]), "jogress")
                return self.send_json({"message": message, **current_state(user)})

            if path.startswith("/api/duel/"):
                step = path.rsplit("/", 1)[1]
                real = time.time()
                try:
                    if step == "challenge":
                        target = store.user_by_name(as_text(body.get("name")))
                        friends.check(store, user, target)
                        if not is_online(target["id"]):
                            raise petlib.Refused(T("{name} ist gerade nicht online.", name=target["name"]))
                        mine, theirs = store.active_pet(owner), store.active_pet(str(target["id"]))
                        for pet in (mine, theirs):
                            if pet:
                                petlib.advance(pet, now)
                        duel_lib.challenge(store, user, target, mine, theirs, real)
                        message = T("Herausforderung an {name} geschickt. Warte auf Antwort ...", name=target["name"])
                    else:
                        duel = store.latest_duel(user["id"])
                        if not duel or duel["status"] not in duel_lib.OPEN:
                            raise petlib.Refused(T("Gerade läuft kein Kampf."))
                        pets = duel_pets(duel, now)
                        side = duel_lib.side_of(duel, user["id"])
                        if step == "answer":
                            if side != "b":
                                raise petlib.Refused(T("Auf deine eigene Herausforderung kannst du nicht antworten."))
                            message = duel_lib.answer(duel, bool(body.get("accept")), pets, real)
                        elif step == "shoot":
                            # {"aim", "charge"} / {"special", "mash"} / alte Form {"quality"}
                            duel_lib.shoot(duel, side, body, pets, real)
                            message = ""
                        elif step == "dodge":
                            duel_lib.dodge(duel, side, body.get("dodged") is True, pets, real)
                            message = ""
                        elif step == "cancel":
                            message = duel_lib.cancel(duel, side, real)
                        elif step == "forfeit":
                            message = duel_lib.forfeit(duel, side, pets, real)
                        else:
                            return self.send_error(404)
                        save_duel(duel, pets)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, **current_state(user)})

            if path == "/api/invite/new":
                if not user["is_admin"]:
                    return self.send_json({"error": T("Nur für den Admin.")}, 403)
                return self.send_json({"code": accounts.new_invite_code(store)})

            if path == "/api/starter":
                # Antworten auswerten -> Persönlichkeitstyp + passendes erstes Ei
                if not starter.pending(store, owner) or store.active_pet(owner):
                    return self.send_json({"error": T("Den Fragenkatalog hast du schon beantwortet.")}, 400)
                try:
                    kind, line = starter.evaluate(body.get("answers"))
                except ValueError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.add_pet(owner, petlib.new_egg(line, now))
                starter.finish(store, owner)
                store.log_activity(user["name"], f"Fragenkatalog: {starter.TYPES[kind]['name']} -> {data.LINES[line]['name']}")
                return self.send_json({"result": starter.result_view(kind, line), **current_state(user)})

            if path == "/api/egg":
                # Gratis-Ei nur als Notnagel; sonst gibt es Eier beim Erkunden und Kämpfen
                if starter.pending(store, owner) and not store.active_pet(owner):
                    return self.send_json({"error": T("Beantworte zuerst die Fragen – dann bekommst du dein erstes Digi-Ei.")}, 400)
                if not can_get_free_egg(owner):
                    return self.send_json({"error": T("Neue Eier findest du beim Erkunden und in Kämpfen.")}, 400)
                collection.new_egg(store, owner, now)
                return self.send_json({"message": T("Ein neues Digi-Ei!"), **current_state(user)})

            if path == "/api/item" and as_text(body.get("item")) in explore.SHARD_ITEMS:
                # 4 Ei-Scherben -> Digi-Ei in die Sammlung (geht auch ohne aktives Digimon)
                item = as_text(body.get("item"))
                try:
                    message = collection.combine_shards(store, owner, item, inventory(owner).get(item, 0),
                                                        lambda n: add_item(owner, item, -n), now)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, "anim": None, **current_state(user)})

            if path == "/api/item" and body.get("id") is not None:
                # Sanduhr für ein Digimon aus der Sammlung
                try:
                    item = as_text(body.get("item"))
                    if inventory(owner).get(item, 0) <= 0:
                        raise petlib.Refused(T("Davon hast du nichts mehr im Rucksack."))
                    message = collection.use_hourglass(store, owner, as_int(body.get("id")), item, now)
                    add_item(owner, item, -1)
                except (TypeError, ValueError):
                    return self.send_json({"error": T("Ungültige Anfrage")}, 400)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, **current_state(user),
                                       "collection": collection.overview(store, owner, now)})

            if path in ("/api/explore", "/api/explore/recall", "/api/explore/confirm", "/api/item"):
                pet = store.active_pet(owner)
                if not pet:
                    return self.send_json({"error": T("Du hast gerade kein Digimon.")}, 400)
                petlib.advance(pet, now)
                anim = None
                try:
                    if path == "/api/explore":
                        if in_open_duel(user):
                            raise petlib.Refused(T("Erst den Kampf gegen deinen Freund beenden."))
                        message = explore.start(pet, as_text(body.get("area")), as_int(body.get("minutes"), 0), now)
                    elif path == "/api/explore/recall":
                        message = explore.recall(pet, now)
                    elif path == "/api/explore/confirm":
                        # Rückkehr bestätigt -> die Zeit läuft wieder (Fail-Safe, game/pet.py)
                        message = petlib.confirm_return(pet, now)
                        anim = "return"
                    else:
                        item = as_text(body.get("item"))
                        if item == "everstone" and pet.get("everstone"):
                            # Ewigstein abnehmen: zurück in den Rucksack
                            anim, message = explore.take_everstone(pet, now)
                            add_item(owner, item, 1)
                        else:
                            if inventory(owner).get(item, 0) <= 0:
                                raise petlib.Refused(T("Davon hast du nichts mehr im Rucksack."))
                            anim, message = explore.use_item(pet, item, now)
                            add_item(owner, item, -1)
                except (TypeError, ValueError):
                    return self.send_json({"error": T("Ungültige Anfrage")}, 400)
                except petlib.Refused as e:
                    store.save_pet(pet)
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.save_pet(pet)
                return self.send_json({"message": message, "anim": anim, **current_state(user)})

            if path == "/api/nickname":
                # Spitzname für das aktive Digimon oder (mit id) eins aus der Sammlung
                pet_id = body.get("id")
                if pet_id is None:
                    pet = store.active_pet(owner)
                else:
                    pet = next((p for p in collection.boxed(store, owner) if p["id"] == as_int(pet_id)), None)
                if not pet:
                    return self.send_json({"error": T("Dieses Digimon gibt es nicht.")}, 400)
                try:
                    message = petlib.set_nickname(pet, as_text(body.get("name")), now)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.save_pet(pet)
                extra = {"collection": collection.overview(store, owner, now)} if pet_id is not None else {}
                return self.send_json({"message": message, **current_state(user), **extra})

            if path in ("/api/box/switch", "/api/box/release", "/api/box/move", "/api/box/name",
                        "/api/box/explore", "/api/box/recall"):
                try:
                    if path.endswith("explore"):
                        message = collection.send(store, owner, as_int(body.get("id")), as_text(body.get("area")),
                                                  as_int(body.get("minutes"), 0), now)
                    elif path.endswith("recall"):
                        message = collection.recall_trip(store, owner, as_int(body.get("id")), now)
                    elif path.endswith("switch"):
                        if in_open_duel(user):
                            raise petlib.Refused(T("Erst den Kampf gegen deinen Freund beenden."))
                        message = collection.switch(store, owner, as_int(body.get("id")), now)
                    elif path.endswith("release"):
                        message = collection.release(store, owner, as_int(body.get("id")))
                    elif path.endswith("move"):
                        message = collection.move(store, owner, as_int(body.get("id")), as_int(body.get("box")))
                    else:
                        message = collection.rename_box(store, owner, as_int(body.get("box")), as_text(body.get("name")))
                except (TypeError, ValueError):
                    return self.send_json({"error": T("Ungültige Auswahl.")}, 400)
                except petlib.Refused as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, **current_state(user),
                                       "collection": collection.overview(store, owner, now)})

            if path == "/api/fridge":
                pet = store.active_pet(owner)
                if not pet:
                    return self.send_json({"error": T("Du hast gerade kein Digimon.")}, 400)
                petlib.advance(pet, now)
                try:
                    if body.get("on") is True and in_open_duel(user):
                        raise petlib.Refused(T("Erst den Kampf gegen deinen Freund beenden."))
                    message = petlib.set_frozen(pet, body.get("on") is True, now)
                except petlib.Refused as e:
                    store.save_pet(pet)
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.save_pet(pet)
                return self.send_json({"message": message, **current_state(user)})

            if path.startswith("/api/battle/"):
                pet = store.active_pet(owner)
                if not pet:
                    return self.send_json({"error": T("Du hast gerade kein Digimon.")}, 400)
                petlib.advance(pet, now)
                step = path.rsplit("/", 1)[1]
                extra = {}
                try:
                    if step == "scout":
                        message = battle.scout(pet, now, event=current_event(now))
                    elif step == "flee":
                        message = battle.flee(pet, now)
                    elif step == "fight":
                        message = battle.fight(pet, now)
                    elif step == "shot":
                        # {"aim", "charge"} / {"special", "mash"} / alte Form {"quality"}
                        extra["round"] = result = battle.shot(pet, body, now)
                        message = result.get("message", "")
                    elif step == "dodge":
                        # Ausweichen: {"dodged": [true/false pro Angriff]} – der Kampf kann hier enden
                        extra["round"] = result = battle.evade(pet, body.get("dodged"), now)
                        message = result.get("message", "")
                    else:
                        return self.send_error(404)
                except petlib.Refused as e:
                    store.save_pet(pet)
                    return self.send_json({"error": i18n.text_of(e), **current_state(user)}, 400)
                store.save_pet(pet)
                # nach dem Kampfende (bei "shot" oder "dodge"): Bits, Erfolge, Event-Item, Ei
                result = extra.get("round", {})
                if result.get("bits"):
                    shop.add(store, owner, result["bits"])              # Bits für den Kampf
                if result.get("won"):                                   # Zähler für die Erfolge
                    progress.count(store, owner, "wins")
                    if result.get("ghost"):
                        progress.count(store, owner, "ghosts")
                if result.get("candy"):
                    add_item(owner, "candy")                            # Event-Item vom Geist
                egg_line = extra.get("round", {}).get("egg_line")
                if egg_line and not collection.store_egg(store, owner, egg_line, now):
                    message += " " + T("Aber deine Sammlung ist voll – das Ei bleibt liegen.")
                elif egg_line:
                    message += " " + T("Es liegt jetzt in deiner Sammlung.")
                return self.send_json({"message": message, **extra, **current_state(user)})

            if path == "/api/cheat":
                if not user["is_admin"]:
                    return self.send_json({"error": "Cheats gibt es nur für den Admin."}, 403)
                op = as_text(body.get("op"))
                pet = store.active_pet(owner)
                if op == "egg":                       # Ei einer bestimmten Sorte
                    line = as_text(body.get("line"))
                    if line not in data.LINES:
                        return self.send_json({"error": "Diese Ei-Sorte gibt es nicht."}, 400)
                    try:
                        collection.new_egg(store, owner, now, line=line, cheated=True)
                    except petlib.Refused as e:
                        return self.send_json({"error": i18n.text_of(e)}, 400)
                    return self.send_json({"message": f"Cheat: {data.LINES[line]['name']}",
                                           **current_state(user)})
                if op == "item":                      # Items in den Rucksack
                    item = as_text(body.get("item"))
                    if item not in explore.ITEMS:
                        return self.send_json({"error": "Dieses Item gibt es nicht."}, 400)
                    try:
                        amount = cheats.amount(body.get("amount"))
                    except petlib.Refused as e:
                        return self.send_json({"error": i18n.text_of(e)}, 400)
                    add_item(owner, item, amount)
                    return self.send_json({"message": f"Cheat: {amount}× {explore.ITEMS[item]['name']} in den Rucksack.",
                                           **current_state(user)})
                if op == "event":                     # Event erzwingen (zum Testen vor dem Start)
                    key = as_text(body.get("key"))
                    store.set_meta("event_force", key if key in events.EVENTS else None)
                    return self.send_json({"message": f"Cheat: Event {key} erzwungen." if key in events.EVENTS
                                           else "Cheat: Events wieder nach Kalender.", **current_state(user)})
                if op == "bits":                      # Bits fürs Testen des Shops
                    try:
                        amount = cheats.amount(body.get("amount"))
                    except petlib.Refused as e:
                        return self.send_json({"error": i18n.text_of(e)}, 400)
                    shop.add(store, owner, amount * 10)
                    return self.send_json({"message": f"Cheat: +{amount * 10} Bits.", **current_state(user)})
                if op == "day":                       # Immer Tag: keine Digimon des Kontos schläft
                    store.set_meta(f"always_day:{owner}", body.get("on") is True)
                    return self.send_json({"message": "Cheat: Immer Tag – deine Digimon schlafen nicht."
                                           if body.get("on") is True else "Cheat: Tag und Nacht wieder normal.",
                                           **current_state(user)})
                if not pet:
                    return self.send_json({"error": "Du hast gerade kein Digimon."}, 400)
                petlib.advance(pet, now)
                try:
                    message = cheats.apply(pet, op, body, now)
                except petlib.Refused as e:
                    store.save_pet(pet)
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.save_pet(pet)
                return self.send_json({"message": message, **current_state(user)})

            if path == "/api/action":
                pet = store.active_pet(owner)
                action = ACTIONS.get(as_text(body.get("action")))
                if not pet or not action:
                    return self.send_json({"error": T("Das geht gerade nicht.")}, 400)
                petlib.advance(pet, now)
                try:
                    anim, message = action(pet, body, now)
                except petlib.Refused as e:
                    store.save_pet(pet)
                    return self.send_json({"anim": "refuse", "message": i18n.text_of(e), **current_state(user)})
                if as_text(body.get("action")) == "clean":
                    found = shop.clean_reward()             # selten: Bits zwischen der Kacke
                    if found:
                        shop.add(store, owner, found)
                        message = message + " " + T("Da glitzert was: {n} Bits!", n=found)
                store.save_pet(pet)
                return self.send_json({"anim": anim, "message": message, **current_state(user)})

            if path in ("/api/decor/buy", "/api/decor/toggle"):
                key, event = as_text(body.get("key")), current_event(now)
                try:
                    if path.endswith("buy"):
                        message = decor.buy(store, owner, key, inventory(owner),
                                            lambda item, n: add_item(owner, item, n), event)
                        store.log_activity(user["name"], f"Deko gekauft: {key}")
                    else:
                        message = decor.toggle(store, owner, key, body.get("on") is True, event)
                except decor.DecorError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, "decor_list": decor.catalog(store, owner, event),
                                       **current_state(user)})

            if path in ("/api/theme/buy", "/api/theme/use"):
                key = as_text(body.get("key"))
                try:
                    if path.endswith("buy"):
                        message = themes.buy(store, owner, key, inventory(owner),
                                             lambda item, n: add_item(owner, item, n), event=current_event(now))
                        store.log_activity(user["name"], f"Design gekauft: {key}")
                    else:
                        message = themes.use(store, owner, key)
                except themes.ThemeError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                return self.send_json({"message": message, "themes": themes.catalog(store, owner, current_event(now)),
                                       **current_state(user)})

            if path == "/api/shop/candy":
                # Event-Items eintauschen (z. B. 15 Gruselbonbons -> Digi-Ei Halloween)
                try:
                    message = shop.trade_candy(as_text(body.get("key")), current_event(now), inventory(owner),
                                               lambda item, n: add_item(owner, item, n),
                                               lambda line: collection.store_egg(store, owner, line, now))
                except shop.ShopError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.log_activity(user["name"], f"Shop-Tausch: {message}")
                return self.send_json({"message": message, "candy_offers": shop.candy_offers(current_event(now)),
                                       **current_state(user)})

            if path == "/api/shop/sell":
                # Items aus dem Rucksack gegen Bits verkaufen – egal was, egal wie viele
                try:
                    message = shop.sell(store, owner, as_text(body.get("item")), as_int(body.get("amount"), 1),
                                        inventory(owner), lambda item, n: add_item(owner, item, n))
                except shop.ShopError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.log_activity(user["name"], f"Verkauf: {message}")
                return self.send_json({"message": message, **current_state(user)})

            if path == "/api/shop/buy":
                try:
                    message = shop.buy(store, owner, as_text(body.get("item")), as_int(body.get("amount"), 1),
                                       lambda item, n: add_item(owner, item, n), event=current_event(now), minute=now)
                except shop.ShopError as e:
                    return self.send_json({"error": i18n.text_of(e)}, 400)
                store.log_activity(user["name"], f"Shop: {message}")
                return self.send_json({"message": message, "shop": shop.catalog(current_event(now), now),
                                       **current_state(user)})
        self.send_error(404)


def main():
    # Standard: nur auf diesem PC erreichbar (VPET_HOST ändert das fürs Online-Stellen)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.daemon_threads = True
    url = f"http://localhost:{PORT}"
    print(f"Digimon V-Pet läuft auf {url}  (Zeit x{SPEED:g})")
    if store.user_count() == 0 and os.environ.get("VPET_PUBLIC"):
        print("Noch kein Konto: Admin anlegen mit  python tools/admin_account.py <name>")
    elif store.user_count() == 0:
        print("Noch kein Konto: das erste Konto braucht keinen Einladungscode und wird Admin.")
    else:
        print(f"Backup beim Start: backups/{backup.make_backup(store, 'start')}")

    def auto_backup():
        while True:
            time.sleep(backup.EVERY)
            try:
                backup.make_backup(store)
            except Exception as e:          # ein fehlgeschlagenes Backup soll das Spiel nicht stoppen
                print("Backup fehlgeschlagen:", e)
    threading.Thread(target=auto_backup, daemon=True).start()
    print("Zum Beenden: Strg+C oder dieses Fenster schließen.")
    if not os.environ.get("VPET_NO_BROWSER"):
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        clock.save()


if __name__ == "__main__":
    main()
