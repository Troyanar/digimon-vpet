# Hinweise für Agenten

Alles Wichtige steht in **README.md** (Projekt-Doku, englisch) – vor jeder Änderung den Abschnitt
„Rules for changes“ lesen. Das Wichtigste in Kürze:

- Der Projekt-Besitzer spricht Deutsch und programmiert nicht selbst: Antworten auf Deutsch,
  einfach erklärt, ohne Fachjargon.
- Lokal bauen und testen; **deployen (`deploy.bat nopause`) nur, wenn ausdrücklich „pushen“ gesagt wird**.
  Nie den Live-Server oder Live-Spielstand direkt anfassen.
- `python -m unittest discover -s tests` muss grün sein.
- Jeder Spielertext zweisprachig: `T("…")` + `game/i18n_en.py`, `tr("…")` + `static/i18n/en-*.js`.
- Bei Änderungen für Spieler: Hilfe (`static/hilfe.html`, deutsch **und** englisch) und Changelog
  (`static/changelog.json`, neue Versionsnummer, keine Admin-/Cheat-Punkte) pflegen.
- Nur Python-Standardbibliothek, Vanilla-JS, kein Build-Schritt.
