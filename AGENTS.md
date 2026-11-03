# AGENTS.md – Arbeitsanleitung für KI-Agenten (Codex, Claude & Co.)

Diese Datei beschreibt **genau**, wie an diesem Projekt gearbeitet wird – so, wie es bisher
gemacht wurde (Versionen 1.0 bis 3.6.2). Wer sie befolgt, kann die bisherige Arbeitsweise fast
1 zu 1 übernehmen. Technische Details zum Code stehen in **README.md** (englisch) – vor allem
die Abschnitte *Project layout*, *How it works* und *Common tasks*. Bei Widersprüchen gilt diese
Datei.

---

## 0. Die 12 Regeln in Kürze

1. **Mit dem Besitzer Deutsch sprechen** – einfach, ohne Fachjargon, er programmiert nicht.
2. **Lokal bauen und testen.** Nie auf dem Live-Server arbeiten, nie den Live-Spielstand lesen
   oder ändern, nie per SSH auf den Server, außer über `deploy.bat`.
3. **Hochladen nur, wenn der Besitzer in seiner Nachricht „push“, „pushen“, „pushe“ o. Ä.
   schreibt** – dann ohne Rückfrage den Ablauf aus [Abschnitt 6](#6-push--genau-so-wird-hochgeladen).
   Sonst nie, auch nicht „nur kurz“.
4. **Alle Tests grün:** `python -W ignore -m unittest discover -s tests`.
5. **JavaScript prüfen:** `node --check static/game.js` (ein Syntaxfehler = weiße Seite).
6. **Jeder Text für Spieler zweisprachig** (Deutsch im Code + englischer Katalog).
7. **Wirklich ausprobieren:** Prüf-Server mit eigenem Test-Spielstand + API-Aufruf und/oder
   Bildschirmfoto (Werkzeuge in `tools/dev/`).
8. **Hilfe pflegen:** `static/hilfe.html`, deutscher Teil **und** englische Vorlage.
9. **Changelog pflegen:** neuer Eintrag oben in `static/changelog.json`, mit Versionsnummer,
   deutsch + englisch, **ohne Admin-/Cheat-Punkte**.
10. **Python-Standardbibliothek + Vanilla-JS**, kein npm, kein Build. Einzige vom Besitzer
    erlaubte Paket-Ausnahme: `pywebpush` mit seinen Abhängigkeiten für Web-Push
    (`python -m pip install -r game/push-requirements.txt`).
11. **Privatsphäre:** Spieler sehen nur Freunde – und von denen keine Zeiten, Gründe, Werte.
12. **Nicht zu viel fragen.** Bei klaren Wünschen einfach bauen; nur echte Entscheidungen fragen
    (dann mit 2–4 Möglichkeiten zur Auswahl). Getroffene Entscheidungen (Abschnitt 9) nicht
    neu aufrollen.

---

## 1. Projekt und Besitzer

- **Was:** Digimon-V-Pet im Browser für den Besitzer und seine Freunde (privat), läuft auf
  einem eigenen Server. Code auf GitHub (`origin` = `Troyanar/digimon-vpet`, Zweig `main`,
  **öffentlich**).
- **Live-Adresse und Server-Details** stehen nur in der lokalen, git-ignorierten
  `DEPLOY.local.md` – **nie** ins Repository schreiben (keine Domain, keine Server-IP, keine
  Server-Pfade wie `/opt/…`, keine persönlichen Windows-Pfade), auch nicht in Kommentare,
  README, AGENTS.md oder Commit-Nachrichten. Im Gespräch mit dem Besitzer darf die Adresse
  genannt werden.
- **Rechner:** Windows 11, Python 3.13, Node, Git, GitHub CLI (`gh`, eingeloggt als Troyanar),
  Microsoft Edge für Bildschirmfotos. Commits mit der Repo-Identität Troyanar.
- **Besitzer:** spricht Deutsch, ist kein Programmierer. Er testet selbst im Browser und meldet
  Fehler oft mit kurzen Sätzen oder weitergeleiteten Spieler-Meldungen (auch auf Englisch aus
  Discord). Er schickt manchmal mitten in der Arbeit eine zweite Nachricht, die die erste
  präzisiert („Aber nur bei Freunden“) – die gehört zur selben Aufgabe.
- **Sprache des Spiels:** Deutsch und Englisch. Admin-Bereich und Cheat-Menü nur Deutsch.

---

## 2. Arbeitsablauf für jede Aufgabe

So wurde bisher jede Aufgabe erledigt – in dieser Reihenfolge:

1. **Verstehen.** Den Wunsch kurz in eigenen Worten fassen. Ist er mehrdeutig *und* kostet ein
   Irrtum viel Arbeit, mit Auswahlmöglichkeiten nachfragen. Sonst sinnvoll entscheiden und das
   im Abschlussbericht sagen („Zwei Dinge habe ich selbst festgelegt: …“).
2. **Bei Fehlermeldungen zuerst nachstellen**, nicht raten: ein kleines Python-Skript (im
   Temp-/Scratch-Ordner, nicht im Projekt), das die Spiellogik aus `game/` direkt aufruft, oder
   ein API-Aufruf gegen den Prüf-Server (`tools/dev/api.py`). Ursache finden, dann beheben.
   Stellt sich heraus, dass der Code richtig ist und der Besitzer etwas missverstanden hat:
   das freundlich erklären (mit dem Beleg) und fragen, was er stattdessen möchte.
3. **Code lesen**, bevor man ändert: die betroffene Datei in `game/`, den Endpunkt in
   `server.py`, die Anzeige in `static/game.js`, `static/index.html`, `static/style.css`.
   Stil und Kommentardichte der Umgebung übernehmen (Kommentare/Docstrings deutsch, kurz).
4. **Bauen.**
   - Spiellogik in `game/*.py` (ohne Server-Abhängigkeit → gut testbar).
   - Endpunkt in `server.py` (`/api/...`), Antwort enthält `message` und `**current_state(user)`.
   - Anzeige in `static/game.js` (+ `index.html`, `style.css` mit CSS-Variablen `--cyan`,
     `--orange`, `--panel`, `--panel-2`, `--line`, `--muted` …, damit die V-Pet-Designs mitfärben).
   - **Texte zweisprachig** (siehe Abschnitt 8).
5. **Test schreiben** in der passenden `tests/test_*.py` (für neue Logik und für jeden
   behobenen Fehler einen Test, der genau den Fehlerfall prüft). Alte Tests, die bewusst
   geändertes Verhalten prüfen, anpassen – nicht löschen.
6. **Prüfen** (Abschnitt 3): Tests, `node --check`, Prüf-Server + API + Bildschirmfoto,
   auch auf Englisch.
7. **Hilfe** (Abschnitt 4) und **Changelog** (Abschnitt 5) ergänzen.
8. **Bericht an den Besitzer** (Abschnitt 7) – und auf „push“ warten.

Während längerer Arbeit alle paar Schritte **eine kurze Zwischenmeldung** auf Deutsch geben
(„Die Spiel-Logik steht, jetzt kommt die Anzeige.“).

---

## 3. Prüfen – Befehle

Alle Befehle im Projektordner. PowerShell-Varianten, weil der Rechner Windows ist.

### 3.1 Tests und Syntax

```powershell
python -W ignore -m unittest discover -s tests      # muss "OK" melden (Stand: 243 Tests)
node --check static/game.js                         # keine Ausgabe = gut
python -c "import json; json.load(open('static/changelog.json', encoding='utf-8')); print('json ok')"
```

`tests/test_i18n_complete.py` schlägt fehl, wenn ein `T("…")`/`tr("…")`-Text keine englische
Fassung hat – das ist Absicht.

### 3.2 Prüf-Server mit Test-Spielstand

Nie mit `savegame.db` herumspielen. Immer einen eigenen Test-Spielstand im Temp-Ordner:

```powershell
$t = "$env:TEMP\vpet-test"; New-Item -ItemType Directory -Force $t | Out-Null
python tools/dev/make_test_db.py "$t\check.db" --pet     # Konto "Tester" + Agumon, 2000 Bits
$env:VPET_PORT='8091'; $env:VPET_NO_BROWSER='1'; $env:VPET_DB="$t\check.db"; python server.py
```

Den Server **im Hintergrund** laufen lassen (sonst blockiert er). Danach wieder beenden:

```powershell
$p = (Get-NetTCPConnection -LocalPort 8091 -State Listen -ErrorAction SilentlyContinue).OwningProcess
if ($p) { Stop-Process -Id $p -Force }
```

Will der Besitzer selbst testen („starte mir den Testserver“): Server mit Browser starten
(`VPET_NO_BROWSER` weglassen) oder `start-schnelltest.bat` (Zeit 60× schneller, Port 8001).

Code geändert? **Server neu starten** – er lädt Python-Dateien nur beim Start.

### 3.3 API direkt aufrufen

```powershell
python tools/dev/api.py GET /api/state                    # als Tester, deutsch
python tools/dev/api.py GET /api/state --lang en          # englische Texte prüfen
python tools/dev/api.py POST /api/item '{\"item\": \"virus\"}'
```

In eigenen Skripten: `sys.path.insert(0, "tools/dev"); from api import call; call("/api/box")`.
Für einen bestimmten Zustand (Items im Rucksack, Digimon in der Sammlung …) vorher den
Test-Spielstand direkt mit `game.store.Store("…\\check.db")` vorbereiten, z. B.
`store.set_meta(f"inventory:{uid}", {"virus": 2})`. Hilfreich: `tests/test_battle.py → rookie()`
liefert ein fertiges Agumon.

**Achtung PowerShell:** `Invoke-RestMethod` schickt keinen `Cookie`-Header – deshalb immer
`tools/dev/api.py` (urllib) verwenden. **Achtung Git-Bash:** Pfade wie `/hilfe.html` werden zu
Windows-Pfaden umgebogen – `MSYS_NO_PATHCONV=1` davor setzen (api.py biegt `/api/…` selbst zurück).

### 3.4 Bildschirmfoto

```powershell
python tools/dev/screenshot.py "$env:TEMP\vpet-test\bild.png"
python tools/dev/screenshot.py "$env:TEMP\vpet-test\bild-en.png" --lang en --js "press('bag')"
python tools/dev/screenshot.py "$env:TEMP\vpet-test\freund.png" --js "openFriend('Tai')"
python tools/dev/screenshot.py "$env:TEMP\vpet-test\hilfe.png" --page /hilfe.html --size 1300,2000
```

`--js` läuft 3 s nach dem Laden (alle Fenster sind dann zu). Global aufrufbar in `game.js`:
`press(id)` (gleiche IDs wie die Tasten, z. B. `bag`, `bagitem:virus`, `item:shard_wald`,
`confirm-return`, `fight`), `openCollection()`, `openShop()`, `openSettings()`, `openEvent()`,
`openFriend(name)`. Mehrere Schritte: `"press('bag'); setTimeout(() => press('bagitem:virus'), 800)"`.

Das Bild danach **ansehen** (Datei öffnen) und prüfen: Text richtig? Englisch wirklich
englisch? Nichts abgeschnitten? Das LCD-Display bleibt headless oft leer – das ist normal.
Headless-Edge ist mindestens ~500 px breit; für Handy-Breite ggf. `--size 500,900`.

### 3.5 Englisch prüfen

Jede neue Meldung einmal mit `--lang en` abrufen (API oder Bildschirmfoto). Typischer Fehler:
ein Text kommt auf Englisch deutsch, weil er per f-String oder `str()` gebaut wurde (Abschnitt 8).

---

## 4. Hilfe pflegen (`static/hilfe.html`)

- Die Datei enthält die **deutsche Anleitung** und darunter die **englische** in
  `<template id="anleitung-en">`. Immer **beide** ändern, inhaltlich gleich.
- Stil: kurze Sätze, pro Kapitel ein Kasten `<p class="tldr"><b>Kurz gesagt</b>…</p>`
  (englisch `<b>In short</b>`), nummerierte Schritte `<ol class="steps">`, Tabellen für Zahlen.
- Preise im Shop-Kapitel stehen als Tabelle – neue Shop-Items dort einsortieren (nach Preis).
- Keine Aufzählung, welche Eier wo zu finden sind (Wunsch des Besitzers: Überraschung).
- Admin-Funktionen gehören nicht in die Spieler-Anleitung.

---

## 5. Changelog (`static/changelog.json`)

Der **oberste** Eintrag ist die Spielversion (wird im Spiel angezeigt, „Neu im Spiel“-Leiste,
Update-Hinweis). Pro Upload **ein** Eintrag ganz oben einfügen:

```json
{
  "id": "2026-10-29-scherben-virus",
  "version": "3.6",
  "date": "2026-10-29",
  "title": "Ei-Scherben & Virus-Diskette",
  "items": [
    "Beim Erkunden findest du jetzt Ei-Scherben statt ganzer Eier – …",
    "4 gleiche Scherben setzt du im Rucksack zu einem Digi-Ei … zusammen."
  ],
  "title_en": "Egg shards & Virus Disk",
  "items_en": [
    "Exploring now finds egg shards instead of whole eggs – …",
    "Put 4 of the same shards together in your backpack …"
  ]
}
```

- `id` = `Datum-kurzname` (eindeutig), `date` = heutiges Datum.
- `items` und `items_en` gleich lang, aus Sicht der Spieler geschrieben („du“), konkret
  (Zahlen, Knopf-Namen in „…“), bei Fehlerbehebungen kurz sagen, was vorher falsch war.
- **Keine Admin-, Cheat- oder Werkzeug-Punkte** (Admin-Preise, Cheat-Menü, tools/ …) – der
  Changelog ist nur für Spieler. Solche Sachen nur im Bericht an den Besitzer erwähnen.
- Reine Text-/Doku-Änderungen ohne Spielauswirkung (z. B. nur Hilfe-Text gekürzt, README)
  brauchen keinen Eintrag – das dann im Bericht sagen.
- **Versionsnummer** (vom letzten Eintrag aus weiterzählen):
  - kleiner Fehler / kleine Änderung → `X.Y.Z` (3.6 → 3.6.1 → 3.6.2)
  - neues Feature → `X.Y` (3.6.2 → 3.7)
  - sehr großes Feature → neue Hauptversion (3.x → 4.0)
  - Mehrere Änderungen vor einem „push“ → **ein** gemeinsamer Eintrag mit der höchsten
    passenden Stufe (nicht drei Mini-Einträge übereinander). Wurde ein Eintrag noch nicht
    hochgeladen und es kommt etwas dazu: denselben Eintrag erweitern.
- Danach JSON prüfen (Befehl in 3.1).

Stand beim Schreiben dieser Datei: **3.6.2** (live).

---

## 6. „push“ – genau so wird hochgeladen

Nur wenn der Besitzer es in seiner Nachricht verlangt („push“, „pushen“, „puuush“ …). Dann
ohne weitere Rückfrage:

1. **Vorher prüfen** (muss alles grün sein, sonst NICHT hochladen und Bescheid sagen):
   ```powershell
   python -W ignore -m unittest discover -s tests
   node --check static/game.js
   python -c "import json; json.load(open('static/changelog.json', encoding='utf-8')); print('json ok')"
   ```
   Kein Prüf-Server darf mehr laufen, der Changelog-Eintrag muss da sein (falls es eine
   Spieler-Änderung ist).
2. **Auf GitHub sichern** (Zweig `main`, das Repository ist **öffentlich**):
   ```powershell
   git status --short          # ansehen: keine .db-Dateien, keine Temp-Dateien, kein deploy.bat
   git add -A
   git diff --cached --name-only                       # was geht mit?
   python tools/dev/scan_staged.py                     # muss "ok – … nichts Verdächtiges" melden
   ```
   `scan_staged.py` sucht Server-Adressen (liest sie aus den lokalen Dateien
   `DEPLOY.local.md`/`deploy.bat`), persönliche Pfade, Schlüssel und verbotene Dateien.
   Findet es etwas: Stelle entfernen (Adresse gehört nach `DEPLOY.local.md`), erneut
   `git add -A`, wieder prüfen. Dann:
   ```powershell
   git commit -m "3.6.2: Hourglass in the collection only while exploring"
   git push origin main
   ```
   Commit-Nachricht kurz auf Englisch, mit Versionsnummer vorne. `.gitignore` hält
   Spielstände (`*.db`), `state/`, `backups/`, `deploy.bat` und `DEPLOY.local.md` heraus –
   diese Dateien **nie** einchecken (Passwort-Hashes, Server-Adresse). Nie `git push --force`
   (wird ohnehin blockiert; falls je nötig, dem Besitzer den Befehl zum Selbst-Ausführen geben).
3. **Auf den Server laden** (im Projektordner):
   ```powershell
   cmd /c "deploy.bat nopause"
   ```
   Das Skript (nur lokal vorhanden, nicht im Repo) packt `server.py game static data tools`
   + Docker-Dateien, lädt per SSH hoch und baut den Container neu. **Der Spielstand bleibt.**
   Am Ende muss „Fertig! Das Spiel laeuft mit dem neuen Stand.“ stehen. Dauert ca. 1 Minute,
   Zeitlimit großzügig setzen (10 Minuten).
   Fehlt `deploy.bat` (z. B. in einer Cloud-Umgebung): **nicht** selbst per SSH deployen,
   sondern dem Besitzer sagen, dass er `deploy.bat` auf seinem PC doppelklicken soll.
4. **Live prüfen** (liest die Adresse aus `DEPLOY.local.md`):
   ```powershell
   python tools/dev/check_live.py                      # changelog.json: 200 <Version> - <Titel>, Startseite: 200
   python tools/dev/check_live.py "neuer Hilfe-Text"   # bei Hilfe-Änderungen: "Text in hilfe.html: True"
   ```
   Kommt eine alte Version: eine halbe Minute warten und noch einmal prüfen (der Container
   startet neu). Bleibt sie alt, dem Besitzer die Ausgabe von `deploy.bat` zeigen.
5. **Kurz melden** (Deutsch): „Version X ist online auf <Live-Adresse>. Die Seite lädt, der
   Changelog zeigt „…“.“ + ein Satz, was sich für Spieler ändert.

Nie: per SSH auf den Server, um Logs/Spielstand anzusehen oder Dateien zu ändern;
`docker`-Befehle auf dem Server; `git push --force`.

---

## 7. Bericht an den Besitzer

Am Ende jeder Aufgabe, auf Deutsch, kurz und ohne Code:

- erster Satz: was gebaut/behoben wurde und **ob es schon online ist** („als Version 3.6.2,
  noch nicht online“);
- bei Fehlern: in 1–2 Sätzen, was die Ursache war;
- **So funktioniert es jetzt:** kurze Liste aus Spielersicht (Knopf-Namen fett/in „…“);
- **Geprüft:** Tests (Anzahl), im Browser/API angeschaut, Hilfe + Changelog ergänzt;
- selbst getroffene Entscheidungen nennen und anbieten, sie zu ändern (z. B. Preise, Chancen);
- zum Schluss: „Sag „push“, dann geht es online.“

Keine langen Erklärungen von Code, keine Dateinamen-Listen, keine englischen Fachwörter, wenn
es ein einfaches deutsches Wort gibt.

---

## 8. Technische Fallstricke (aus der bisherigen Arbeit gelernt)

**Zweisprachige Texte (Server, `game/i18n.py`):**
- Spielertexte immer als `T("Deutsche Vorlage {name}", name=…)`; englische Fassung in
  `game/i18n_en.py` mit **genau** der deutschen Vorlage (inkl. Platzhalter) als Schlüssel.
  Lange Vorlagen dürfen über mehrere Zeilen als aneinandergehängte Strings stehen – der
  Schlüssel in `i18n_en.py` muss zusammengesetzt identisch sein.
- `Text + Text` und `Text + "str"` behalten Englisch; **f-Strings, `"…".join()`, `str(text)`,
  `.format()` verlieren es** → `T(…)`, `+` oder `i18n.join()` benutzen.
- Gespeicherte Texte (Tagebuch `pet["log"]`, Berichte) speichern `text` **und** `en`
  (`P._log` macht das automatisch, sonst `{"text": str(t), "en": en_of(t)}`), beim Ausgeben
  `stored(text, en)`.
- Fehlermeldungen: `raise P.Refused(T("…"))`, im Server `i18n.text_of(e)` (nicht `str(e)`).
- Die Sprache wählt `send_json` per Cookie `vpet_lang`, ohne Cookie die Konto-Sprache.

**Zweisprachige Texte (Browser):**
- `tr("Deutsch {n}", { n })` + Eintrag in `static/i18n/en-game.js` (Hilfe: `en-help.js`,
  Regeln: `en-rules.js`).
- Feste Texte in `index.html` werden über denselben Katalog übersetzt (exakter Text als
  Schlüssel). Absätze mit `<b>`/`<kbd>` bekommen `data-i18n`, Schlüssel = ganzes innerHTML.

**Spiel-Logik:**
- Zeit = Spielminuten (`clock.now()`); `pet.advance(pet, now)` holt verpasste Zeit nach.
  In der Sammlung (`in_box`), im Kühlschrank (`frozen`) und bei unbestätigter Rückkehr vom
  Erkunden (`returned`) steht die Zeit still (`shift_times`).
- Ein wildes Digimon vom Erkunden (`pet["scout"]`) darf erst nach dem OK (`returned` weg)
  bekämpft werden.
- Preise immer über `shop.price_of(item)`, `themes.cost(k)`, `decor.cost(k)` – der Admin kann
  sie überschreiben (`shop.OVERRIDES`). Tests, die Modul-Zustand ändern, setzen ihn in
  `tearDown` zurück.
- Eier heißen überall nur „Digi-Ei“ (`data.egg_name(line)`, Browser `eggLabel(line)`), nur
  Event-Eier (z. B. Halloween) nennen ihre Sorte.
- Neues Item: `explore.ITEMS` (+ ggf. `ITEM_ODDS`, `use_item`), Preis in `shop.PRICES`,
  Symbol in `game.js` → `ICONS`/`ITEM_ICON`, EN-Texte, Hilfe (Rucksack-Liste + Shop-Tabelle).
- Freunde: alles Soziale über `friends.check`/`friends.are_friends`. Freunden nie
  Rückkehrzeiten, Gründe („warum kann er nicht kämpfen“) oder Werte zeigen.

**Browser:**
- Nach jeder JS-Änderung `node --check static/game.js` – ein doppeltes `const` hat schon
  einmal das ganze Spiel weiß gemacht.
- Anzeige-Modi der Tasten: `S.mode` + `keysFor(mode)` + `press(id)` in `game.js`.
- Meldungen aus Fenstern (Sammlung, Shop) landen in der Meldungszeile unter dem **aktiven**
  Digimon – deshalb in Meldungen über andere Digimon immer deren Namen nennen.

**Werkzeuge:**
- Python-Server lädt Code nur beim Start → nach Änderungen neu starten.
- PowerShell 5.1: kein `&&` (statt dessen `;` bzw. `if ($?) { … }`).

---

## 9. Entscheidungen des Besitzers (nicht neu fragen)

- Browser-Spiel/PWA, keine .exe. Echtzeit wie das Original-V-Pet; Digimon können sterben.
- Neue Digimon nur über Eier. Erkunden bringt **Ei-Scherben** (eine Sorte pro Gebiet,
  10 % pro Fundchance), **4 gleiche = 1 Ei** aus diesem Gebiet. Event-Eier bleiben ganze Eier.
- Was aus einem Ei wird, ist eine Überraschung (keine Ei-Listen in der Hilfe, Eier heißen
  „Digi-Ei“).
- Digimon-Namen wie in der deutschen Serie (Growlmon, Wizardmon, Daemon …).
- Armor-Eier kann man nicht kaufen; Armor-Formen sind eine eigene Endstufe.
- Kämpfe: höchstens 25 Runden, Gleichstand = Unentschieden.
- Sanduhr: aktives Digimon jederzeit; Sammlungs-Digimon **nur während es erkundet**, sonst
  Meldung „Das geht nicht …“.
- Virus-Diskette: +1 Pflegefehler, nie über 19 (bei 20 stirbt das Digimon), 80 Bits.
- Verkaufen im Rucksack: alles, beliebig viele; Shop-Items zum halben Preis.
- Daily Steal: jeden Tag ein Item 40 % günstiger.
- Freunde per Freundescode (beidseitig); Kämpfen/Tauschen/Jogress und Profil ansehen nur mit
  Freunden.
- Jogress solo: zwei eigene Digimon werden eines. Vorher Grundlage wählen (Spitzname, Alter,
  Geschichte bleiben), Vorschau bestätigen; der andere Partner wird verbraucht, Digidex bleibt.
  Mit Freunden werden beide zur gleichen Fusion, jeder behält sein eigenes Digimon.
  Werte wie bei normaler Digitation, nicht addieren. Beide müssen ausdrücklich zustimmen.
- Changelog nur Spieler-Sachen; jede hochgeladene Änderung bekommt eine Versionsnummer.
- Eigenes Design (Navy/Cyan/Orange, Chakra Petch + Silkscreen), keine Standard-/„KI-Look“-UIs.

Mehr Geschichte: `static/changelog.json` (alle Versionen mit Begründung aus Spielersicht) und
`git log`.

---

## 10. Wo was steht (Kurzfassung)

| Thema | Dateien |
|---|---|
| Pflege, Zeit, Digitation, Tagebuch | `game/pet.py`, `game/data.py`, `static/rules.js` |
| Erkunden, Items, Scherben, Rucksack | `game/explore.py`, `game/collection.py` (`combine_shards`) |
| Kämpfe wild / gegen Freunde | `game/battle.py`, `game/duel.py` |
| Sammlung (Digimon-PC), Sammlungs-Ausflüge | `game/collection.py` |
| Freunde, Freundesprofil, Tausch, Jogress | `game/friends.py`, `game/social.py` |
| Shop, Preise, Daily Steal, Verkaufen | `game/shop.py`, `game/themes.py`, `game/decor.py` |
| Events (Halloween) | `game/events.py` |
| Erfolge, Digidex-Stand, Merkliste | `game/progress.py`, `game/wishlist.py` |
| Server, alle Endpunkte, Sprache | `server.py` |
| Texte EN | `game/i18n_en.py`, `static/i18n/en-game.js`, `en-help.js`, `en-rules.js` |
| Spiel-Oberfläche | `static/index.html`, `static/game.js`, `static/style.css` |
| Hilfe + Finder + Digidex | `static/hilfe.html`, `static/hilfe.js` |
| Admin-Bereich (nur deutsch) | `static/admin.html`, `static/admin.js`, `game/admin.py` |
| Prüf-Werkzeuge | `tools/dev/` (make_test_db, api, screenshot, proxy, check_live, scan_staged) |
| Server-Adresse, Deploy-Notizen (lokal, nicht im Repo) | `DEPLOY.local.md`, `deploy.bat` |
