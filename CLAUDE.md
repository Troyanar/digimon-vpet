# Hinweise für Agenten

Die vollständige Arbeitsanleitung steht in **AGENTS.md** (Ablauf, Prüfen, Hilfe, Changelog,
„push“, Fallstricke, Entscheidungen des Besitzers) – vor jeder Aufgabe lesen. Technische
Projekt-Doku: **README.md** (englisch). Das Wichtigste in Kürze:

- Der Projekt-Besitzer spricht Deutsch und programmiert nicht selbst: Antworten auf Deutsch,
  einfach erklärt, ohne Fachjargon.
- Lokal bauen und testen; **hochladen nur, wenn ausdrücklich „push“/„pushen“ gesagt wird** –
  dann Ablauf aus AGENTS.md Abschnitt 6 (Tests → git commit/push → `deploy.bat nopause` →
  live prüfen). Nie den Live-Server oder Live-Spielstand direkt anfassen.
- `python -W ignore -m unittest discover -s tests` muss grün sein, `node --check static/game.js` auch.
- Jeder Spielertext zweisprachig: `T("…")` + `game/i18n_en.py`, `tr("…")` + `static/i18n/en-*.js`.
- Bei Änderungen für Spieler: Hilfe (`static/hilfe.html`, deutsch **und** englisch) und Changelog
  (`static/changelog.json`, neue Versionsnummer, keine Admin-/Cheat-Punkte) pflegen.
- Prüf-Werkzeuge: `tools/dev/` (Test-Spielstand, API-Aufrufe, Bildschirmfotos).
- Python-Standardbibliothek, Vanilla-JS, kein Build-Schritt. Vom Besitzer erlaubte Ausnahme:
  `pywebpush` mit seinen Abhängigkeiten für Web-Push (`game/push-requirements.txt`).
