# Digimon V-Pet

Ein Digimon-Tamagotchi im Browser – wie das Original-V-Pet von 1997, mit Konten, Kämpfen
gegen Freunde, Tausch, Jogress, Events und einem Shop. Deutsch und Englisch.

- **Technik:** Python-Standardbibliothek als Server (keine Pakete), Vanilla-JavaScript im
  Browser (kein Build-Schritt), SQLite als Spielstand, Docker zum Hosten.
- **Spielregeln für Spieler:** stehen im Spiel unter **?** (`static/hilfe.html`) – diese README
  erklärt das Projekt, nicht das Spiel im Detail.

> **Für Agenten (Claude & Co.):** Lies vor jeder Änderung den Abschnitt
> [Regeln für Änderungen](#regeln-für-änderungen). Kurzfassung: lokal bauen → alle Tests grün →
> deutsch **und** englisch → Hilfe + Changelog pflegen → **nur auf ausdrückliche Anweisung deployen**.

---

## Inhalt

1. [Was das Spiel kann](#was-das-spiel-kann)
2. [Lokal starten](#lokal-starten)
3. [Projektaufbau](#projektaufbau)
4. [Wie es technisch funktioniert](#wie-es-technisch-funktioniert)
5. [Regeln für Änderungen](#regeln-für-änderungen)
6. [Häufige Aufgaben](#häufige-aufgaben)
7. [Online-Server & Deploy](#online-server--deploy)
8. [Konten, Admin & Backups](#konten-admin--backups)
9. [Auf GitHub hochladen](#auf-github-hochladen)
10. [Credits](#credits)

---

## Was das Spiel kann

| Bereich | Kurz | Code |
|---|---|---|
| Pflege | Füttern, Training (3 Minispiele), Putzen, Licht/Schlaf, Medizin, Rufe & Pflegefehler, Tod | `game/pet.py` |
| Entwicklung | 30 Ei-Sorten, über 500 Digimon, Regeln aus tuipet + eigene Linien, Armor-Digitation | `game/data.py`, `data/digimon.json`, `static/rules.js` |
| Erkunden | 6 Gebiete, Expeditionen 30 Min / 2 Std / 8 Std, Eier & Items finden, Rückkehr mit OK bestätigen | `game/explore.py` |
| Kämpfe | gegen wilde Digimon (Laden, Ausweichen, Spezialattacke) und live gegen Freunde | `game/battle.py`, `game/duel.py` |
| Sammlung | „Digimon-PC“: 8 Boxen × 20 Plätze, Zeit steht still, bis zu 3 Digimon erkunden von dort | `game/collection.py` |
| Freunde | eigener Freundescode pro Konto; Kampf, Tausch, Jogress nur mit Freunden | `game/friends.py`, `game/social.py` |
| Shop | Items für Bits, Daily Steal (täglich ein Item −40 %), Verkaufen im Rucksack, V-Pet-Designs, Deko | `game/shop.py`, `game/themes.py`, `game/decor.py` |
| Events | z. B. Halloween (25.10.–2.11.): Geister, Event-Ei, Gruselbonbons, Event-Tab mit Story | `game/events.py` |
| Fortschritt | Erfolge, Digidex, Rangliste, Merkliste mit Ziel pro Digimon | `game/progress.py`, `game/wishlist.py` |
| Start | Fragenkatalog fürs erste Ei | `game/starter.py` |
| Admin | Spieler, Spielregeln, Shop-Preise & Daily Steal, Zugang, Backups, Protokoll; Cheat-Menü | `game/admin.py`, `game/settings.py`, `game/cheats.py`, `static/admin.*` |

---

## Lokal starten

Voraussetzung: **Python 3.10 oder neuer** (Windows: bei der Installation „Add Python to PATH“).
Sonst nichts – keine `pip install`.

| Wie | Was passiert |
|---|---|
| Doppelklick **`start.bat`** (oder `python server.py`) | Spiel auf http://localhost:8000, Spielstand `savegame.db`, Browser öffnet sich |
| Doppelklick **`start-schnelltest.bat`** | Zeit läuft 60× schneller, eigener Spielstand `testgame.db`, Port 8001 |

Das **erste Konto** auf einem neuen Spielstand braucht keinen Einladungscode und wird Admin.
Lokal zwei Spieler testen: zweites Konto in einem privaten Browserfenster anlegen.

### Umgebungsvariablen

| Variable | Standard | Wofür |
|---|---|---|
| `VPET_PORT` | `8000` | Port |
| `VPET_HOST` | `127.0.0.1` | `0.0.0.0` = auch andere Geräte im Netz |
| `VPET_DB` | `savegame.db` | Spielstand-Datei (relativ zum Projektordner oder absolut) |
| `VPET_SPEED` | `1` | Zeitraffer zum Testen (60 = 1 Sekunde ist 1 Spielminute) |
| `VPET_TZ` | `Europe/Berlin` | Zeitzone für Tag/Nacht, Events, Daily Steal |
| `VPET_NO_BROWSER` | aus | Browser beim Start nicht öffnen |
| `VPET_PUBLIC` | aus | beim Hosten: erstes Konto wird *nicht* automatisch Admin |
| `VPET_SECURE` | aus | hinter HTTPS: Login-Cookie nur über HTTPS |
| `VPET_TRUST_PROXY` | aus | hinter Reverse-Proxy: echte IP aus `X-Forwarded-For` (Login-Sperre) |

Beispiel (PowerShell) für einen Testserver mit eigenem Spielstand ohne Browser:

```powershell
$env:VPET_PORT='8091'; $env:VPET_NO_BROWSER='1'; $env:VPET_DB='C:\Temp\test.db'; python server.py
```

### Tests

```bash
python -m unittest discover -s tests
```

Alle Tests müssen grün sein (Stand: über 230). `tests/test_i18n_complete.py` prüft dabei auch,
dass jeder Text im Code eine englische Fassung hat.

---

## Projektaufbau

```
server.py                 Webserver: alle /api/...-Endpunkte, Spielstand pro Anfrage, Sprache, Login
game/                     Spiel-Logik (reines Python, ohne Server-Abhängigkeiten → gut testbar)
  pet.py                  Pflege-Simulation: advance() rechnet die Zeit nach, Schlaf, Rufe, Digitation
  data.py                 lädt data/digimon.json (Digimon, Linien, Entwicklungsregeln)
  explore.py              Gebiete, Expeditionen, Items (ITEMS), Item benutzen
  battle.py / duel.py     Kampf gegen wilde Digimon / live gegen Freunde
  collection.py           Sammlung (Boxen), Erkunden aus der Sammlung, Rangliste
  social.py               Tausch und Jogress
  friends.py              Freundescodes und Freundeslisten
  shop.py                 Bits, Preise, Admin-Preise, Daily Steal, Kaufen/Verkaufen
  themes.py / decor.py    V-Pet-Designs (Farben fürs ganze Spiel) / Display-Deko
  events.py               zeitlich begrenzte Events (Story, Belohnungen, Geister, Event-Ei)
  progress.py             Erfolge, Statistiken, Digidex-Fortschritt
  wishlist.py             Merkliste und Ziel pro Digimon
  starter.py              Fragenkatalog fürs erste Ei
  accounts.py             Konten (PBKDF2), Sitzungen, Einladungscode, Login-Sperre
  admin.py / settings.py  Admin-Aktionen / Server-Regeln (meta "settings")
  cheats.py               Cheat-Menü (nur Admin)
  backup.py               automatische und manuelle Backups
  store.py                SQLite: Tabellen users, sessions, pets, meta, duels, requests, activity
  i18n.py / i18n_en.py    zweisprachige Texte: T("…") + englischer Katalog EN
static/                   Browser (wird 1:1 ausgeliefert)
  index.html, game.js     das Spiel (LCD-Canvas, Tasten, Fenster für Shop, Sammlung, Event …)
  style.css               alle Styles (Farben als CSS-Variablen, Designs überschreiben sie)
  rules.js                Entwicklungsregeln erklären / Wege finden (Spiel + Hilfe)
  hilfe.html, hilfe.js    Anleitung (deutsch + <template id="anleitung-en">), Digimon-Finder, Digidex
  admin.html, admin.js    Admin-Bereich (nur deutsch)
  i18n.js, i18n/en-*.js   tr("…") und die englischen Texte fürs Spiel / rules.js / Hilfe
  changelog.json          „Was ist neu?“ – neuester Eintrag = Versionsnummer des Spiels
  digidex.json, digidex_en.json   Digidex-Texte (von tools/build_digidex.py gebaut)
  sounds/, icons/, sw.js, manifest.webmanifest   Töne, App-Symbole, PWA
data/                     Quelldaten (digimon.json mit Sprites und Regeln, Digidex-Rohdaten)
tools/                    Hilfsskripte (Daten bauen, Admin-Konto, Icons, Sounds)
tests/                    unittest-Tests, eine Datei pro Bereich
Dockerfile, docker-compose.yml, deploy.bat   Hosting
start.bat, start-schnelltest.bat              lokal starten
```

---

## Wie es technisch funktioniert

**Zeit:** Das Spiel rechnet in *Spielminuten* (`clock.now()`, mit `VPET_SPEED` beschleunigt).
Ein Digimon wird nicht laufend simuliert, sondern bei jeder Anfrage mit `pet.advance(pet, now)`
bis jetzt nachgerechnet. Pausierte Zustände (Sammlung `in_box`, Kühlschrank `frozen`, Rückkehr
vom Erkunden noch nicht bestätigt `returned`) schieben ihre Zeitstempel einfach weiter.

**Spielstand:** SQLite (`game/store.py`). Digimon liegen als JSON in `pets`, alles Kontobezogene
als Schlüssel in `meta`, z. B.:

| meta-Schlüssel | Inhalt |
|---|---|
| `bits:<id>`, `inventory:<id>` | Bits, Rucksack `{Item: Anzahl}` |
| `themes:<id>`, `theme:<id>` | gekaufte / aktive Designs |
| `decor:<id>`, `decor_on:<id>` | gekaufte Deko / an-aus |
| `friends:<id>`, `friendcode:<id>`, `friendcode_owner:<CODE>` | Freunde und Freundescodes |
| `wishlist:<id>`, `stats:<id>`, `ach:<id>`, `dex:<id>`, `lang:<id>`, `boxnames:<id>` | Merkliste, Statistik, Erfolge, Digidex, Sprache, Boxnamen |
| `settings`, `prices`, `daily_steal`, `event_force` | Server-Regeln, Admin-Preise, festgelegter Daily Steal, erzwungenes Event (Cheat) |

**Ablauf einer Aktion:** Browser `POST /api/...` → `server.py` lädt Konto + Digimon, ruft eine
Funktion in `game/` auf → Antwort enthält `message` und den kompletten neuen Zustand
(`current_state(user)`) → `game.js` zeichnet neu (`apply(res)`). Fehler aus der Spiel-Logik
sind Exceptions mit Meldung für den Spieler (`pet.Refused`, `shop.ShopError` …).

**Zwei Sprachen:** Im Code steht alles auf Deutsch.
- Server: `T("{name} isst Fleisch.", name=…)` liefert einen deutschen String, der seine englische
  Fassung mitträgt; Englisch steht in `game/i18n_en.py` (Schlüssel = deutsche Vorlage *mit*
  Platzhaltern). Texte nie mit f-Strings zusammenbauen, sonst geht das Englische verloren.
- Browser: `tr("…{n}…", { n })`, Englisch in `static/i18n/en-game.js` (bzw. `en-rules.js`, `en-help.js`).
  Feste HTML-Texte werden über denselben Katalog übersetzt; Absätze mit `<b>` u. ä. bekommen
  `data-i18n` (dann ist das ganze innerHTML der Schlüssel).
- Hilfe: die englische Anleitung ist ein eigener Block `<template id="anleitung-en">` in `hilfe.html`.
- Admin-Bereich und Cheat-Menü bleiben nur deutsch.

**Update-Hinweis:** `VERSION` ist ein Fingerabdruck aller Spieldateien; ändert er sich, bietet der
Browser „Neu laden“ an. Die Versionsnummer für Menschen kommt aus dem neuesten Eintrag in
`static/changelog.json`.

---

## Regeln für Änderungen

Diese Regeln gelten für jede Änderung – auch für Agenten.

1. **Lokal bauen und testen, nicht live.** Erst wenn der Projekt-Besitzer ausdrücklich
   „pushen“/„deployen“ sagt, wird `deploy.bat` ausgeführt. Nie auf eigene Faust deployen,
   nie direkt auf dem Server Dateien ändern oder den Live-Spielstand lesen/ändern.
2. **Tests:** `python -m unittest discover -s tests` muss komplett grün sein. Für neue Logik
   einen Test in die passende `tests/test_*.py` schreiben. Tests, die Modul-Zustand ändern
   (z. B. `shop.OVERRIDES`), setzen ihn im `tearDown` zurück.
3. **Immer zweisprachig:** jeder neue Spielertext als `T("…")` bzw. `tr("…")` **plus** englischer
   Eintrag. `tests/test_i18n_complete.py` schlägt sonst fehl.
4. **Wirklich ausprobieren:** UI-Änderungen auf einem lokalen Testserver mit eigenem Spielstand
   ansehen (nie mit `savegame.db` herumspielen – vorher kopieren). JavaScript zusätzlich mit
   `node --check static/game.js` prüfen, falls Node vorhanden ist (ein Syntaxfehler legt das ganze
   Spiel lahm).
5. **Hilfe aktuell halten:** Ändert sich etwas, das Spieler wissen müssen, in `static/hilfe.html`
   **beide** Fassungen anpassen (deutsch und `<template id="anleitung-en">`). Stil: kurze Sätze,
   „Kurz gesagt“-Kasten pro Kapitel, nummerierte Schritte.
6. **Changelog:** für jedes Update einen Eintrag **oben** in `static/changelog.json`:
   ```json
   { "id": "2026-10-25-kurzname", "version": "3.4", "date": "2026-10-25",
     "title": "…", "items": ["…"], "title_en": "…", "items_en": ["…"] }
   ```
   - `items` und `items_en` gleich lang, aus Spielersicht geschrieben.
   - **Keine Admin- oder Cheat-Funktionen** in den Changelog – der ist nur für Spieler.
   - **Versionsnummer:** neues Feature `X.Y` (3.3 → 3.4), kleine Korrektur `X.Y.Z` (3.4 → 3.4.1),
     sehr großes Update neue Hauptversion (3.x → 4.0).
7. **Keine Zusatzpakete:** Server nur mit der Python-Standardbibliothek (im Docker-Image kommt
   allein `tzdata` dazu), Browser ohne Frameworks und ohne Build-Schritt.
8. **Stil:** Code-Kommentare und Docstrings auf Deutsch, kurz, im Stil der umliegenden Datei.
   Eigenes, flächiges „Digital World“-Design (Navy/Cyan/Orange, Chakra Petch + Silkscreen) –
   keine generischen Standard-Oberflächen. Farben immer über die CSS-Variablen (`--cyan`,
   `--orange`, `--panel` …), damit die V-Pet-Designs sie umfärben können.
9. **Datenschutz zwischen Spielern:** Andere Spieler sehen nur Freunde, und auch von denen nur
   Name, online-Status und Digimon – keine Gründe, Zeiten oder Details (z. B. wann ein Digimon vom
   Erkunden zurückkommt).

---

## Häufige Aufgaben

**Neues Item:** in `game/explore.py` → `ITEMS` (Name/Beschreibung mit `T`), Wirkung in
`explore.use_item`, Fundchance in `ITEM_ODDS`, Preis (falls im Shop) in `shop.PRICES`, Symbol in
`static/game.js` → `ITEM_ICON`/`ICONS`, englische Texte, Hilfe-Tabelle.

**Preise:** Standardpreise stehen im Code (`shop.PRICES`, `shop.EVENT_PRICES`, `themes.THEMES`,
`decor.DECOR`). Der Admin kann sie im Admin-Bereich → *Shop & Preise* überschreiben (gespeichert
in `meta "prices"`); im Code deshalb immer `shop.price_of(item)`, `themes.cost(key)`,
`decor.cost(key)` benutzen, nie die Tabellen direkt. Der Daily Steal ist immer
`shop.STEAL_DISCOUNT` (40 %) günstiger.

**Neues Event:** Eintrag in `game/events.py` → `EVENTS` mit `name`, `text`, `story` (2–3 Absätze),
`icon`, `start`/`end` (Monat, Tag), `ghosts`, `eggs`, `item`. Event-Preise in `shop.EVENT_PRICES`,
Tausch in `shop.CANDY_OFFERS`, Event-Design/-Deko mit `"event": "<key>"`. Englische Texte nicht
vergessen. Testen per Cheat-Menü → Event erzwingen.

**Neues V-Pet-Design:** `game/themes.py` → `THEMES` (Gehäuse, LCD, Pixel) **und** `UI`
(Farben fürs ganze Spiel).

**Digimon-Daten neu bauen:**
- `python tools/build_data.py <pfad/zu/tuipet-….whl>` → `data/digimon.json` (+ Sounds). Eigene
  Linien und Armor-Eier stehen dort in `CUSTOM_LINES` / `ARMOR_EGGS`.
- `python tools/fetch_digidex.py` (Digi-API) → `data/digidex_api.json`, dann
  `python tools/build_digidex.py` → `static/digidex.json` und `static/digidex_en.json`.

**Admin-Konto anlegen / Passwort neu setzen / Sperre aufheben** (Server vorher beenden):
`python tools/admin_account.py <name>` (fragt das Passwort verdeckt ab).

---

## Online-Server & Deploy

Das Spiel läuft als Docker-Container `vpet` (siehe `Dockerfile`, `docker-compose.yml`) hinter
dem Nginx Proxy Manager. Spielstand und Backups liegen außerhalb des Containers in `state/` und
`backups/` neben der `docker-compose.yml`. Online sind `VPET_PUBLIC` und `VPET_TRUST_PROXY` an.

- **Update hochladen:** Ein eigenes Deploy-Skript (nicht im Repo) packt `server.py game static data tools`
  + Docker-Dateien + README, lädt sie per SSH hoch und baut den Container neu. **Der Spielstand bleibt
  erhalten.**
- **Nach dem Deploy prüfen:** `/changelog.json` auf dem Server zeigt oben die neue Version.
- **Logs:** `docker logs --tail 50 vpet`.

---

## Konten, Admin & Backups

- Neue Spieler brauchen den **Einladungscode** (Admin-Bereich → Zugang, oder Einstellungen →
  „Freunde einladen“). Registrierung kann auch offen oder geschlossen sein.
- Nach 8 falschen Passwörtern für ein Konto (oder 30 von einem Gerät) ist die Anmeldung
  15 Minuten gesperrt. Anmeldungen gelten 90 Tage.
- **Admin-Bereich** (`/admin.html`, nur Admins): Übersicht, Spieler verwalten, Spielregeln,
  Shop & Preise (inkl. Daily Steal), Zugang/Wartungsmodus/Nachricht an alle, Backups, Protokoll.
- **Cheat-Menü** (Admin, im Spiel mit Shift+C): Zeit vorspulen, Werte setzen, verwandeln, Items
  geben, Event erzwingen … Gecheatete Digimon werden markiert.
- **Backups:** automatisch beim Start und alle 6 Stunden in `backups/` (pro Spielstand mit
  Präfix). Einspielen am einfachsten im Admin-Bereich → Backups; vorher wird automatisch der
  aktuelle Stand gesichert, danach müssen sich alle neu anmelden.

---

## Auf GitHub hochladen

- Die `.gitignore` hält Spielstände (`*.db`), `state/` und `backups/` heraus – die enthalten
  Konten mit Passwort-Hashes und dürfen **nie** ins Repository.
- `deploy.bat` enthält die Server-Adresse. Das Repository deshalb **privat** anlegen (oder die
  Adresse vorher herausnehmen).
- Digimon-Figuren und -Namen gehören Bandai/Toei; das Projekt ist ein privates Fan-Projekt –
  auch deshalb besser ein privates Repository.

---

## Credits

Pixel-Sprites, Soundeffekte und Entwicklungslinien aus [tuipet](https://pypi.org/project/tuipet/)
(MIT-Lizenz, Joel Taylor). Digidex-Beschreibungen, Typen, Attacken und Artworks:
[Digi-API](https://digi-api.com) (Beschreibungen ins Deutsche übersetzt).
Digimon und alle Figuren © Bandai / Toei Animation. Privates Fan-Projekt, nicht für die
öffentliche oder kommerzielle Verbreitung.
