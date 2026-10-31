# Digimon V-Pet

A Digimon virtual pet in the browser – like the original 1997 V-Pet, with accounts, battles against friends, trading, Jogress, events and a shop. German and English UI.

- **Tech:** Python standard library as the server (no packages), vanilla JavaScript in the browser (no build step), SQLite for save data, Docker for hosting.
- **Rules for players:** in the game under **?** (`static/hilfe.html`).

## Features
- Classic V-pet care: feeding, training, sleeping, cleaning, battles and digivolution with pixel sprites and sounds
- Accounts, friends, real-time duels, trading and gifts, Jogress
- Shop, decorations, themes, seasonal events, Digidex and wishlist
- Installable PWA, admin panel with backups

## Run locally
```
python server.py        # or start.bat – http://localhost:8000
python -m unittest      # tests
```
Docker: `docker compose up -d`. Save data lives in `state/`, backups in `backups/` (both ignored by git).

Detailed German documentation for the project (architecture, rules, admin, deployment): [README.de.md](README.de.md)

Digimon names and sprites © Akiyoshi Hongo, Toei Animation, Bandai. Fan project, not affiliated with Bandai Namco.
