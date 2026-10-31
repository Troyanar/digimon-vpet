# Digimon V-Pet

A Digimon virtual pet in the browser – like the original 1997 V-Pet, with accounts, battles
against friends, trading, Jogress, events and a shop. German and English UI.

- **Tech:** Python standard library as the server (no packages), vanilla JavaScript in the
  browser (no build step), SQLite for save data, Docker for hosting.
- **Rules for players:** in the game under **?** (`static/hilfe.html`) – this README
  explains the project, not the game in detail.

> **For agents (Claude & co.):** read the section [Rules for changes](#rules-for-changes)
> before every change. In short: build locally → all tests green → German **and** English →
> keep help + changelog up to date → **deploy only when explicitly told to**.

---

## Contents

1. [Features](#features)
2. [Run locally](#run-locally)
3. [Project layout](#project-layout)
4. [How it works](#how-it-works)
5. [Rules for changes](#rules-for-changes)
6. [Common tasks](#common-tasks)
7. [Online server & deploy](#online-server--deploy)
8. [Accounts, admin & backups](#accounts-admin--backups)
9. [Publishing on GitHub](#publishing-on-github)
10. [Credits](#credits)

---

## Features

| Area | Summary | Code |
|---|---|---|
| Care | Feeding, training (3 mini-games), cleaning, light/sleep, medicine, calls & care mistakes, death | `game/pet.py` |
| Digivolution | 30 egg types, over 500 Digimon, rules from tuipet + own lines, Armor digivolution | `game/data.py`, `data/digimon.json`, `static/rules.js` |
| Exploring | 6 areas, expeditions 30 min / 2 h / 8 h, find eggs & items, confirm the return with OK | `game/explore.py` |
| Battles | against wild Digimon (charge, dodge, special attack) and live against friends | `game/battle.py`, `game/duel.py` |
| Collection | "Digimon PC": 8 boxes × 20 slots, time stands still, up to 3 Digimon explore from there | `game/collection.py` |
| Friends | own friend code per account; battles, trading and Jogress only with friends | `game/friends.py`, `game/social.py` |
| Shop | items for Bits, Daily Steal (one item −40 % per day), selling from the backpack, V-Pet designs, decorations | `game/shop.py`, `game/themes.py`, `game/decor.py` |
| Events | e.g. Halloween (Oct 25 – Nov 2): ghosts, event egg, spooky candy, event tab with a story | `game/events.py` |
| Progress | achievements, Digidex, ranking, wishlist with a goal per Digimon | `game/progress.py`, `game/wishlist.py` |
| Start | questionnaire for the first egg | `game/starter.py` |
| Admin | players, game rules, shop prices & Daily Steal, access, backups, log; cheat menu | `game/admin.py`, `game/settings.py`, `game/cheats.py`, `static/admin.*` |

---

## Run locally

Requirement: **Python 3.10 or newer** (Windows: tick "Add Python to PATH" during installation).
Nothing else – no `pip install`.

| How | What happens |
|---|---|
| Double-click **`start.bat`** (or `python server.py`) | Game at http://localhost:8000, save file `savegame.db`, the browser opens |
| Double-click **`start-schnelltest.bat`** | Time runs 60× faster, separate save file `testgame.db`, port 8001 |

Save files are created on first start. The **first account** on a new save file needs no invite code and becomes admin.
To test two players locally, create the second account in a private browser window.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `VPET_PORT` | `8000` | Port |
| `VPET_HOST` | `127.0.0.1` | `0.0.0.0` = reachable from other devices on the network |
| `VPET_DB` | `savegame.db` | Save file (relative to the project folder or absolute) |
| `VPET_SPEED` | `1` | Time lapse for testing (60 = 1 second is 1 game minute) |
| `VPET_TZ` | `Europe/Berlin` | Time zone for day/night, events, Daily Steal |
| `VPET_NO_BROWSER` | off | Don't open the browser on start |
| `VPET_PUBLIC` | off | When hosting: the first account does *not* become admin automatically |
| `VPET_SECURE` | off | Behind HTTPS: login cookie only over HTTPS |
| `VPET_TRUST_PROXY` | off | Behind a reverse proxy: real IP from `X-Forwarded-For` (login lockout) |

Example (PowerShell) for a test server with its own save file and no browser:

```powershell
$env:VPET_PORT='8091'; $env:VPET_NO_BROWSER='1'; $env:VPET_DB='C:\Temp\test.db'; python server.py
```

### Tests

```bash
python -m unittest discover -s tests
```

All tests must pass (currently over 230). `tests/test_i18n_complete.py` also checks
that every text in the code has an English version.

---

## Project layout

```
server.py                 web server: all /api/... endpoints, game state per request, language, login
game/                     game logic (plain Python, no server dependencies → easy to test)
  pet.py                  care simulation: advance() catches up on elapsed time, sleep, calls, digivolution
  data.py                 loads data/digimon.json (Digimon, lines, digivolution rules)
  explore.py              areas, expeditions, items (ITEMS), using items
  battle.py / duel.py     battles against wild Digimon / live against friends
  collection.py           collection (boxes), exploring from the collection, ranking
  social.py               trading and Jogress
  friends.py              friend codes and friend lists
  shop.py                 Bits, prices, admin prices, Daily Steal, buying/selling
  themes.py / decor.py    V-Pet designs (colours for the whole game) / display decorations
  events.py               time-limited events (story, rewards, ghosts, event egg)
  progress.py             achievements, statistics, Digidex progress
  wishlist.py             wishlist and goal per Digimon
  starter.py              questionnaire for the first egg
  accounts.py             accounts (PBKDF2), sessions, invite code, login lockout
  admin.py / settings.py  admin actions / server rules (meta "settings")
  cheats.py               cheat menu (admin only)
  backup.py               automatic and manual backups
  store.py                SQLite: tables users, sessions, pets, meta, duels, requests, activity
  i18n.py / i18n_en.py    bilingual texts: T("…") + English catalogue EN
static/                   browser (served as is)
  index.html, game.js     the game (LCD canvas, buttons, windows for shop, collection, event …)
  style.css               all styles (colours as CSS variables, designs override them)
  rules.js                explains digivolution rules / finds paths (game + help)
  hilfe.html, hilfe.js    guide (German + <template id="anleitung-en">), Digimon finder, Digidex
  admin.html, admin.js    admin area (German only)
  i18n.js, i18n/en-*.js   tr("…") and the English texts for the game / rules.js / help
  changelog.json          "What's new?" – newest entry = the game's version number
  digidex.json, digidex_en.json   Digidex texts (built by tools/build_digidex.py)
  sounds/, icons/, sw.js, manifest.webmanifest   sounds, app icons, PWA
data/                     source data (digimon.json with sprites and rules, raw Digidex data)
tools/                    helper scripts (build data, admin account, icons, sounds)
tests/                    unittest tests, one file per area
Dockerfile, docker-compose.yml   hosting
start.bat, start-schnelltest.bat  run locally
```

---

## How it works

**Time:** the game counts in *game minutes* (`clock.now()`, sped up by `VPET_SPEED`).
A Digimon is not simulated continuously; on every request `pet.advance(pet, now)` catches it up
to the present. Paused states (collection `in_box`, fridge `frozen`, return from exploring
not yet confirmed `returned`) simply move their timestamps forward.

**Save data:** SQLite (`game/store.py`). Digimon are stored as JSON in `pets`, everything account-related
as keys in `meta`, e.g.:

| meta key | Content |
|---|---|
| `bits:<id>`, `inventory:<id>` | Bits, backpack `{item: count}` |
| `themes:<id>`, `theme:<id>` | bought / active designs |
| `decor:<id>`, `decor_on:<id>` | bought decorations / on-off |
| `friends:<id>`, `friendcode:<id>`, `friendcode_owner:<CODE>` | friends and friend codes |
| `wishlist:<id>`, `stats:<id>`, `ach:<id>`, `dex:<id>`, `lang:<id>`, `boxnames:<id>` | wishlist, statistics, achievements, Digidex, language, box names |
| `settings`, `prices`, `daily_steal`, `event_force` | server rules, admin prices, fixed Daily Steal, forced event (cheat) |

**Flow of an action:** browser `POST /api/...` → `server.py` loads account + Digimon and calls a
function in `game/` → the response contains `message` and the complete new state
(`current_state(user)`) → `game.js` redraws (`apply(res)`). Errors from the game logic
are exceptions with a message for the player (`pet.Refused`, `shop.ShopError` …).

**Two languages:** everything in the code is written in German.
- Server: `T("{name} isst Fleisch.", name=…)` returns a German string that carries its English
  version along; English lives in `game/i18n_en.py` (key = German template *with*
  placeholders). Never build texts with f-strings, or the English is lost.
- Browser: `tr("…{n}…", { n })`, English in `static/i18n/en-game.js` (or `en-rules.js`, `en-help.js`).
  Fixed HTML texts are translated through the same catalogue; paragraphs with `<b>` etc. get
  `data-i18n` (the whole innerHTML is then the key).
- Help: the English guide is a separate block `<template id="anleitung-en">` in `hilfe.html`.
- The admin area and cheat menu stay German only.

**Update notice:** `VERSION` is a fingerprint of all game files; when it changes, the
browser offers "Reload". The human-readable version number comes from the newest entry in
`static/changelog.json`.

---

## Rules for changes

These rules apply to every change – agents included.

1. **Build and test locally, not live.** Only when the project owner explicitly says
   "push"/"deploy" is the deploy script run. Never deploy on your own, never change files
   directly on the server or read/change the live save data.
2. **Tests:** `python -m unittest discover -s tests` must pass completely. Write a test for new logic
   in the matching `tests/test_*.py`. Tests that change module state
   (e.g. `shop.OVERRIDES`) reset it in `tearDown`.
3. **Always bilingual:** every new player-facing text as `T("…")` or `tr("…")` **plus** an English
   entry. Otherwise `tests/test_i18n_complete.py` fails.
4. **Actually try it:** look at UI changes on a local test server with its own save file
   (never play around with `savegame.db` – copy it first). Also check JavaScript with
   `node --check static/game.js` if Node is available (one syntax error breaks the whole
   game).
5. **Keep the help up to date:** if something changes that players need to know, update **both**
   versions in `static/hilfe.html` (German and `<template id="anleitung-en">`). Style: short sentences,
   a "Kurz gesagt" (in short) box per chapter, numbered steps.
6. **Changelog:** add an entry **at the top** of `static/changelog.json` for every update:
   ```json
   { "id": "2026-10-25-shortname", "version": "3.4", "date": "2026-10-25",
     "title": "…", "items": ["…"], "title_en": "…", "items_en": ["…"] }
   ```
   - `items` and `items_en` have the same length, written from the player's point of view.
   - **No admin or cheat features** in the changelog – it is for players only.
   - **Version number:** new feature `X.Y` (3.3 → 3.4), small fix `X.Y.Z` (3.4 → 3.4.1),
     very large update a new major version (3.x → 4.0).
7. **No extra packages:** server only with the Python standard library (the Docker image only adds
   `tzdata`), browser without frameworks and without a build step.
8. **Style:** code comments and docstrings in German, short, in the style of the surrounding file.
   Own flat "Digital World" design (navy/cyan/orange, Chakra Petch + Silkscreen) –
   no generic default UIs. Always use colours via the CSS variables (`--cyan`,
   `--orange`, `--panel` …) so the V-Pet designs can recolour them.
9. **Privacy between players:** other players only see friends, and of those only
   name, online status and Digimon – no reasons, times or details (e.g. when a Digimon returns
   from exploring).

---

## Common tasks

**New item:** in `game/explore.py` → `ITEMS` (name/description with `T`), effect in
`explore.use_item`, find chance in `ITEM_ODDS`, price (if sold in the shop) in `shop.PRICES`, icon in
`static/game.js` → `ITEM_ICON`/`ICONS`, English texts, help table.

**Prices:** default prices are in the code (`shop.PRICES`, `shop.EVENT_PRICES`, `themes.THEMES`,
`decor.DECOR`). The admin can override them in the admin area → *Shop & prices* (stored
in `meta "prices"`); so in code always use `shop.price_of(item)`, `themes.cost(key)`,
`decor.cost(key)`, never the tables directly. The Daily Steal is always
`shop.STEAL_DISCOUNT` (40 %) cheaper.

**New event:** entry in `game/events.py` → `EVENTS` with `name`, `text`, `story` (2–3 paragraphs),
`icon`, `start`/`end` (month, day), `ghosts`, `eggs`, `item`. Event prices in `shop.EVENT_PRICES`,
trades in `shop.CANDY_OFFERS`, event design/decoration with `"event": "<key>"`. Don't forget the
English texts. Test via cheat menu → force event.

**New V-Pet design:** `game/themes.py` → `THEMES` (shell, LCD, pixels) **and** `UI`
(colours for the whole game).

**Rebuilding the Digimon data:**
- `python tools/build_data.py <path/to/tuipet-….whl>` → `data/digimon.json` (+ sounds). Own
  lines and Armor eggs are defined there in `CUSTOM_LINES` / `ARMOR_EGGS`.
- `python tools/fetch_digidex.py` (Digi-API) → `data/digidex_api.json`, then
  `python tools/build_digidex.py` → `static/digidex.json` and `static/digidex_en.json`.

**Create an admin account / reset a password / lift a lockout** (stop the server first):
`python tools/admin_account.py <name>` (asks for the password without showing it).

---

## Online server & deploy

The game runs as the Docker container `vpet` (see `Dockerfile`, `docker-compose.yml`) behind
a reverse proxy (Nginx Proxy Manager, external network `npm_default`). Save data and backups live outside the container in `state/` and
`backups/` next to `docker-compose.yml`. Online, `VPET_PUBLIC` and `VPET_TRUST_PROXY` are on.

- **Uploading an update:** a separate deploy script (not in the repository) packs `server.py game static data tools`
  + Docker files + README, uploads them via SSH and rebuilds the container. **The save data is
  kept.**
- **Check after deploying:** `/changelog.json` on the server shows the new version at the top.
- **Logs:** `docker logs --tail 50 vpet`.

---

## Accounts, admin & backups

- New players need the **invite code** (admin area → Access, or Settings →
  "Invite friends"). Registration can also be open or closed.
- After 8 wrong passwords for an account (or 30 from one device), logging in is locked
  for 15 minutes. Logins last 90 days.
- **Admin area** (`/admin.html`, admins only): overview, manage players, game rules,
  shop & prices (including Daily Steal), access/maintenance mode/message to everyone, backups, log.
- **Cheat menu** (admin, in game with Shift+C): fast-forward time, set stats, transform, give items,
  force an event … Cheated Digimon are marked.
- **Backups:** automatically on start and every 6 hours in `backups/` (prefixed per save
  file). Easiest to restore in the admin area → Backups; the current state is backed up
  automatically first, and everyone has to log in again afterwards.

---

## Publishing on GitHub

- `.gitignore` keeps save files (`*.db`), `state/` and `backups/` out – they contain
  accounts with password hashes and must **never** go into the repository.
- The deploy script (`deploy.bat`) contains the server address and is ignored by git as well.

---

## Credits

Pixel sprites, sound effects and digivolution lines from [tuipet](https://pypi.org/project/tuipet/)
(MIT license, Joel Taylor). Digidex descriptions, types, attacks and artwork:
[Digi-API](https://digi-api.com) (descriptions translated into German).
Digimon and all characters © Akiyoshi Hongo, Bandai / Toei Animation. Private fan project, not affiliated with
Bandai Namco and not for commercial distribution.
