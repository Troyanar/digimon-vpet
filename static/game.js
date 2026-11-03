"use strict";

// ------------------------------------------------------------ Pixel-Grafiken
// 8x8-Symbole im LCD-Stil ("X" = Pixel an)
const ICONS = {
  food: ["...XXX..", "..XXXXX.", ".XXXXXXX", ".XXXXXXX", "..XXXXX.", "...XX...", "..X..X..", ".XX..XX."],
  train: ["........", "X......X", "XX....XX", "XXXXXXXX", "XX....XX", "X......X", "........", "........"],
  battle: [".......X", "......XX", ".....XX.", "X...XX..", ".X.XX...", "..XX....", ".X.X....", "X...X..."],
  clean: ["...X....", "...X....", "..XXX...", ".XXXXX..", "XXXXXXX.", "XXXXXXX.", ".XXXXX..", "..XXX..."],
  light: ["..XXX...", ".X...X..", "X.....X.", "X.....X.", ".X...X..", "..XXX...", "..XXX...", "...X...."],
  medicine: ["..XXX...", "..XXX...", "XXXXXXX.", "XXXXXXX.", "XXXXXXX.", "..XXX...", "..XXX...", "........"],
  call: ["...XX...", "...XX...", "...XX...", "...XX...", "...XX...", "........", "...XX...", "...XX..."],
  explore: ["XX......", "XX..XX..", "....XX..", "XX......", "XX..XX..", "....XX..", "XX......", "XX......"],
  bag: ["..XXXX..", ".X....X.", "XXXXXXXX", "X..XX..X", "X......X", "X......X", "XXXXXXXX", "........"],
  home: ["...XX...", "..XXXX..", ".XXXXXX.", "XXXXXXXX", ".X....X.", ".X.XX.X.", ".X.XX.X.", ".XXXXXX."],
  star: ["...X....", "...X....", "XXXXXXX.", ".XXXXX..", "..XXX...", ".XX.XX..", "XX...XX.", "........"],
  snow: ["...X....", ".X.X.X..", "..XXX...", "XXXXXXX.", "..XXX...", ".X.X.X..", "...X....", "........"],
  fridge: [".XXXXXX.", ".X..X.X.", ".X....X.", ".XXXXXX.", ".X..X.X.", ".X..X.X.", ".X....X.", ".XXXXXX."],
  totem: ["..XXXX..", ".XX..XX.", "..XXXX..", "XXXXXXXX", "X.XXXX.X", "..XXXX..", "..X..X..", "..XXXX.."],
  // Armor-Ei: Ei mit Wappen in der Mitte
  armor: ["...XX...", "..XXXX..", ".XX..XX.", ".X.XX.X.", "XX.XX.XX", "XXX..XXX", ".XXXXXX.", "..XXXX.."],
  news: ["XXXXXXX.", "X.....X.", "X.XXX.X.", "X.....X.", "X.XXX.X.", "X.....X.", "XXXXXXX.", "........"],
  trophy: ["XXXXXXX.", "XXXXXXX.", "XXXXXXX.", ".XXXXX..", "..XXX...", "...X....", "..XXX...", ".XXXXX.."],
  help: ["..XXXX..", ".XX..XX.", ".....XX.", "....XX..", "...XX...", "...XX...", "........", "...XX..."],
  gear: ["...XX...", ".X.XX.X.", "..XXXX..", "XXX..XXX", "XXX..XXX", "..XXXX..", ".X.XX.X.", "...XX..."],
  back: ["...X....", "..XX....", ".XXXXXXX", "XXXXXXXX", ".XXXXXXX", "..XX....", "...X....", "........"],
  // Kampf: Pfeile für oben / unten
  up: ["...XX...", "..XXXX..", ".XXXXXX.", "XXXXXXXX", "...XX...", "...XX...", "...XX...", "...XX..."],
  down: ["...XX...", "...XX...", "...XX...", "...XX...", "XXXXXXXX", ".XXXXXX.", "..XXXX..", "...XX..."],
  meat: ["...XXX..", "..XXXXX.", ".XXXXXXX", ".XXXXXXX", "..XXXXX.", "...XX...", "..X..X..", ".XX..XX."],
  protein: ["..XXXX..", "...XX...", "..XXXX..", ".X....X.", ".X.XX.X.", ".X.XX.X.", ".X....X.", "..XXXX.."],
  poop: ["....X...", "...XX...", "..XXXX..", "..X..X..", ".XXXXXX.", "X.X..X.X", "XXXXXXXX", "........"],
  skull: [".XXXXXX.", "XXXXXXXX", "X..XX..X", "X..XX..X", "XXXXXXXX", ".XX..XX.", "..XXXX..", "..X.X.X."],
  zz: ["XXXX....", "..X.....", ".X......", "XXXX....", "....XXX.", ".....X..", "....XXX.", "........"],
  // Shop: Münze (Bits), Ewigstein, Sanduhr, Löschdiskette
  coin: ["..XXXX..", ".X.XX.X.", "X.XXXX.X", "X.XX...X", "X..XXX.X", "X.XXXX.X", ".X.XX.X.", "..XXXX.."],
  stone: ["........", "..XXX...", ".XX.XX..", "XXXX.XX.", "XX.XXXX.", ".XXXXX..", "..XXX...", "........"],
  hourglass: ["XXXXXXX.", ".X...X..", "..XXX...", "...X....", "..X.X...", ".XXXXX..", "XXXXXXX.", "........"],
  disk: ["XXXXXXX.", "X.XXX.X.", "X.XXX.X.", "X.....X.", "X.XXX.X.", "X.X.X.X.", "XXXXXXX.", "........"],
  // Halloween: Kürbis (Event-Leiste), Gruselbonbon; Reset-Kristall
  pumpkin: ["....X...", "...X....", ".XXXXXX.", "XX.XX.XX", "XXXXXXXX", "X.X..X.X", "XX.XX.XX", ".XXXXXX."],
  candy: ["........", "X......X", "XX.XX.XX", "XXX..XXX", "XXX..XXX", "XX.XX.XX", "X......X", "........"],
  crystal: ["...XX...", "..X..X..", ".X.XX.X.", "X.XXXX.X", "X.XXXX.X", ".X.XX.X.", "..X..X..", "...XX..."],
  // Ei-Scherbe (ein Stück Eierschale mit Zacken) und Virus-Diskette (Diskette mit Virus-Fleck)
  shard: ["........", "...X....", "..XXX.X.", ".XXXXXX.", ".XX.XXX.", "XXXX.XX.", "XXXXXX..", ".XXXX..."],
  virus: ["XXXXXXX.", "X.XXX.X.", "X.XXX.X.", "X.....X.", "X.X.X.X.", "X..X..X.", "X.X.X.X.", "XXXXXXX."],
};
// Fledermaus, die während Halloween oben übers Display flattert (zwei Flügelschläge)
const BAT = [["X.......X", "XX.X.X.XX", "XXXXXXXXX", ".X.XXX.X.", "....X...."],
  [".........", "...X.X...", ".XXXXXXX.", "XX.XXX.XX", "X...X...X"]];
// welches Symbol zu welchem Item (Rucksack und Shop)
const ITEM_ICON = { snack: "meat", weight: "train", charm: "star", totem: "totem", everstone: "stone",
  hourglass1: "hourglass", hourglass3: "hourglass", hourglass6: "hourglass", erase: "disk",
  candy: "candy", reset: "crystal", virus: "virus" };
const itemIcon = it => (it.armor ? "armor" : it.shard ? "shard" : ITEM_ICON[it.key] || "bag");
const SHARDS_PER_EGG = 4;                  // wie game/explore.py
// Leckerbissen aus dem Rucksack: ein Stück Torte mit Kerze
const SNACK = ["...X....", "...X....", ".XXXXXX.", ".X.XX.X.", ".XXXXXX.", ".X....X.", ".XXXXXX.", "........"];
// Fleisch / Protein / Torte verschwinden in drei Bissen
const bites = icon => [icon,
  icon.map(r => r.slice(0, 5) + "..."),
  icon.map(r => r.slice(0, 3) + "....."),
  icon.map(() => "........")];
const BITES = { meat: bites(ICONS.meat), protein: bites(ICONS.protein), snack: bites(SNACK) };

// Besen (Stiel schräg nach hinten, Borsten unten auf dem Boden)
const BROOM = [
  "X.......", ".X......", ".X......", "..X.....", "..X.....", "...X....", "...X....", "....X...",
  "...XXX..", "...XXX..", "..XXXXX.", "..X.X.X.", ".X.X.X.X", ".X.X.X.X", "X.X.X.X.", "X.X.X.X.",
];
// Spritze: Kolben links, Nadel rechts (wird gespiegelt, damit sie aufs Digimon zeigt)
const SYRINGE = ["X.XXXXXXX....", "XXX.X.X.XXXXX", "X.XXXXXXX...."];
const DUMBBELL = ["XX......XX", "XXXXXXXXXX", "XX......XX"];
const SUN = ["X..X..X", ".X.X.X.", "..XXX..", "XXXXXXX", "..XXX..", ".X.X.X.", "X..X..X"];
const ANGER = ["X.X.X", ".X.X.", "X...X", ".X.X.", "X.X.X"];
const SPARK = ["X.X", ".X.", "X.X"];
const BUBBLE = [".X.", "X.X", ".X."];

const GRAVE = [
  "................", "......XXXX......", ".....X....X.....", "....X......X....",
  "....X..XX..X....", "....X.XXXX.X....", "....X..XX..X....", "....X..XX..X....",
  "....X......X....", "....X......X....", "....X......X....", "...XXXXXXXXXX...",
  "..X..........X..", "..XXXXXXXXXXXX..", "................", "................",
];

// Digi-Ei: Umriss einer Eiform plus Flecken
const EGG = (() => {
  const rows = [];
  for (let y = 0; y < 16; y++) {
    let row = "";
    for (let x = 0; x < 16; x++) {
      const dy = (y - 9) / (y < 9 ? 8 : 6.5);
      const dx = (x - 7.5) / (6.5 - Math.max(0, 8 - y) * 0.25);
      const d = dx * dx + dy * dy;
      const spot = (x >= 5 && x <= 7 && y >= 6 && y <= 8) || (x >= 9 && x <= 10 && y >= 10 && y <= 11);
      row += (d <= 1 && d > 0.62) || (d <= 1 && spot) ? "X" : ".";
    }
    rows.push(row);
  }
  return rows;
})();

// Die Sprache steht beim Laden fest (Umschalten lädt die Seite neu) – daher darf tr() schon hier laufen.
const ATTR_DE = { Vaccine: tr("Serum"), Data: tr("Daten"), Virus: "Virus", Free: tr("Frei") };

// ------------------------------------------------------------ Zustand
const S = {
  data: null,      // digimon.json (Sprites)
  state: null,     // letzter Stand vom Server
  anim: null,      // laufende Animation {type, food, start}
  mode: "main",    // Tastenfeld: main | food | train | eggs
  tick: 0,         // 10 Ticks pro Sekunde
  x: 8, dir: -1, pose: 0,
  bagKey: null, sellN: 1,   // Rucksack: gewähltes Item, Menge beim Verkaufen
};

const $ = sel => document.querySelector(sel);
const lcd = $("#lcd");
const ctx = lcd.getContext("2d");
let PX = 10;                         // Größe eines LCD-Pixels, passt sich dem Fenster an
// Display-Farben – ändern sich mit dem V-Pet-Design (applyTheme).
// DARK_*: Licht aus. Normal wird das Display dann "negativ" (Pixelfarbe als Hintergrund);
// bei Designs mit hellen Pixeln auf dunklem Display (Nachtmodus) wird es stattdessen schwarz.
let COLOR_BG, COLOR_PX, COLOR_GHOST, DARK_BG, DARK_PX;
function readLcdColors() {
  const css = getComputedStyle(document.documentElement);
  COLOR_BG = css.getPropertyValue("--lcd").trim();
  COLOR_PX = css.getPropertyValue("--lcd-pixel").trim();
  COLOR_GHOST = css.getPropertyValue("--lcd-ghost").trim();
  const inverted = luminance(COLOR_PX) > luminance(COLOR_BG);
  DARK_BG = inverted ? "#000000" : COLOR_PX;
  DARK_PX = inverted ? hexAlpha(COLOR_PX, 0.4) : COLOR_BG;
}

function luminance(hex) {
  const n = parseInt(String(hex).replace("#", ""), 16) || 0;
  return 0.3 * (n >> 16) + 0.59 * ((n >> 8) & 255) + 0.11 * (n & 255);
}

// V-Pet-Design (game/themes.py): Gehäuse-Verlauf + Display-Farben als CSS-Variablen.
// Auf dem Gerät gemerkt, damit beim Laden nicht kurz das alte Design aufblitzt.
const THEME_KEY = "vpet.theme";
// Farben des Datenregens im Hintergrund (folgen dem Design)
const RAIN = { a: "rgba(46,230,255,.35)", b: "rgba(255,138,31,.7)", fade: "rgba(2, 6, 19, .18)" };
let themeShown = null;
function applyTheme(theme) {
  if (!theme || theme.key === themeShown) return;
  themeShown = theme.key;
  const root = document.documentElement.style;
  ["a", "b", "c"].forEach((n, i) => root.setProperty(`--device-${n}`, theme.device[i]));
  root.setProperty("--lcd", theme.lcd);
  root.setProperty("--lcd-pixel", theme.pixel);
  root.setProperty("--lcd-ghost", hexAlpha(theme.pixel, 0.07));
  // Farben fürs ganze Spiel: Hintergrund, Flächen, Linien, Akzente (game/themes.py UI)
  const ui = theme.ui;
  if (ui) {
    root.setProperty("--deep", ui.deep);
    root.setProperty("--bg", ui.bg);
    root.setProperty("--panel", ui.panel);
    root.setProperty("--panel-2", ui.panel2);
    root.setProperty("--line", ui.line);
    root.setProperty("--cyan", ui.accent);
    root.setProperty("--orange", ui.accent2);
    if (ui.muted) root.setProperty("--muted", ui.muted);
    RAIN.a = hexAlpha(ui.accent, 0.35);
    RAIN.b = hexAlpha(ui.accent2, 0.7);
    RAIN.fade = hexAlpha(ui.deep, 0.18);
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = ui.bg;
    // Symbole auf Knöpfen (Zahnrad, Pokal …) in den neuen Farben
    document.querySelectorAll(".head-buttons canvas[data-icon], .event-bar canvas[data-icon]").forEach(paintIcon);
  }
  document.body.className = document.body.className.replace(/\btheme-\S+/g, "").trim();
  document.body.classList.add(`theme-${theme.key}`);
  readLcdColors();
  // Symbole im Display (Ruf, Krank, Schlaf, Licht) in der neuen Pixelfarbe neu malen
  document.querySelectorAll(".lcd canvas[data-icon]").forEach(paintIcon);
  try { localStorage.setItem(THEME_KEY, JSON.stringify(theme)); } catch { /* egal */ }
}

function hexAlpha(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}

readLcdColors();
try { applyTheme(JSON.parse(localStorage.getItem(THEME_KEY))); } catch { /* Standard-Design */ }
if (!themeShown) document.body.classList.add("theme-classic");

// Das LCD hat 32 x 24 Pixel: oben 8 Zeilen für Symbole (Ruf, Totenkopf, Zz),
// darunter das 32 x 16 große Spielfeld. Alle y-Angaben beim Zeichnen beziehen
// sich aufs Spielfeld; die Symbolleiste liegt bei y = HUD_Y.
const LCD_W = 32, LCD_H = 24, OY = 8, HUD_Y = -8;

// so groß wie möglich, in ganzen Pixeln für scharfe Kanten
function fitLcd() {
  const box = $("#lcd-box");
  const dpr = window.devicePixelRatio || 1;
  const w = box.clientWidth - 24, h = box.clientHeight - 24;
  const cssPx = Math.max(4, Math.floor(Math.min(w / LCD_W, h / LCD_H)));
  PX = Math.round(cssPx * dpr);
  lcd.width = LCD_W * PX;
  lcd.height = LCD_H * PX;
  lcd.style.width = LCD_W * cssPx + "px";
  lcd.style.height = LCD_H * cssPx + "px";
}
new ResizeObserver(fitLcd).observe($("#lcd-box"));

// ------------------------------------------------------------ Zeichnen
function drawBitmap(c, rows, ox, oy, scale, color, flip = false, gap = 0) {
  c.fillStyle = color;
  const w = rows[0].length;
  rows.forEach((row, y) => {
    for (let x = 0; x < w; x++) {
      const ch = row[flip ? w - 1 - x : x];
      if (ch === "1" || ch === "X") {
        c.fillRect((ox + x) * scale + gap, (oy + y) * scale + gap, scale - gap, scale - gap);
      }
    }
  });
}

function lcdPixels(rows, x, y, flip, dark) {
  drawBitmap(ctx, rows, x, y + OY, PX, dark ? DARK_PX : COLOR_PX, flip, Math.max(1, Math.round(PX / 12)));
}

function lcdRect(x, y, w, h, dark) {
  const gap = Math.max(1, Math.round(PX / 12));
  ctx.fillStyle = dark ? DARK_PX : COLOR_PX;
  for (let yy = y + OY; yy < y + OY + h; yy++) {
    for (let xx = x; xx < x + w; xx++) ctx.fillRect(xx * PX + gap, yy * PX + gap, PX - gap, PX - gap);
  }
}

function clearLcd(dark) {
  ctx.fillStyle = dark ? DARK_BG : COLOR_BG;
  ctx.fillRect(0, 0, lcd.width, lcd.height);
  // schwaches Pixelraster wie bei einem echten LCD
  const gap = Math.max(1, Math.round(PX / 12));
  ctx.fillStyle = dark ? "rgba(255,255,255,.03)" : COLOR_GHOST;
  for (let y = 0; y < LCD_H; y++) {
    for (let x = 0; x < LCD_W; x++) ctx.fillRect(x * PX + gap, y * PX + gap, PX - gap, PX - gap);
  }
}

// Symbolleiste oben: Ruf links, Totenkopf Mitte, Zz rechts (blinken)
function renderHud(pet, dark) {
  const blink = Math.floor(S.tick / 5) % 2 === 0;
  if (pet.call && blink) lcdPixels(ICONS.call, 1, HUD_Y, false, dark);
  if ((pet.sick || pet.injured) && blink) lcdPixels(ICONS.skull, 12, HUD_Y, false, dark);
  if (pet.asleep && Math.floor(S.tick / 10) % 2) lcdPixels(ICONS.zz, 24, HUD_Y, false, dark);
  // Deko „Fledermäuse“: ab und zu flattert eine durch die Symbolleiste (nur wenn dort Platz ist)
  if (hasDecor("bats") && !pet.call && !pet.sick && !pet.injured && !pet.asleep) {
    const x = 32 - Math.floor((S.tick % 90) / 2);
    if (x > -9) lcdPixels(BAT[Math.floor(S.tick / 3) % 2], x, HUD_Y + 1 + (Math.floor(S.tick / 6) % 2), false, dark);
  }
}

// ------------------------------------------------------------ Deko (game/decor.py)
// Gekaufte Deko liegt blass hinter dem Digimon, damit sie nie von Ruf/Haufen ablenkt.
const HEART_S = ["XX.XX", "XXXXX", ".XXX.", "..X.."];
const STARS = [[9, -7, 0], [21, -6, 7], [10, -3, 13], [22, -2, 4], [4, -1, 10], [28, -1, 16]];
const BUBBLES = [{ x: 0, speed: 3, off: 0 }, { x: 28, speed: 4, off: 11 }, { x: 1, speed: 5, off: 17 }];
const SNOW = [{ x: 2, speed: 3, off: 0 }, { x: 7, speed: 4, off: 9 }, { x: 13, speed: 3, off: 15 },
  { x: 19, speed: 5, off: 4 }, { x: 25, speed: 4, off: 19 }, { x: 30, speed: 3, off: 12 }];

function hasDecor(key) {
  return !!(S.state && (S.state.decor || []).includes(key));
}

function renderDecor(pet, dark) {
  const list = (S.state && S.state.decor) || [];
  if (!list.length) return;
  ctx.save();
  ctx.globalAlpha = 0.45;
  if (list.includes("stars")) {
    // funkeln abwechselnd in den freien Lücken der Symbolleiste
    STARS.forEach(([x, y, off]) => {
      const phase = (Math.floor(S.tick / 4) + off) % 12;
      if (phase < 4) lcdPixels(phase === 1 || phase === 2 ? PLUS : ["X"], x - (phase === 1 || phase === 2 ? 1 : 0), y - (phase === 1 || phase === 2 ? 1 : 0), false, dark);
    });
  }
  if (list.includes("bubbles")) {
    BUBBLES.forEach(b => {
      const y = 16 - ((Math.floor(S.tick / b.speed) + b.off) % 28);
      lcdPixels(BUBBLE, b.x + (Math.floor(S.tick / 8 + b.off) % 2), y, false, dark);
    });
  }
  if (list.includes("snow")) {
    SNOW.forEach(f => {
      const y = ((Math.floor(S.tick / f.speed) + f.off) % 25) - 8;
      lcdRect(f.x + (Math.floor((S.tick + f.off) / 12) % 2), y, 1, 1, dark);
    });
  }
  if (list.includes("hearts") && !pet.asleep && !pet.sick && !pet.injured) {
    // alle 10 Sekunden steigt ein Herz über dem Kopf auf
    const t = S.tick % 100;
    if (t < 24) lcdPixels(HEART_S, Math.min(S.x, walkLimit(pet)) + 5, 1 - Math.floor(t / 3), false, dark);
  }
  ctx.restore();
}

function sprite(dex, kind, i = 0) {
  const d = S.data.digimon[dex];
  const list = S.data.frames[kind];
  return d.frames[list[i % list.length]];
}

function poopSlots(count) {
  // bis zu 4 Haufen, rechts in einem 2x2-Raster
  return [[24, 8], [24, 0], [16, 8], [16, 0]].slice(0, count);
}

function walkLimit(pet) {
  const cols = pet.poop === 0 ? 0 : pet.poop <= 2 ? 1 : 2;
  return 16 - cols * 8;   // höchste x-Position für ein 16 Pixel breites Sprite
}

// ------------------------------------------------------------ Kühlschrank
// Ein echter Kühlschrank übers ganze Display: oben das Gefrierfach, darunter die
// große Tür mit Griff, unten zwei Füße. Die Tür hat ihr Scharnier links.
// Innenraum: x 7..24, y -3..13 – das 16x16-Digimon steht darin bei x 8, y -2.
const FRIDGE_FLAKES = [{ x: 0, speed: 3, off: 0 }, { x: 3, speed: 4, off: 13 },
  { x: 27, speed: 4, off: 6 }, { x: 29, speed: 3, off: 19 }];
const FRIDGE_SPARKLES = [[11, 1], [17, 4], [13, 8], [19, 10], [10, 12], [15, 0]];
const PLUS = [".X.", "XXX", ".X."];

// Pixel wieder "ausschalten" (Hintergrund + LCD-Raster)
function lcdErase(x, y, w, h) {
  const gap = Math.max(1, Math.round(PX / 12));
  for (let yy = y + OY; yy < y + OY + h; yy++) {
    for (let xx = x; xx < x + w; xx++) {
      ctx.fillStyle = COLOR_BG;
      ctx.fillRect(xx * PX, yy * PX, PX, PX);
      ctx.fillStyle = COLOR_GHOST;
      ctx.fillRect(xx * PX + gap, yy * PX + gap, PX - gap, PX - gap);
    }
  }
}

function drawFridge(open, inside, flakes) {
  // Gehäuse, Trennlinie zum Gefrierfach, Füße
  lcdRect(6, -8, 20, 1, false);
  lcdRect(6, 14, 20, 1, false);
  lcdRect(6, -8, 1, 23, false);
  lcdRect(25, -8, 1, 23, false);
  lcdRect(6, -4, 20, 1, false);
  lcdRect(7, 15, 2, 1, false);
  lcdRect(23, 15, 2, 1, false);
  // Gefrierfach: Griff + kleine Schneeflocke + blinkende Kontrollleuchte
  lcdRect(20, -6, 3, 1, false);
  lcdPixels(PLUS, 8, -7, false, false);
  if (Math.floor(S.tick / 10) % 2) lcdRect(12, -6, 1, 1, false);

  // Innenraum mit Digimon (sichtbar, sobald die Tür aufgeht)
  if (open > 0 && inside) inside();
  // Tür: je weiter offen, desto schmaler wird sie (sie dreht sich zum Scharnier links)
  const w = Math.round(18 * (1 - open));
  if (w > 0) {
    lcdErase(7, -3, w, 17);
    if (w < 18) lcdRect(7 + w, -3, 1, 17, false);        // Türkante
    if (w >= 3) lcdRect(5 + w, 0, 1, 6, false);         // Griff
    if (open === 0) {
      // Reif glitzert auf der Tür
      FRIDGE_SPARKLES.forEach(([x, y], i) => {
        if ((Math.floor(S.tick / 6) + i * 3) % 7 === 0) lcdRect(x, y, 1, 1, false);
      });
    }
  }
  // offene Tür steht links heraus, mit Fächern innen
  const pw = Math.round(5 * open);
  if (pw >= 2) {
    const x0 = 6 - pw;
    lcdRect(x0, -3, pw, 1, false);
    lcdRect(x0, 13, pw, 1, false);
    lcdRect(x0, -3, 1, 17, false);
    if (pw >= 4) [2, 7].forEach(y => lcdRect(x0 + 1, y, pw - 1, 1, false));
  }
  // kalte Luft: Flocken rieseln links und rechts am Kühlschrank vorbei
  FRIDGE_FLAKES.forEach((f, i) => {
    if (f.x < 6 && pw >= 2) return;                      // da steht gerade die Tür
    if (!flakes && i % 2) return;
    const y = ((Math.floor(S.tick / f.speed) + f.off) % 30) - 10;
    lcdPixels(PLUS, f.x, y, false, false);
  });
}

function renderFridge(pet, anim) {
  const t = anim ? S.tick - anim.start : 0;
  const ramp = (from, to) => Math.max(0, Math.min(1, (t - from) / (to - from)));
  const body = kind => () => {
    if (pet.dex) lcdPixels(sprite(pet.dex, kind, Math.floor(S.tick / 5)), 8, -2, false, false);
    else lcdPixels(EGG, 8, -2, false, false);
  };

  if (anim && anim.type === "fridge_in") {
    // Digimon steht drin, Tür geht zu, dann wird's kalt
    drawFridge(1 - ramp(12, 20), body("happy"), t > 20);
    if (t > 40) S.anim = null;
    return;
  }
  if (anim && anim.type === "fridge_out") {
    // Tür geht auf, Digimon freut sich und hüpft raus
    const open = ramp(0, 8);
    const hop = t > 8 && Math.floor(t / 4) % 2 ? -1 : 0;
    drawFridge(open, () => {
      if (pet.dex) lcdPixels(sprite(pet.dex, t > 8 ? "happy" : "sleep", Math.floor(t / 5)), 8, -2 + hop, false, false);
      else lcdPixels(EGG, 8, -2 + hop, false, false);
    }, false);
    if (t > 28) S.anim = { type: "happy", start: S.tick };
    return;
  }
  // geschlossen – alle 10 Sekunden kurz die Tür auf: "Schläft es noch?"
  const c = S.tick % 100;
  const open = c < 70 ? 0 : c < 75 ? (c - 70) / 5 : c < 90 ? 1 : c < 95 ? (95 - c) / 5 : 0;
  drawFridge(open, body("sleep"), true);
}

// ------------------------------------------------------------ Animationen zu den Aktionen
// t = Ticks seit dem Start (10 pro Sekunde). Liefert true, solange etwas gezeichnet wurde.
function renderAnim(pet, a, t, dark) {
  const mon = (kind, x = 8, y = 0, flip = false, dex = pet.dex) => lcdPixels(sprite(dex, kind, Math.floor(t / 5)), x, y, flip, dark);
  const px = (rows, x, y, flip = false) => lcdPixels(rows, x, y, flip, dark);
  const done = (next = null) => { S.anim = next ? { type: next, start: S.tick } : null; };
  const blink = n => Math.floor(t / n) % 2 === 1;

  switch (a.type) {
    case "eat":
    case "overfeed": {
      // Bissen für Bissen – beim Überfressen kommt danach ein Rülpser
      if (t <= 24) {
        px(BITES[a.food || "meat"][Math.min(3, Math.floor(t / 6))], 1, 8);
        mon("eat", 9);
      } else if (a.type === "overfeed" && t <= 44) {
        mon(blink(4) ? "happy" : "idle", 9);
        px(BUBBLE, 8, 2 - Math.floor((t - 24) / 3));
        if (t > 32) px(BUBBLE, 6, 6 - Math.floor((t - 32) / 3));
      } else done();
      return true;
    }
    case "clean": {
      // Besen fegt von links nach rechts und schiebt die Haufen vom Bildschirm
      const bx = 16 + t;
      mon(blink(4) ? "happy" : "idle", -2);
      if (bx <= 33) {
        poopSlots(a.poop || 1).forEach(([x, y]) => px(ICONS.poop, Math.max(x, bx + 8), y));
        px(BROOM, bx, 0);
        if (t % 2) lcdRect(bx - 1, 14, 1, 1, dark);                    // Staubwölkchen
        else lcdRect(bx - 2, 13, 1, 1, dark);
      } else if (t < 44) {
        // blitzblank: es funkelt, wo vorher die Haufen lagen
        poopSlots(a.poop || 1).forEach(([x, y], i) => { if ((Math.floor(t / 3) + i) % 2) px(SPARK, x + 3, y + 3); });
      } else done("happy");
      return true;
    }
    case "medicine": {
      // Spritze fliegt heran, Pieks, dann ist es gesund
      if (t < 8) { mon("sick", 2); px(SYRINGE, 32 - t * 2, 6, true); }
      else if (t < 16) { mon("tired", 2); px(SYRINGE, 16 + (blink(2) ? 1 : 0), 6, true); }
      else if (t < 22) { mon("happy", 2); px(SYRINGE, 16 + (t - 16) * 3, 6, true); }
      else if (t < 40) {
        mon(blink(4) ? "happy" : "idle", 8);
        [[0, -7], [25, -5], [25, 5]].forEach(([x, y], i) => { if ((Math.floor(t / 3) + i) % 2) px(ICONS.medicine.slice(0, 7), x, y); });
      } else done();
      return true;
    }
    case "cheer": {
      // Training geschafft: Freudensprünge, Sterne funkeln
      mon("happy", 8, blink(3) ? -2 : 0);
      [[1, -6], [26, -6], [2, 6], [27, 6]].forEach(([x, y], i) => { if ((Math.floor(t / 3) + i) % 2) px(SPARK, x, y); });
      if (t > 24) done();
      return true;
    }
    case "angry":
    case "refuse": {
      // Kopfschütteln – bei "angry" mit Ärger-Zeichen über dem Kopf
      mon(a.type, 8, 0, blink(3));
      if (a.type === "angry" && blink(2)) px(ANGER, 22, -6);
      if (t > 18) done();
      return true;
    }
    case "wake": {
      // Licht an: blinzeln, strecken, die Sonne geht auf
      mon(t < 10 ? "sleep" : blink(4) ? "happy" : "idle");
      if (t >= 6) px(SUN, 24, Math.max(-8, -2 - Math.floor((t - 6) / 2)));
      if (t > 30) done();
      return true;
    }
    case "lift": {
      // Trainingsgewicht stemmen: hoch – runter – hoch
      const up = blink(5);
      mon(up ? "happy" : "idle");
      px(DUMBBELL, 11, up ? -5 : -3);
      if (t > 30) done();
      return true;
    }
    case "charm":
    case "totem": {
      // Glücksbringer / Schutz-Totem schwebt herab und funkelt
      mon(blink(4) ? "happy" : "idle");
      px(a.type === "totem" ? ICONS.totem : ICONS.star, 12, -8 + Math.min(2, Math.floor(t / 4)));
      if (t > 12) [[4, -6], [22, -4]].forEach(([x, y], i) => { if ((Math.floor(t / 3) + i) % 2) px(SPARK, x, y); });
      if (t > 30) done();
      return true;
    }
    case "hatch": {
      // Ei wackelt, bekommt einen Riss, springt auf – das Baby ist da
      if (t < 10) px(EGG, 8 + (t % 2 ? 1 : -1), 0);
      else if (t < 18) {
        px(EGG, 8, 0);
        for (let x = 3; x <= 12; x++) lcdRect(8 + x, 7 + (x % 2), 1, 1, dark);     // Zickzack-Riss
      } else if (t < 32) {
        const s = t - 18;
        mon("happy");
        px(EGG.slice(0, 8), 8 - s, -s);                                  // obere Schale fliegt weg
        px(EGG.slice(8).map(r => r.slice(0, 8)), 8 - s, 8);            // untere Hälften
        px(EGG.slice(8).map(r => r.slice(8)), 16 + s, 8);
      } else done("happy");
      return true;
    }
    case "armor": {
      // Armor-Digitation: das Armor-Ei sinkt auf das Digimon und leuchtet – dann die Digitation
      if (t < 26) {
        mon(t < 14 ? "idle" : "happy", 8, 0, false, a.from || pet.dex);
        if (t < 16 || blink(2)) px(ICONS.armor, 12, Math.min(-2, -10 + Math.floor(t / 2)));
        if (t >= 16) [[2, -6], [24, -6], [2, 6], [26, 6]].forEach(([x, y], i) => { if ((Math.floor(t / 2) + i) % 2) px(SPARK, x, y); });
      } else S.anim = { type: "evolve", from: a.from, start: S.tick };
      return true;
    }
    case "evolve": {
      // Digitation: altes und neues Digimon wechseln sich immer schneller ab, mit Lichtblitzen
      if (t < 36) {
        const speed = t < 12 ? 6 : t < 24 ? 3 : 1;
        const flash = t >= 12 && t % 6 === 0;
        if (flash) clearLcd(!dark);
        const showNew = Math.floor(t / speed) % 2 === 1;
        lcdPixels(sprite(showNew ? pet.dex : a.from, "idle"), 8, 0, false, flash ? !dark : dark);
        // Lichtstrahlen
        if (t >= 24) [[2, 2], [27, 2], [2, 12], [27, 12]].forEach(([x, y]) => lcdRect(x, y, 2, 1, flash ? !dark : dark));
      } else if (t < 50) {
        mon(blink(4) ? "happy" : "idle");
        [[1, -6], [26, -6], [3, 8], [26, 8]].forEach(([x, y], i) => { if ((Math.floor(t / 3) + i) % 2) px(SPARK, x, y); });
      } else done();
      return true;
    }
    case "return": {
      // zurück vom Erkunden: kommt von rechts angelaufen
      const x = Math.max(8, 32 - t);
      if (x > 8) {
        mon("idle", x, 0, false);
        if (t % 4 < 2) lcdRect(x + 15, 15, 1, 1, dark);
      } else done("happy");
      return true;
    }
    case "happy": {
      mon(blink(5) ? "happy" : "idle");
      if (t > 20) done();
      return true;
    }
  }
  done();
  return false;
}

// Schutz-Totem rettet vor dem Tod: Digimon sackt zusammen, das Totem erscheint,
// dreht sich im Lichtblitz (wie in Minecraft) – dann geht's ab in den Kühlschrank
function renderTotemSave(pet, t) {
  if (t < 12) {
    if (t % 4 < 3) lcdPixels(sprite(pet.dex, "tired"), 8, 0, false, false);
    return;
  }
  if (t < 36) {
    const flash = t < 24 && t % 4 === 0;
    if (flash) clearLcd(true);
    lcdPixels(sprite(pet.dex, t < 24 ? "tired" : "happy"), 8, 0, false, flash);
    // Totem dreht sich (spiegeln) und steigt dabei auf
    lcdPixels(ICONS.totem, 12, -4 - Math.min(4, Math.floor((t - 12) / 3)), Math.floor(t / 2) % 2 === 1, flash);
    [[1, -7], [26, -7], [2, 3], [27, 3], [5, 10], [23, 10]].forEach(([x, y], i) => {
      if ((Math.floor(t / 2) + i) % 3 === 0) lcdPixels(SPARK, x, y, false, flash);
    });
    return;
  }
  S.anim = { type: "fridge_in", start: S.tick };
  renderFridge(pet, S.anim);
}

// Reset-Kristall: das Digimon flackert immer schneller, ein Lichtblitz – und da liegt ein Ei
function renderReset(a, t, dark) {
  if (t < 18 && a.from) {
    const speed = t < 8 ? 4 : t < 14 ? 2 : 1;
    if (Math.floor(t / speed) % 2 === 0) lcdPixels(sprite(a.from, "idle"), 8, 0, false, dark);
    lcdPixels(ICONS.crystal, 12, -8 + Math.min(2, Math.floor(t / 3)), false, dark);
    return;
  }
  if (t < 26) {
    const flash = t % 4 < 2;
    if (flash) clearLcd(!dark);
    lcdPixels(EGG, 8, 0, false, flash ? !dark : dark);
    return;
  }
  lcdPixels(EGG, 8 + (Math.floor(t / 4) % 2), 0, false, dark);
  [[2, -6], [26, -6], [3, 8], [26, 8]].forEach(([x, y], i) => {
    if ((Math.floor(t / 3) + i) % 2) lcdPixels(SPARK, x, y, false, dark);
  });
  if (t > 44) S.anim = null;
}

function render() {
  const st = S.state;
  const pet = st && st.pet;
  const dark = !!(pet && pet.alive && !pet.light);
  clearLcd(dark);
  if (!S.data) return;

  if (!pet) {
    // noch kein Digimon: ein Ei wackelt und wartet
    lcdPixels(EGG, 8 + (Math.floor(S.tick / 5) % 2), 0, false, false);
    return;
  }
  if (!pet.alive) {
    const a = S.anim && S.anim.type === "death" ? S.anim : null;
    const t = a ? S.tick - a.start : 99;
    if (t < 16) {
      // es wird schwächer und schwächer ...
      if (t % 4 < 3) lcdPixels(sprite(a.from, "tired"), 8, 0, false, false);
      return;
    }
    lcdPixels(GRAVE, 8, 0, false, false);
    // ... und schwebt blinkend nach oben davon
    if (t < 40 && t % 2) lcdPixels(sprite(a.from, "sleep"), 8, -(t - 16), false, false);
    if (a && t >= 40) S.anim = null;
    return;
  }
  if (S.anim && S.anim.type === "totem_save") return renderTotemSave(pet, S.tick - S.anim.start);
  if (S.anim && S.anim.type === "reset") return renderReset(S.anim, S.tick - S.anim.start, dark);
  const fridgeAnim = S.anim && S.anim.type.startsWith("fridge") ? S.anim : null;
  if (pet.frozen || fridgeAnim) return renderFridge(pet, fridgeAnim);
  if (pet.stage === "Egg") {
    lcdPixels(EGG, 8 + (Math.floor(S.tick / 5) % 2), 0, false, dark);
    return;
  }
  if (pet.away) {
    // unterwegs: Haus links, Fußspuren laufen in die Ferne
    lcdPixels(ICONS.home, 1, 8, false, false);
    for (let i = 0; i < 6; i++) {
      const x = 11 + i * 3 + ((Math.floor(S.tick / 4) + i) % 2);
      if ((Math.floor(S.tick / 4) + i) % 6 < 4) lcdRect(x, 12 - (i % 2), 1, 1, false);
    }
    lcdPixels(ICONS.explore, 24, 0, false, false);
    return;
  }
  if (S.mode === "scout" && pet.scout) {
    // wildes Digimon taucht auf: beide schauen sich an
    lcdPixels(sprite(pet.dex, "idle", Math.floor(S.tick / 5)), 0, 0, true, false);
    lcdPixels(sprite(pet.scout.dex, "idle", Math.floor(S.tick / 6)), 16, 0, false, false);
    return;
  }
  if (S.mode === "battle" || (S.mode === "duel" && F.opp)) return renderBattle(pet);
  if ((S.mode === "challenged" || S.mode === "duelwait") && S.state.duel) {
    // Herausforderung: beide schauen sich an (Gegner-Digimon, falls bekannt)
    const d = S.state.duel;
    lcdPixels(sprite(pet.dex, "idle", Math.floor(S.tick / 5)), 0, 0, true, false);
    if (d.opp_pet) lcdPixels(sprite(d.opp_pet.dex, "idle", Math.floor(S.tick / 6)), 16, 0, false, false);
    if (Math.floor(S.tick / 5) % 2) lcdPixels(ICONS.call, 12, HUD_Y, false, false);
    return;
  }
  if (S.mode === "train") return renderTraining(pet, dark);

  renderDecor(pet, dark);
  renderHud(pet, dark);
  poopSlots(pet.poop).forEach(([x, y]) => lcdPixels(ICONS.poop, x, y, false, dark));

  if (S.anim && renderAnim(pet, S.anim, S.tick - S.anim.start, dark)) return;

  if (pet.asleep) {
    lcdPixels(sprite(pet.dex, "sleep", Math.floor(S.tick / 10)), Math.min(S.x, walkLimit(pet)), 0, false, dark);
    return;
  }
  if (pet.sick || pet.injured) {
    const frame = S.tick % 50 === 49 ? "tired" : "sick";
    lcdPixels(sprite(pet.dex, frame), Math.min(S.x, walkLimit(pet)), 0, false, dark);
    return;
  }

  lcdPixels(sprite(pet.dex, "idle", S.pose), S.x, 0, S.dir > 0, dark);
}

function stepWalk() {
  const pet = S.state && S.state.pet;
  if (!pet || !pet.alive || pet.stage === "Egg" || pet.asleep || pet.frozen || pet.away || S.anim || S.mode !== "main") return;
  const limit = walkLimit(pet);
  if (Math.random() < 0.3) S.dir = -S.dir;
  S.x += S.dir * 2;
  if (S.x <= 0) { S.x = 0; S.dir = 1; }
  if (S.x >= limit) { S.x = limit; S.dir = -1; }
  S.pose ^= 1;
}

// ------------------------------------------------------------ Training auf dem LCD
// Drei Trainingsarten mit eigenem Minispiel:
//   Kraft:        ein Zeiger pendelt durch eine Skala – im Kasten drücken (3 von 5)
//   Tempo:        5 Sekunden lang so oft wie möglich drücken (25 Mal)
//   Verteidigung: ein Angriff fliegt heran – kurz vor dem Einschlag blocken (3 von 5)
const T = { kind: "power", hits: [], zone: 0, start: 0, locked: false };
const ZONE_H = 3;
const SPEED_TIME = 5000, SPEED_GOAL = 25;
// eigene Liste statt tr(): "Kraft" heißt im Englischen sonst "Strength" (die Herzen-Anzeige)
const SKILL_NAME = I18N.lang === "en" ? { power: "Power", speed: "Speed", defense: "Defense" }
  : { power: "Kraft", speed: "Tempo", defense: "Verteidigung" };
const TRAIN_HELP = {
  power: tr("Drück, wenn der Zeiger im Kasten ist. 3 von 5 Treffern!"),
  speed: tr("Drück so oft du kannst! {goal} Mal in 5 Sekunden.", { goal: SPEED_GOAL }),
  defense: tr("Ein Angriff fliegt heran – drück kurz vor dem Einschlag zum Blocken. Nicht zu früh! 3 von 5."),
};

function needleY() {
  const phase = (performance.now() - T.start) / 230;
  return 1 + Math.round(13 * (Math.sin(phase) + 1) / 2);   // 1..14
}

function resultDots(dark) {
  // oben in der Symbolleiste: großer Punkt = geschafft, kleiner = daneben
  for (let i = 0; i < 5; i++) {
    const x = 2 + i * 6, hit = T.hits[i];
    if (hit === true) lcdRect(x, HUD_Y + 2, 4, 4, dark);
    else if (hit === false) lcdRect(x + 1, HUD_Y + 3, 2, 2, dark);
    else { lcdRect(x, HUD_Y + 2, 4, 1, dark); lcdRect(x, HUD_Y + 5, 4, 1, dark); }
  }
}

function renderTraining(pet, dark) {
  if (T.kind === "speed") return renderSpeed(pet, dark);
  if (T.kind === "defense") return renderDefense(pet, dark);
  const attack = T.locked ? "attack" : "idle";
  lcdPixels(sprite(pet.dex, attack, S.pose), 1, 0, false, dark);
  // Skala-Rahmen x 20..27, Zielbereich, Zeiger
  lcdRect(20, 0, 8, 1, dark);
  lcdRect(20, 15, 8, 1, dark);
  lcdRect(20, 0, 1, 16, dark);
  lcdRect(27, 0, 1, 16, dark);
  lcdRect(22, T.zone, 4, 1, dark);
  lcdRect(22, T.zone + ZONE_H - 1, 4, 1, dark);
  lcdRect(21, needleY(), 6, 1, dark);
  resultDots(dark);
}

function renderSpeed(pet, dark) {
  const elapsed = performance.now() - T.start;
  if (!T.locked && elapsed >= SPEED_TIME) finishTraining(T.presses >= SPEED_GOAL);
  // oben: Restzeit (dünn) und Fortschritt zum Ziel (dick)
  const left = Math.max(0, 1 - elapsed / SPEED_TIME);
  lcdRect(0, HUD_Y + 1, Math.max(0, Math.round(left * 32)), 1, dark);
  lcdRect(0, HUD_Y + 4, 32, 1, dark);
  lcdRect(0, HUD_Y + 6, 32, 1, dark);
  lcdRect(0, HUD_Y + 5, Math.min(32, Math.round(T.presses / SPEED_GOAL * 32)), 1, dark);
  // das Digimon rennt – jeder Druck ein Schritt
  const x = 8 + (T.presses % 2) * 2;
  lcdPixels(sprite(pet.dex, T.locked ? "happy" : "idle", T.presses), x, 0, true, dark);
  // Staubwolken hinter ihm
  if (!T.locked && T.presses % 2) lcdRect(x - 3, 13, 2, 2, dark);
}

function renderDefense(pet, dark) {
  const now = performance.now();
  const shot = T.shot;
  if (shot && !shot.done && now - shot.start >= DEFENSE_FLIGHT) defenseResult(false, tr("Getroffen!"));
  const blocked = shot && shot.done && shot.blocked && now - shot.doneAt < 600;
  const hurt = shot && shot.done && !shot.blocked && now - shot.doneAt < 600;
  lcdPixels(sprite(pet.dex, blocked ? "attack" : hurt ? "tired" : "idle", Math.floor(S.tick / 5)), 0, 0, true, dark);
  if (shot && !shot.done) {
    const p = (now - shot.start) / DEFENSE_FLIGHT;     // 0 .. 1
    lcdPixels(BALL, 29 - Math.round(p * 15), 6, false, dark);
  }
  if (blocked) lcdRect(16, 3, 1, 10, dark);               // Schild
  resultDots(dark);
}

const DEFENSE_FLIGHT = 1100;        // so lange fliegt ein Angriff (ms)
const DEFENSE_WINDOW = 0.55;        // ab diesem Anteil der Flugzeit zählt Blocken

function nextDefenseShot() {
  T.shot = null;
  if (T.hits.length >= 5) return;
  clearTimeout(T.timer);
  T.timer = setTimeout(() => {
    if (S.mode !== "train" || T.kind !== "defense") return;
    T.shot = { start: performance.now(), done: false };
    sfx("attack");
  }, 700 + Math.random() * 1600);
}

function defenseResult(blocked, text) {
  clearTimeout(T.timer);              // geplanten Angriff verwerfen, die Runde ist entschieden
  if (!T.shot) T.shot = { start: 0 };
  T.shot.done = true;
  T.shot.blocked = blocked;
  T.shot.doneAt = performance.now();
  T.hits.push(blocked);
  sfx(blocked ? "trainhit" : "cancel");
  setMessage(text);
  if (T.hits.length >= 5) finishTraining(T.hits.filter(Boolean).length >= 3);
  else T.timer = setTimeout(nextDefenseShot, 600);
}

function startTraining(kind = "power") {
  clearTimeout(T.timer);
  clearTimeout(T.endTimer);
  Object.assign(T, { kind, hits: [], presses: 0, locked: false, start: performance.now(), shot: null });
  newZone();
  setMode("train");
  setMessage(TRAIN_HELP[kind]);
  if (kind === "defense") nextDefenseShot();
}

function newZone() { T.zone = 1 + Math.floor(Math.random() * (14 - ZONE_H)); }

function trainingHit() {
  if (T.locked) return;
  if (T.kind === "speed") {
    T.presses++;
    if (T.presses % 5 === 0) sfx("menu");
    return;
  }
  if (T.kind === "defense") {
    const shot = T.shot;
    if (!shot || shot.done) return defenseResult(false, tr("Zu früh! Warte, bis der Angriff heranfliegt."));
    const p = (performance.now() - shot.start) / DEFENSE_FLIGHT;
    return defenseResult(p >= DEFENSE_WINDOW, p >= DEFENSE_WINDOW ? tr("Geblockt!") : tr("Zu früh geblockt!"));
  }
  const y = needleY();
  const hit = y >= T.zone && y < T.zone + ZONE_H;
  T.hits.push(hit);
  sfx(hit ? "trainhit" : "cancel");
  newZone();
  if (T.hits.length >= 5) finishTraining(T.hits.filter(Boolean).length >= 3);
}

function finishTraining(success) {
  if (T.locked) return;
  T.locked = true;
  clearTimeout(T.timer);
  const kind = T.kind;
  if (kind === "speed") {
    setMessage(success ? tr("{n} Mal gedrückt – geschafft!", { n: T.presses })
      : tr("{n} Mal gedrückt – {goal} wären nötig gewesen.", { n: T.presses, goal: SPEED_GOAL }));
  }
  T.endTimer = setTimeout(() => {
    sfx(success ? "win" : "lose");
    if (S.mode === "train") setMode("main");
    act("train", { success, kind });
  }, 900);
}

// ------------------------------------------------------------ Kampf auf dem LCD
// Wie beim V-Pet: links dein Digimon, rechts der Gegner, Schüsse fliegen hin und
// her. ↑ oder ↓ halten = laden (oben die Leiste, zweite Stufe = MEGA), loslassen =
// Schuss in diese Höhe. Danach fliegt der Gegenangriff oben oder unten heran:
// Ball unten -> ↑ springen, Ball oben -> ↓ ducken, kurz vor dem Einschlag.
// Jeder Treffer (ausgeteilt oder eingesteckt) füllt die Spezial-Leiste (Striche unter den Leben).
const BALL = ["XXX", "XXX", "XXX"];
const BIG_BALL = [".XXX.", "XXXXX", "XXXXX", "XXXXX", ".XXX."];
const PHASE = 8;                          // Ticks pro Animationsschritt (0,8 s)
const STEP_MS = PHASE * 100;
const BATTLE_STAGES = ["Rookie", "Champion", "Armor", "Ultimate", "Mega"];
const CHARGE_MS = 1200;                   // so lange braucht eine Stufe der Ladeleiste
const CHARGE_MAX = 2;                     // Stufe 2 (MEGA) feuert von selbst
const SPECIAL_MAX = 3;                    // Spezial-Leiste voll
const MASH_MS = 2000, MASH_GOAL = 16;     // Spezialattacke: 2 s drücken, 16 Drücker = volle Wirkung
const DODGE_FLIGHT = 1300;                // so lange fliegt ein Gegenangriff bis zum Einschlag (ms)
const DODGE_PASS = 350;                   // ausgewichen: so lange fliegt er noch vorbei
const WARN_MS = 1000;                     // Ankündigung eines starken Angriffs
const JUMP = -5, DUCK = 5;                // Ausweichen: Sprite hoch- bzw. runterversetzen
const BALL_Y = { high: 2, low: 12 }, BIG_Y = { high: 0, low: 11 };
// Phasen, in denen gerade eine Animation läuft (dann wartet alles andere)
const FIGHT_ANIM = ["pause", "myShot", "oppImpact", "oppWarn", "oppShot", "dodge", "myImpact", "end"];
// Gegenangriff unterwegs: die Knöpfe heißen dann Springen / Ducken
const DODGE_PHASES = ["oppWarn", "oppShot", "dodge"];
const F = { phase: "aim", steps: [], step: null, t0: 0, start: 0, myHp: 3, oppHp: 3, myMax: 3, oppMax: 3,
  myGauge: 0, oppGauge: 0, opp: null, hold: null, mash: null, token: 0, dodged: [], incoming: [], note: "" };
// Persönlichkeiten wilder Gegner (den Namen schickt normalerweise der Server mit)
const PERSONALITY = { normal: tr("ruhig"), aggressive: tr("aggressiv"), armored: tr("gepanzert"),
  nimble: tr("flink"), sly: tr("listig") };

// Zahl vom Server – oder ein Ersatzwert, falls das Feld fehlt
const numOr = (v, fallback) => (typeof v === "number" && isFinite(v) ? v : fallback);
const ballY = (side, big) => (big ? BIG_Y : BALL_Y)[side === "low" ? "low" : "high"];
const myName = () => { const p = S.state && S.state.pet; return p ? p.nickname || p.name : ""; };

function hpPips(x, hp, max) {
  for (let i = 0; i < max; i++) {
    if (i < hp) lcdRect(x + i * 3, HUD_Y + 3, 2, 2, false);
    else lcdRect(x + i * 3, HUD_Y + 4, 2, 1, false);
  }
}

// Spezial-Leiste: kleine Striche unter den Leben (leer = Punkt, voll = blinkt)
function gaugeDots(x, n) {
  for (let i = 0; i < SPECIAL_MAX; i++) {
    if (i >= n) lcdRect(x + i * 3 + 1, HUD_Y + 6, 1, 1, false);
    else if (n < SPECIAL_MAX || Math.floor(S.tick / 3) % 2) lcdRect(x + i * 3, HUD_Y + 6, 2, 1, false);
  }
}

// Ladeleiste zwischen den Lebensanzeigen (x 12..19, Platz für je 4 Leben).
// Stufe 1 füllt die Mitte, Stufe 2 (MEGA) macht sie dicker und blinkt.
function chargeBar(v) {
  lcdRect(12, HUD_Y + 2, 8, 1, false);
  lcdRect(12, HUD_Y + 5, 8, 1, false);
  const n = Math.round(Math.min(1, v) * 8);
  if (n) lcdRect(12, HUD_Y + 3, n, 2, false);
  const mega = Math.round(Math.max(0, v - 1) * 8);
  if (mega && (v >= 1.95 || S.tick % 2)) {
    lcdRect(12, HUD_Y + 1, mega, 1, false);
    lcdRect(12, HUD_Y + 6, mega, 1, false);
  }
}

function chargeValue(now = performance.now()) {
  return F.hold ? Math.min(CHARGE_MAX, (now - F.hold.start) / CHARGE_MS) : 0;
}

// Zeitfenster fürs Ausweichen: 350 ms + 25 ms pro Punkt Tempo-Training
function dodgeWindow() {
  const pet = S.state && S.state.pet;
  return 350 + 25 * numOr(pet && pet.skills && pet.skills.speed, 0);
}

// Display wackelt (Treffer mit 2 Schaden)
function shakeLcd() {
  lcd.classList.remove("shake");
  void lcd.offsetWidth;                  // Animation neu starten
  lcd.classList.add("shake");
}
lcd.addEventListener("animationend", () => lcd.classList.remove("shake"));

// Meldung, die bis zum nächsten Schuss stehen bleiben darf (Hinweise werden angehängt)
function say(text) {
  F.note = text;
  setMessage(text);
}

// setTimeout, der nichts mehr tut, wenn inzwischen ein anderer Kampf läuft
function later(ms, fn) {
  const token = F.token;
  setTimeout(() => { if (token === F.token) fn(); }, ms);
}

// Neuer Kampf (oder nach Neuladen): alles Alte verwerfen
function resetFight() {
  F.token++;
  Object.assign(F, { steps: [], step: null, hold: null, mash: null, pending: null, dodged: [], incoming: [],
    hints: 0, note: "", result: null, locked: 0 });
}

function personalityOf(b) {
  const p = b.personality;
  const key = p && typeof p === "object" ? p.key : p;
  if (!key) return null;
  return { key, name: (p && typeof p === "object" && p.name) || b.personality_name || PERSONALITY[key] || key };
}

function startBattleView(battle) {
  resetFight();
  F.pvp = false;
  F.opp = battle.dex;
  F.oppMon = battle.name || "";
  F.myHp = numOr(battle.my_hp, 3);
  F.oppHp = numOr(battle.opp_hp, 3);
  F.myMax = numOr(battle.my_max, 3);
  F.oppMax = numOr(battle.opp_max, 3);
  F.myGauge = numOr(battle.my_gauge, 0);
  F.oppGauge = numOr(battle.opp_gauge, 0);
  F.specialName = battle.special_name || tr("Spezialattacke");
  F.oppSpecialName = battle.opp_special_name || tr("Spezialattacke");
  F.personality = personalityOf(battle);
  F.phase = "aim";
}

// „Es wirkt aggressiv.“ – nur, wenn der Server es nicht schon geschrieben hat
function personalityText(message) {
  const p = F.personality;
  return p && !String(message).includes(p.name) ? " " + tr("Es wirkt {p}.", { p: p.name }) : "";
}

function renderBattle(pet) {
  const now = performance.now();
  const s = F.step || {};
  const ms = now - F.t0;
  const p = s.dur ? Math.min(1, ms / s.dur) : 0;          // Fortschritt des Schritts 0..1
  const t = S.tick - F.start;
  const blink = n => Math.floor(S.tick / n) % 2 === 1;
  const me = (kind, dy = 0) => lcdPixels(sprite(pet.dex, kind, Math.floor(S.tick / 5)), 0, dy, true, false);
  const foe = (kind, dy = 0) => lcdPixels(sprite(F.opp, kind, Math.floor(S.tick / 6)), 16, dy, false, false);
  const ball = (big, x, y) => lcdPixels(big ? BIG_BALL : BALL, x, y, false, false);
  renderFightScene(pet, s, now, ms, p, t, blink, me, foe, ball);
  // oben: deine Leben | Ladeleiste | Leben des Gegners, darunter die Spezial-Leisten
  // (nach den Sprites und auf frei geräumter Fläche, damit ein springendes Digimon sie nicht verdeckt)
  lcdErase(0, HUD_Y + 3, 12, 4);
  lcdErase(20, HUD_Y + 3, 12, 4);
  hpPips(0, F.myHp, F.myMax);
  hpPips(32 - F.oppMax * 3 + 1, F.oppHp, F.oppMax);
  gaugeDots(0, F.myGauge);
  gaugeDots(32 - SPECIAL_MAX * 3 + 1, F.oppGauge);
}

function renderFightScene(pet, s, now, ms, p, t, blink, me, foe, ball) {
  switch (F.phase) {
    case "aim":
      chargeBar(0);
      me("idle");
      return;
    case "charge": {
      // der Ball schwebt in der gewählten Höhe – überladen blinkt er (Risiko!)
      const v = chargeValue(now);
      const big = v >= 0.85;
      chargeBar(v);
      me(v >= 1 ? "attack" : "idle");
      if (v <= 1 || v >= 1.95 || blink(1)) ball(big, 17, ballY(F.hold ? F.hold.side : "high", big));
      return;
    }
    case "special": {
      // Spezialattacke: Leiste = Drücker, darunter läuft die Zeit ab
      const m = F.mash || { presses: 0, start: now };
      chargeBar(Math.min(1, m.presses / MASH_GOAL));
      lcdRect(12, HUD_Y + 7, Math.max(0, Math.round(8 * (1 - (now - m.start) / MASH_MS))), 1, false);
      me(m.presses % 2 ? "attack" : "happy");
      ball(true, 18, 5);
      if (m.presses % 2) [[17, 0], [24, 1], [23, 11]].forEach(([x, y]) => lcdPixels(SPARK, x, y, false, false));
      return;
    }
    case "wait":
      chargeBar(F.locked || 0);
      me("idle");
      return;
    case "myShot":
      if (s.interrupted) {
        // beim Aufladen unterbrochen: kein Schuss, es taumelt
        if (t % 4 < 3) me("tired");
        if (blink(2)) lcdPixels(ANGER, 18, 2, false, false);
        return;
      }
      me("attack");
      ball(s.big, 15 + Math.round(p * 17), ballY(s.aim, s.big));
      return;
    case "oppImpact": {
      const by = ballY(s.aim, s.big);
      const hurt = s.hit && p >= 0.5;
      // ausgewichen: der Gegner springt über einen tiefen Ball bzw. duckt sich unter einem hohen
      const dy = s.dodged && p > 0.15 ? (s.aim === "low" ? JUMP : DUCK) : 0;
      if (!(hurt && blink(1))) foe(hurt ? "tired" : "idle", dy);
      // gedeckte Seite: Schild vor dem Gegner
      if (s.guard && !s.special) lcdRect(14, s.guard === "low" ? 8 : 0, 1, 8, false);
      const stop = s.big ? 9 : 11;                                   // hier prallt er am Schild ab
      if (s.hit) { if (p < 0.5) ball(s.big, -3 + Math.round(p * 2 * 17), by); }
      else if (s.blocked) ball(s.big, p < 0.5 ? -3 + Math.round(p * 2 * (stop + 3)) : stop - Math.round((p - 0.5) * 2 * (stop + 3)), by);
      else if (s.dodged) ball(s.big, -3 + Math.round(p * 36), by);                 // fliegt vorbei
      else ball(s.big, -3 + Math.round(p * 36), by - Math.round(p * 8));          // daneben: fliegt drüber weg
      return;
    }
    case "oppWarn":
      // starker Angriff kündigt sich an: Gegner blinkt, „!“ oben
      if (t % 4 < 2) foe("attack");
      if (blink(2)) lcdPixels(ICONS.call, 12, HUD_Y, false, false);
      return;
    case "oppShot":
      foe("attack");
      ball(s.big, 14 - Math.round(p * 17), ballY(s.inc.side, s.big));
      return;
    case "dodge": {
      // der Gegenangriff fliegt auf dich zu – springen oder ducken
      const by = ballY(s.inc.side, s.big);
      const pose = s.move && (s.ok || now - s.moveAt < 450) ? (s.move === "jump" ? JUMP : DUCK) : 0;
      me(s.inc.special && ms > DODGE_FLIGHT - 300 ? "tired" : "idle", pose);
      if (ms < DODGE_FLIGHT) ball(s.big, 32 - Math.round(ms / DODGE_FLIGHT * 17), by);      // 32 -> 15 = Einschlag
      else if (s.ok) ball(s.big, 15 - Math.round((ms - DODGE_FLIGHT) / DODGE_PASS * 20), by);
      else ball(s.big, 15, by);
      return;
    }
    case "dodgeWait":
      me("idle");
      if (F.pending) ball(F.pending.big, 15, F.pending.y);
      return;
    case "myImpact": {
      const by = ballY(s.inc.side, s.big);
      const hurt = s.hit && p >= 0.5;
      if (!(hurt && blink(1))) me(hurt ? "tired" : "idle");
      if (s.hit) { if (p < 0.5) ball(s.big, s.from - Math.round(p * 2 * (s.from - 12)), by); }
      else ball(s.big, s.from - Math.round(p * (s.from + 5)), by - Math.round(p * 8));   // daneben: fliegt drüber weg
      return;
    }
    case "end": {
      const won = F.result && F.result.won;
      lcdPixels(sprite(pet.dex, won ? "happy" : "tired", Math.floor(t / 5)), won ? 8 : 0, 0, false, false);
      if (!won) foe("happy");
      return;
    }
    default:
      me("idle");
  }
}

// ---- Ablauf einer Runde als Warteschlange von Schritten
// Schritt mit `phase` + `dur` (ms) = Animation; mit `phase` ohne `dur` = warten, bis
// jemand runSteps() aufruft; ohne `phase` = Sofort-Aktion (`run`).
function runSteps(list) {
  F.steps = list;
  nextStep();
}

function nextStep() {
  for (;;) {
    const s = F.steps.shift();
    F.step = s || null;
    if (!s) return;
    if (!s.phase) {
      s.run();
      if (F.step !== s) return;         // die Aktion hat selbst etwas Neues gestartet
      continue;
    }
    F.phase = s.phase;
    F.t0 = performance.now();
    F.start = S.tick;
    if (s.run) s.run(s);
    renderKeys();
    return;
  }
}

// eigener Schuss fliegt los (oder fällt aus, wenn das Aufladen unterbrochen wurde)
function myShotStep(a) {
  return { ...a, phase: "myShot", dur: STEP_MS, run: () => {
    F.note = "";
    if (a.interrupted) {
      sfx("cancel");
      return say(tr("{name} wurde beim Aufladen unterbrochen!", { name: myName() }));
    }
    sfx(a.special || a.mega || a.power ? "strongAttack" : "attack");
    setMessage(a.special ? F.specialName + "!" : a.mega ? tr("MEGA-SCHUSS!") : a.power ? tr("POWER-SCHUSS!") : tr("Schuss!"));
  } };
}

// dein Schuss kommt beim Gegner an: Treffer, gedeckt, ausgewichen oder daneben
function oppImpactStep(a) {
  return { ...a, phase: "oppImpact", dur: STEP_MS,
    run: () => later(STEP_MS / 2, () => {
      const text = [];
      if (a.guard && !a.special) text.push(a.gap ? tr("Lücke!") : tr("Gedeckt!"));
      if (a.dodged) text.push(tr("{name} ist ausgewichen!", { name: F.oppMon }));
      else text.push(!a.hit ? tr("Daneben!") : a.dmg >= 2 ? tr("Volltreffer – 2 Schaden!") : tr("Treffer!"));
      say(text.join(" "));
      if (a.hit) {
        sfx(a.dmg >= 2 || a.power ? "strongHit" : "attackHit");
        if (a.dmg >= 2) shakeLcd();
      }
    }),
    done: () => { F.oppHp = Math.max(0, numOr(a.hp, F.oppHp - (a.hit ? a.dmg : 0))); } };
}

// starker Angriff: vorher ankündigen
function warnStep(inc) {
  return { phase: "oppWarn", dur: WARN_MS, inc, run: () => {
    sfx("alarm");
    setMessage((F.note ? F.note + " " : "") + tr("Starker Angriff – weich aus!"));
  } };
}

const bigAttack = inc => !!(inc.special || inc.strong || inc.power || inc.mega);

// der Gegner schießt (sein Ball verlässt das Display nach links)
function oppShotStep(inc, i) {
  return { phase: "oppShot", dur: STEP_MS, inc, big: bigAttack(inc), run: () => {
    sfx(bigAttack(inc) ? "strongAttack" : "attack");
    const lead = F.note ? F.note + " " : "";
    if (inc.special) setMessage(lead + tr("SPEZIAL") + " – " + tr("{name}! Dem kann man nicht ausweichen!", { name: F.oppSpecialName }));
    else if (inc.strong) return;                                   // „Starker Angriff“ steht schon da
    else if (F.hints < 2) setMessage(lead + tr("Weich aus! Ball unten = ↑ springen, Ball oben = ↓ ducken."));
    else if (i > 0) setMessage(lead + tr("Noch ein Angriff!"));
    F.hints = (F.hints || 0) + 1;
  } };
}

// der Ball fliegt auf dich zu – das Ausweichen beurteilt dodgeInput()
function dodgeStep(inc, i) {
  const big = bigAttack(inc);
  return { phase: "dodge", dur: DODGE_FLIGHT + DODGE_PASS, inc, i, big,
    done: s => { if (!s.ok) F.pending = { big, y: ballY(inc.side, big) }; } };
}

// Ergebnis eines Gegenangriffs, der nicht ausgewichen wurde
function myImpactStep(a) {
  return { ...a, phase: "myImpact", dur: STEP_MS,
    run: () => {
      F.pending = null;
      later(STEP_MS / 2, () => {
        say(!a.hit ? tr("Daneben – Glück gehabt!") : a.dmg >= 2 ? tr("Autsch – 2 Schaden!") : tr("Getroffen!"));
        if (a.hit) {
          sfx(a.dmg >= 2 ? "strongHit" : "attackHit");
          if (a.dmg >= 2) shakeLcd();
        }
      });
    },
    done: () => { F.myHp = Math.max(0, numOr(a.hp, F.myHp)); } };
}

function setGauges(r) {
  F.myGauge = Math.min(SPECIAL_MAX, numOr(r.my_gauge, F.myGauge));
  F.oppGauge = Math.min(SPECIAL_MAX, numOr(r.opp_gauge, F.oppGauge));
  renderKeys();
}

function endBattle(won, draw, message) {
  F.phase = "end";
  F.start = S.tick;
  F.t0 = performance.now();
  F.result = { won: !!won, draw: !!draw };
  F.hold = F.mash = null;
  sfx(won ? "win" : draw ? "cancel" : "lose");
  setMessage(message || "");
  renderKeys();
  later(2600, () => {
    // Kampf ganz abschließen – sonst hält ein alter Zustand den nächsten Kampf auf
    F.pvp = false;
    F.phase = "idle";
    F.steps = [];
    F.step = null;
    if (S.mode === "battle" || S.mode === "duel") setMode("main");
  });
}

// Kampf gegen ein wildes Digimon: "Runde 5 von 12" – kurz vor Schluss mit Warnung,
// denn nach der letzten Runde entscheiden die Leben (gleich viele = unentschieden)
function wildRoundText() {
  const b = S.state && S.state.pet && S.state.pet.battle;
  if (!b || !b.max_rounds) return tr("Nächste Runde! Lade deinen Schuss.");
  const n = Math.min(b.round + 1, b.max_rounds), left = b.max_rounds - n;
  const text = tr("Runde {n} von {max}! Lade deinen Schuss.", { n, max: b.max_rounds });
  if (left === 0) return text + " " + tr("Letzte Runde – danach gewinnt, wer mehr Leben hat!");
  if (left <= 2) return text + " " + tr("Nur noch {n} Runden – danach gewinnt, wer mehr Leben hat.", { n: left + 1 });
  return text;
}

function nextRound() {
  F.phase = "aim";
  F.hold = F.mash = F.pending = null;
  const ready = F.myGauge >= SPECIAL_MAX ? tr(" Spezial-Leiste voll – drück E!") : "";
  setMessage((F.pvp ? tr("Runde {n}! Lade deinen Schuss – {name} lädt auch.", { n: F.seen + 1, name: F.oppName })
    : wildRoundText()) + ready);
  renderKeys();
  if (F.pvp) later(0, () => syncDuel(S.state));      // vielleicht liegt die nächste Runde schon bereit
}

// ---- Bedienung: ↑/↓ halten = laden, loslassen = Schuss; beim Gegenangriff springen/ducken.
// src = wer hält (Taste, Knopf, Display) – nur derselbe lässt wieder los.
function holdStart(side, src, dodgeOk = true) {
  if (S.mode !== "battle" && S.mode !== "duel") return;
  if (F.phase === "special") return mashPress();
  if (F.phase === "dodge") {
    if (dodgeOk) dodgeInput(side === "low" ? "duck" : "jump");
    return;
  }
  if (F.phase !== "aim" || F.hold) return;
  F.hold = { side, src, start: performance.now(), full: false };
  F.phase = "charge";
}

function holdEnd(src) {
  if (F.hold && (!src || F.hold.src === src)) fire();
}

function fire() {
  const h = F.hold;
  F.hold = null;
  if (!h || F.phase !== "charge") return;
  const charge = Math.min(CHARGE_MAX, (performance.now() - h.start) / CHARGE_MS);
  F.locked = charge;
  const body = { aim: h.side, charge: Math.floor(charge * 100) / 100 };
  if (F.pvp) duelShoot(body);
  else shoot(body);
}

// Ausweichen: richtige Richtung im Zeitfenster kurz vor dem Einschlag
function dodgeInput(move) {
  const s = F.step;
  if (F.phase !== "dodge" || !s || s.tried || s.inc.special) return;     // Spezialattacke: zwecklos
  const now = performance.now();
  const left = F.t0 + DODGE_FLIGHT - now;                               // ms bis zum Einschlag
  const need = s.inc.side === "low" ? "jump" : "duck";
  Object.assign(s, { tried: true, move, moveAt: now });
  s.ok = move === need && left >= 0 && left <= dodgeWindow();
  F.dodged[s.i] = s.ok;
  sfx(s.ok ? "trainhit" : "cancel");
  setMessage(s.ok ? tr("Ausgewichen!")
    : move !== need ? (need === "duck" ? tr("Falsch! Ball oben = ↓ ducken.") : tr("Falsch! Ball unten = ↑ springen."))
    : left > 0 ? tr("Zu früh!") : tr("Zu spät!"));
}

// Taste E / Knopf „Spezial“: startet die Spezialattacke (Leiste voll) oder zählt als Drücker
function specialKey() {
  if (S.mode !== "battle" && S.mode !== "duel") return;
  if (F.phase === "special") return mashPress();
  if (F.phase !== "aim") return;
  if (F.myGauge < SPECIAL_MAX) {
    sfx("refuse");
    return setMessage(tr("Die Spezial-Leiste ist noch nicht voll ({n}/{max}). Sie füllt sich bei jedem Treffer.",
      { n: F.myGauge, max: SPECIAL_MAX }));
  }
  F.phase = "special";
  F.mash = { start: performance.now(), presses: 0 };
  sfx("strongAttack");
  setMessage(tr("{name}! Jetzt so schnell wie möglich drücken!", { name: F.specialName }));
  renderKeys();
}

function mashPress() {
  if (F.phase !== "special" || !F.mash) return;
  F.mash.presses++;
  if (F.mash.presses % 2 === 0) sfx("click");
}

function finishMash() {
  const mash = Math.min(1, F.mash.presses / MASH_GOAL);
  F.mash = null;
  F.locked = mash;
  const body = { special: true, mash: Math.round(mash * 100) / 100 };
  if (F.pvp) duelShoot(body);
  else shoot(body);
}

// Fenster verliert den Fokus o. Ä.: nichts darf „hängen“ bleiben
function releaseAll() { holdEnd(); }
window.addEventListener("blur", releaseAll);
document.addEventListener("visibilitychange", () => { if (document.hidden) releaseAll(); });
["pointerup", "pointercancel"].forEach(type => window.addEventListener(type, () => { holdEnd("lcd"); holdEnd("btn"); }));

// Tastatur im Kampf: ↑/W, ↓/S halten, Leertaste = oben laden, E = Spezial
const FIGHT_KEYS = { arrowup: "up", w: "up", arrowdown: "down", s: "down", " ": "space", e: "special" };

function fightKey(k) {
  if (k === "up") holdStart("high", "kb-up");
  else if (k === "down") holdStart("low", "kb-down");
  else if (k === "space") holdStart("high", "kb-space", false);     // Leertaste weicht nicht aus
  else specialKey();
}

document.addEventListener("keyup", e => {
  const k = FIGHT_KEYS[(e.key || "").toLowerCase()];
  if (!k) return;
  // Leertaste soll im Kampf keinen gerade fokussierten Knopf (z. B. „Aufgeben“) auslösen
  if ((S.mode === "battle" || S.mode === "duel") && !(e.target.closest && e.target.closest("input"))) e.preventDefault();
  if (k !== "special") holdEnd("kb-" + k);
});

// Während Bälle fliegen oder geladen wird, öfter zeichnen (flüssiger, genaueres Ausweichen)
const FAST_PHASES = ["charge", "special", "myShot", "oppImpact", "oppShot", "dodge", "myImpact"];
function fastFrame() {
  if ((S.mode === "battle" || S.mode === "duel") && FAST_PHASES.includes(F.phase)) render();
  requestAnimationFrame(fastFrame);
}

// ------------------------------------------------------------ Kampf gegen Freunde
// Beide laden gleichzeitig und schießen (Phase "aim"). Sind beide Schüsse da, fliegen
// sie los (Phase "dodge"): jeder sieht seinen eigenen Ball und weicht dem des anderen
// aus. Danach wertet der Server die Runde aus; wir zeigen die Treffer.
const DUEL_MODES = ["duelwait", "challenged", "duel"];
const FAST_POLL_MODES = [...DUEL_MODES, "jogwait", "jogask"];     // hier öfter beim Server nachfragen
let lastChallengeId = null;

// Nummer der laufenden Runde (damit dieselbe Ausweich-Phase nicht zweimal startet)
const duelRoundKey = d => numOr(d.round, (d.rounds || []).length);

function startDuelView(d) {
  resetFight();
  F.pvp = true;
  F.opp = d.opp_pet ? d.opp_pet.dex : null;
  F.oppName = d.opponent;
  F.oppMon = d.opp_pet ? d.opp_pet.name : d.opponent;
  F.myHp = numOr(d.my_hp, 3); F.oppHp = numOr(d.opp_hp, 3);
  F.myMax = numOr(d.my_max, 3); F.oppMax = numOr(d.opp_max, 3);
  F.myGauge = numOr(d.my_gauge, 0); F.oppGauge = numOr(d.opp_gauge, 0);
  F.specialName = d.special_name || tr("Spezialattacke");
  F.oppSpecialName = d.opp_special_name || tr("Spezialattacke");
  F.personality = null;
  F.seen = (d.rounds || []).length;
  F.dodgeFor = null;
  F.phase = d.i_shot ? "wait" : "aim";     // nach Neuladen: schon geschossen? dann warten
  F.locked = 1;
  F.t0 = performance.now();
  if (d.phase === "dodge" && d.i_dodged) {
    // nach Neuladen: schon ausgewichen -> auf die Auswertung warten
    F.phase = "dodgeWait";
    F.dodgeFor = duelRoundKey(d);
  }
}

// Wird bei jedem neuen Stand vom Server aufgerufen
function syncDuel(state) {
  const d = state && state.duel;
  // gerade läuft noch eine Kampf-Animation gegen einen Freund
  const busy = S.mode === "duel" && F.pvp && FIGHT_ANIM.includes(F.phase);
  if (!d) {
    if (DUEL_MODES.includes(S.mode) && !busy) setMode("main");
    return;
  }
  if (d.status === "pending") {
    const mode = d.challenger ? "duelwait" : "challenged";
    if (S.mode !== mode && !["battle", "train", "scout"].includes(S.mode)) {
      setMode(mode);
      if (mode === "challenged" && lastChallengeId !== d.id) {
        lastChallengeId = d.id;
        sfx("alarm");
        notify(tr("{name} fordert dich heraus!", { name: d.opponent }), tr("Öffne das Spiel, um den Kampf anzunehmen."), "duel");
      }
    }
    if (S.mode === mode) {             // nicht mitten ins Training o. Ä. reinschreiben
      setMessage(d.challenger
        ? tr("Warte auf {name} ... (läuft ab in {s} s)", { name: d.opponent, s: d.expires_in })
        : d.opp_pet
          ? tr("{name} fordert dich heraus mit {mon} ({stage})! Kämpfen kostet 1 Herz Hunger + 1 Kraft. ({s} s)",
            { name: d.opponent, mon: d.opp_pet.name, stage: d.opp_pet.stage_de, s: d.expires_in })
          : tr("{name} fordert dich heraus! Kämpfen kostet 1 Herz Hunger + 1 Kraft. ({s} s)",
            { name: d.opponent, s: d.expires_in }));
    }
    return;
  }
  if (d.status === "active" && S.mode !== "duel" && !busy) {
    startDuelView(d);
    setMode("duel");
    sfx("startBattle");
    setMessage(tr("Kampf gegen {name}! Lade deinen Schuss – {name} lädt auch.", { name: d.opponent })
      + tr(" Halte ↑ oder ↓ zum Laden, loslassen = Schuss."));
  }
  const rounds = d.rounds || [];
  if (S.mode === "duel" && rounds.length > F.seen && ["aim", "charge", "special", "wait", "dodgeWait"].includes(F.phase)) {
    // neue Runde ausgewertet -> animieren (nach dem Ausweichen nur noch die Einschläge)
    const full = F.phase !== "dodgeWait";
    F.hold = F.mash = null;
    const r = rounds[F.seen];
    F.seen++;
    playDuelRound(d, r || {}, full);
    return;
  }
  if (S.mode === "duel" && d.status === "active" && d.phase === "dodge"
      && ["aim", "charge", "special", "wait"].includes(F.phase) && duelRoundKey(d) !== F.dodgeFor) {
    // beide haben geschossen: die Bälle fliegen – ausweichen!
    startDuelDodge(d);
    return;
  }
  if (d.status !== "active" && d.status !== "pending" && d.result && !busy && S.mode !== "main"
      && DUEL_MODES.includes(S.mode) && !(rounds.length > F.seen)) {
    // abgelehnt, abgelaufen, aufgegeben ...
    setMessage(d.result.text);
    setMode("main");
  }
  if (S.mode === "duel" && F.phase === "wait") {
    setMessage(d.they_shot ? tr("Gleich geht's los ...") : tr("Warte auf {name} ... ({s} s)", { name: d.opponent, s: d.time_left }));
  }
  if (S.mode === "duel" && F.phase === "aim" && d.status === "active" && d.phase !== "dodge"
      && !d.i_shot && numOr(d.time_left, 99) <= 10) {
    // wer zögert, sieht, wann sein Digimon von selbst (schwach) schießt
    setMessage(tr("Noch {s} s – dann schießt {name} von selbst, aber schwach!", { s: d.time_left, name: (S.state.pet && S.state.pet.name) || "Digimon" }));
  }
  if (S.mode === "duel" && F.phase === "dodgeWait" && performance.now() - F.t0 > 1500) {
    setMessage(tr("Warte auf {name} ... ({s} s)", { name: d.opponent, s: numOr(d.time_left, 0) }));
  }
}

// Ausweich-Phase: mein Ball fliegt in meiner Höhe los, seiner in seiner Höhe auf mich zu
function startDuelDodge(d) {
  F.dodgeFor = duelRoundKey(d);
  F.hold = F.mash = null;
  const mine = d.my_attack || {};
  const a = { aim: mine.aim === "low" ? "low" : "high", special: !!mine.special, mega: !!mine.mega,
    power: !!mine.power, interrupted: !!mine.interrupted };
  a.big = a.special || a.mega || a.power;
  const steps = [myShotStep(a)];
  const inc = d.incoming;
  if (inc && inc.side && !inc.interrupted) {
    const i = { side: inc.side === "low" ? "low" : "high", special: !!inc.special, strong: false,
      power: !!inc.power, mega: !!inc.mega };
    F.incoming = [i];
    F.dodged = [false];
    // Spezialattacke: nicht ausweichbar, der Server zählt mich dann schon als fertig
    steps.push(oppShotStep(i, 0), dodgeStep(i, 0),
      { phase: "dodgeWait", run: i.special ? () => later(0, () => syncDuel(S.state)) : sendDuelDodge });
  } else {
    // auf mich fliegt nichts (sein Aufladen wurde unterbrochen) -> gleich auf die Auswertung warten
    F.incoming = [];
    F.dodged = [];
    steps.push({ phase: "dodgeWait", run: () => {
      if (inc && inc.interrupted) say(tr("{name} wurde beim Aufladen unterbrochen!", { name: F.oppMon }));
      later(0, () => syncDuel(S.state));
    } });
  }
  runSteps(steps);
}

async function sendDuelDodge() {
  const token = F.token;
  try {
    const res = await api("/api/duel/dodge", { dodged: !!F.dodged[0] });
    if (token === F.token) apply(res);
  } catch { /* z. B. Runde schon ausgewertet – dann einfach auf das Ergebnis warten */ }
  if (token === F.token && S.state) syncDuel(S.state);
}

// eine ausgewertete Runde zeigen. full = auch die Schüsse (wenn wir die Ausweich-Phase verpasst haben)
function playDuelRound(d, r, full) {
  const rounds = d.rounds || [];
  const last = F.seen === rounds.length && d.status !== "active";
  F.message = d.result ? d.result.text : "";
  const myAim = r.my_aim === "low" ? "low" : "high", oppAim = r.opp_aim === "low" ? "low" : "high";
  const a = { aim: myAim, special: !!r.my_special, mega: !!r.my_mega, power: !!r.power_shot,
    interrupted: !!r.my_interrupted };
  a.big = a.special || a.mega || a.power;
  const inc = { side: oppAim, special: !!r.opp_special, strong: false, power: !!r.opp_power, mega: !!r.opp_mega };
  const steps = [];
  if (full) steps.push(myShotStep(a));
  if (!a.interrupted) {
    steps.push(oppImpactStep({ ...a, hit: !!r.my_hit, dodged: !!r.they_dodged && !a.special,
      dmg: numOr(r.my_damage, r.my_hit ? 1 : 0), hp: r.opp_hp }));
  }
  if (!r.opp_interrupted) {
    if (full) steps.push(oppShotStep(inc, 0));
    // schon ausgewichen? Dann ist der Ball längst vorbei
    if (full || !r.i_dodged || inc.special) {
      steps.push(myImpactStep({ inc, big: bigAttack(inc), hit: !!r.opp_hit,
        dmg: numOr(r.opp_damage, r.opp_hit ? 1 : 0), hp: r.my_hp, from: full ? 32 : 15 }));
    }
  }
  steps.push({ run: () => {
    setGauges({ my_gauge: numOr(r.my_gauge, d.my_gauge), opp_gauge: numOr(r.opp_gauge, d.opp_gauge) });
    F.myHp = Math.max(0, numOr(r.my_hp, F.myHp));
    F.oppHp = Math.max(0, numOr(r.opp_hp, F.oppHp));
    if (last) endBattle(d.result && d.result.won, d.result && d.result.draw, F.message);
    else nextRound();
  } });
  runSteps(steps);
}

async function duelStep(step, body = {}) {
  try {
    const res = await api(`/api/duel/${step}`, body);
    apply(res);
    // Annehmen: syncDuel (über apply) hat schon die Kampf-Meldung mit Bedienhilfe gesetzt
    if (res.message && !(step === "answer" && S.mode === "duel")) setMessage(res.message);
    return res;
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
    return null;
  }
}

async function duelShoot(body) {
  F.phase = "wait";
  renderKeys();
  sfx("click");
  const token = F.token;
  const res = await duelStep("shoot", body);
  if (!res && token === F.token && F.phase === "wait") F.phase = "aim";
}

// ------------------------------------------------------------ Jogress
let lastJogressId = null;

async function jogressStep(step, body) {
  try {
    const res = await api(`/api/jogress/${step}`, body);
    S.mode = "main";
    S.anim = null;
    apply(res);
    if (res.message) setMessage(res.message);
    if (step !== "ask") sfx(body.accept === false ? "cancel" : "evolve");
    renderKeys();
    return res;
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
    return null;
  }
}

// Jogress-Anfragen von/an Freunde mitverfolgen
function syncJogress(state) {
  const j = state.jogress;
  if (!j) {
    if (["jogwait", "jogask"].includes(S.mode)) setMode("main");
    return;
  }
  if (j.status === "pending" && j.incoming) {
    if (S.mode !== "jogask" && S.mode === "main") {
      setMode("jogask");
      if (lastJogressId !== j.id) {
        lastJogressId = j.id;
        sfx("alarm");
        notify(tr("{name} möchte eine Jogress!", { name: j.partner }), tr("Mit deinem Digimon zu {to}.", { to: j.to }), "jogress");
      }
    }
    if (S.mode === "jogask") {
      setMessage(tr("{name} möchte mit deinem Digimon fusionieren – zu {to}! Dein Digimon bleibt, wie es ist. ({s} s)",
        { name: j.partner, to: j.to, s: j.expires_in }));
    }
  } else if (j.status === "pending" && S.mode === "jogwait") {
    setMessage(tr("Warte auf {name} ... ({s} s)", { name: j.partner, s: j.expires_in }));
  } else if (j.status !== "pending" && ["jogwait", "jogask"].includes(S.mode)) {
    setMode("main");
    setMessage(j.status === "done" ? (j.result || tr("Jogress geschafft!"))
      : j.status === "declined" ? tr("{name} hat abgelehnt.", { name: j.partner })
      : tr("Die Fusion hat nicht geklappt – ein Digimon wurde inzwischen getauscht."));
  }
}

async function showFriends() {
  try {
    S.players = (await api("/api/players")).players;
    setMode("friends");
    setMessage(S.players.length ? tr("Wen möchtest du herausfordern? (nur wer online ist)")
      : tr("Noch keine Freunde – tauscht eure Freundescodes aus (Einstellungen → Freunde)."));
  } catch (e) { setMessage(e.message); }
}

function tickBattle() {
  if (S.mode !== "battle" && S.mode !== "duel") return;
  const now = performance.now();
  if (F.phase === "charge" && F.hold) {
    const v = chargeValue(now);
    if (v >= 1 && !F.hold.full) {
      F.hold.full = true;
      sfx("menu");
      setMessage(tr("Voll geladen! Weiter halten = MEGA – aber es kann dich unterbrechen."));
    }
    if (v >= CHARGE_MAX) fire();                     // MEGA voll: Schuss geht von selbst los
  }
  if (F.phase === "special" && F.mash && now - F.mash.start >= MASH_MS) finishMash();
  const s = F.step;
  if (s && s.phase && s.dur && now - F.t0 >= s.dur) {
    if (s.done) s.done(s);
    nextStep();
  }
}

async function battleStep(step, body = {}) {
  try {
    const res = await api(`/api/battle/${step}`, body);
    apply(res);
    return res;
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
    if (step !== "shot") setMode("main");
    return null;
  }
}

async function scoutBattle() {
  const res = await battleStep("scout");
  if (!res) return;
  setMode("scout");
  sfx("menu");
  reply(res);
}

async function startFight() {
  const res = await battleStep("fight");
  if (!res) return;
  if (!res.pet || !res.pet.battle) return setMode("main");
  startBattleView(res.pet.battle);
  setMode("battle");
  sfx("startBattle");
  setMessage(res.message + personalityText(res.message) + tr(" Halte ↑ oder ↓ zum Laden, loslassen = Schuss.")
    + " " + tr("Höchstens {n} Runden.", { n: res.pet.battle.max_rounds || 25 }));
}

// Schuss gegen ein wildes Digimon: {aim, charge} oder {special, mash}
async function shoot(body) {
  F.phase = "wait";
  renderKeys();
  const token = F.token;
  const res = await battleStep("shot", body);
  if (token !== F.token) return;
  if (!res) {
    F.phase = "aim";
    renderKeys();
    return;
  }
  playShot(res.round || {}, res.message || "", body);
}

// Antwort auf den Schuss zeigen: dein Ball, Einschlag beim Gegner, dann sein Gegenangriff
function playShot(r, message, body) {
  const aim = r.aim === "low" || r.aim === "high" ? r.aim : body.aim === "low" ? "low" : "high";
  const special = !!(r.special || body.special);
  const mega = !!r.mega;
  const hit = !!r.my_hit;
  const a = { aim, special, mega, power: !!r.power_shot, interrupted: !!r.interrupted };
  a.big = special || mega || a.power;
  const steps = [];
  const late = r.late;
  if (late && late.opp_hits && late.opp_hits.some(Boolean)) {
    // ein offener Angriff von vorhin (Seite neu geladen) hat noch getroffen
    const dmg = numOr(late.damage_taken, 1);
    steps.push(myImpactStep({ inc: { side: "high" }, big: dmg >= 2, hit: true, dmg,
      hp: Math.max(0, F.myHp - dmg), from: 32 }));
  }
  if (r.over && !r.aim) {
    // der Kampf war schon dadurch vorbei – dein Schuss kam nicht mehr dazu
    steps.push({ run: () => { setGauges(r); endBattle(r.won, r.draw, message || r.message); } });
    return runSteps(steps);
  }
  steps.push(myShotStep(a));
  if (!a.interrupted) {
    steps.push(oppImpactStep({ ...a, hit, dmg: numOr(r.damage, hit ? (mega || special ? 2 : 1) : 0),
      guard: r.guard, gap: !!r.gap, blocked: !hit && !special && r.guard === aim, hp: r.opp_hp }));
  }
  steps.push({ run: () => setGauges(r) });
  const incoming = Array.isArray(r.incoming) ? r.incoming : [];
  if (r.over) steps.push({ run: () => endBattle(r.won, r.draw, message || r.message) });
  else if (incoming.length) steps.push(...attackSteps(incoming));
  else steps.push({ run: nextRound });
  runSteps(steps);
}

// Gegenangriff(e) dieser Runde: ankündigen, heranfliegen, ausweichen – dann dem Server melden
function attackSteps(list) {
  F.incoming = list.map(inc => ({ side: inc && inc.side === "low" ? "low" : "high",
    strong: !!(inc && inc.strong), special: !!(inc && inc.special) }));
  F.dodged = F.incoming.map(() => false);
  F.pending = null;
  const steps = [];
  F.incoming.forEach((inc, i) => {
    if (inc.strong && !inc.special) steps.push(warnStep(inc));
    steps.push(oppShotStep(inc, i), dodgeStep(inc, i));
  });
  steps.push({ phase: "dodgeWait", run: sendDodge });
  return steps;
}

async function sendDodge() {
  const token = F.token;
  const res = await battleStep("dodge", { dodged: F.dodged.slice() });
  if (token !== F.token) return;
  if (!res) {
    // battleStep ist schon im Hauptmenü – gleich neu laden, dann geht der Kampf weiter
    refresh();
    return;
  }
  const r = res.round || {};
  const hits = Array.isArray(r.opp_hits) ? r.opp_hits : [];
  const dodged = Array.isArray(r.dodged) ? r.dodged : F.dodged;
  let hp = F.myHp;
  const steps = [];
  F.incoming.forEach((inc, i) => {
    if (dodged[i] && !inc.special) return;                 // ist schon vorbeigeflogen
    const hit = !!hits[i];
    const dmg = hit ? (inc.strong || inc.special ? 2 : 1) : 0;
    hp = Math.max(0, hp - dmg);
    steps.push(myImpactStep({ inc, big: bigAttack(inc), hit, dmg, hp, from: 15 }));
  });
  steps.push({ run: () => {
    setGauges(r);
    const b = S.state && S.state.pet && S.state.pet.battle;
    F.myHp = Math.max(0, numOr(r.my_hp, b ? b.my_hp : F.myHp));
    F.oppHp = Math.max(0, numOr(r.opp_hp, b ? b.opp_hp : F.oppHp));
    if (r.over) endBattle(r.won, r.draw, res.message || r.message);
    else nextRound();
  } });
  runSteps(steps);
}

// ------------------------------------------------------------ Anzeige rechts
function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function hhmm(minute) {
  return new Date(minute * 60000).toLocaleTimeString(I18N.locale(), { hour: "2-digit", minute: "2-digit" });
}

function duration(min) {
  const h = Math.floor(min / 60), m = min % 60;
  return h ? `${h} h ${m} min` : `${m} min`;
}

function segs(el, n, show) {
  el.innerHTML = [0, 1, 2, 3].map(i => `<i class="${show && i < n ? "on" : ""}"></i>`).join("");
  el.classList.toggle("empty", show && n === 0);
}

function stat(label, value, bad = false) {
  return `<div><dt>${label}</dt><dd class="${bad ? "bad" : ""}">${value}</dd></div>`;
}

// Warum ruft es? Grund + was zu tun ist + Restzeit bis zum Pflegefehler
const CALLS = {
  hunger: { short: "Hunger", text: tr("{name} hat Hunger. Gib ihm Fleisch!") },
  strength: { short: tr("Kraft"), text: tr("{name} ist schlapp. Gib ihm Protein oder trainiere!") },
  light: { short: tr("Licht"), text: tr("{name} will schlafen, aber das Licht ist an. Mach das Licht aus!") },
};
// Text eines Rufs mit Namen ("{name} hat Hunger ...")
const callText = (what, name) => CALLS[what].text.replace("{name}", () => name);

function renderCalls(pet) {
  const calls = (pet && pet.calls) || [];
  $("#call-text").textContent = calls.length
    ? tr("RUF") + ": " + calls.map(c => CALLS[c.what].short).join("+") : tr("RUF");
  $("#gauge-hunger").classList.toggle("calling", calls.some(c => c.what === "hunger"));
  $("#gauge-strength").classList.toggle("calling", calls.some(c => c.what === "strength"));
  const box = $("#alert");
  box.hidden = !calls.length;
  box.innerHTML = calls.map(c => {
    const when = c.left === null ? tr("Pflegefehler wurde schon gezählt.")
      : c.left === 0 ? tr("Gleich gibt es einen Pflegefehler!")
      : tr("Noch {n} Min bis zum Pflegefehler.", { n: c.left });
    return `<div><b>${tr("Ruf")}</b>${escapeHtml(callText(c.what, pet.name))} ${when}</div>`;
  }).join("");
}

// Zurück vom Erkunden: Bericht bleibt stehen, bis man OK drückt (solange wartet das Digimon)
function renderReturn(pet) {
  const box = $("#return-box");
  const back = pet && pet.alive && pet.returned;
  box.hidden = !back;
  if (!back) return;
  const report = typeof pet.returned === "string" ? pet.returned : "";
  const html = `<b>${tr("Zurück vom Erkunden!")}</b>${escapeHtml(report)}`
    + `<small>${tr("Dein Digimon wartet, bis du OK drückst – so lange gibt es keinen Hunger und keine Rufe.")}</small>`;
  if (box.dataset.html !== html) box.innerHTML = box.dataset.html = html;
}

function renderPanel() {
  const st = S.state;
  const pet = st.pet;
  const alive = pet && pet.alive;
  const hatched = alive && pet.stage !== "Egg";

  $("#lcd-clock").textContent = hhmm(st.now) + (st.speed !== 1 ? ` x${st.speed}` : "");
  $("#lcd-name").textContent = pet ? pet.name : tr("Kein Digimon");
  const flag = (id, on, blink) => {
    $(id).classList.toggle("on", !!on);
    $(id).classList.toggle("blink", !!(on && blink));
  };
  flag("#flag-call", alive && pet.call, true);
  renderCalls(alive ? pet : null);
  renderReturn(pet);
  flag("#flag-sick", alive && (pet.sick || pet.injured), true);
  flag("#flag-sleep", alive && pet.asleep);
  flag("#flag-light", alive && pet.light);
  document.title = (alive && pet.call ? "(!) " : "") + "Digimon V-Pet";

  // Spitzname: groß der Spitzname, darunter die Art
  $("#nick-edit").hidden = !(pet && pet.alive && pet.stage !== "Egg");
  if (!pet) {
    $("#name").textContent = tr("Kein Digimon");
    $("#name").dataset.html = "";
    $("#meta").textContent = tr("Hol dir unten ein Digi-Ei.");
  } else {
    // Name antippen -> Digidex-Eintrag dieses Digimon
    const title = pet.nickname || pet.name;
    const html = pet.dex ? `<a class="dex-link" href="hilfe.html#digimon/${pet.dex}" title="${
      tr("Digidex-Eintrag von {name} öffnen", { name: escapeHtml(pet.name) })}">${escapeHtml(title)}</a>` : escapeHtml(title);
    if ($("#name").dataset.html !== html) $("#name").innerHTML = $("#name").dataset.html = html;
    const attr = ATTR_DE[pet.attribute];
    const age = pet.age_days === 1 ? tr("{n} Tag alt", { n: 1 }) : tr("{n} Tage alt", { n: pet.age_days });
    $("#meta").textContent = !pet.alive
      ? `${pet.nickname ? pet.name + " · " : ""}${tr("Gestorben: {cause}", { cause: pet.death_cause })}`
      : [pet.nickname && pet.name, pet.stage_de, attr, age,
        pet.frozen && tr("im Kühlschrank"), pet.nap && tr("Nickerchen"), pet.away && tr("unterwegs"),
        pet.totem && tr("hält Schutz-Totem"), pet.everstone && tr("hält Ewigstein"),
        pet.charm && tr("trägt Glücksbringer"), pet.cheated && tr("gecheatet")]
        .filter(Boolean).join(" · ");
  }

  segs($("#g-hunger"), pet ? pet.hunger : 0, hatched);
  segs($("#g-strength"), pet ? pet.strength : 0, hatched);

  $("#stats").innerHTML = pet ? [
    stat(tr("Gewicht"), `${pet.weight} g`),
    stat("Training", `${pet.trainings} <small>${tr("K{power} T{speed} V{defense}", pet.skills)}${
      pet.style ? " ★" + SKILL_NAME[pet.style] : ""}</small>`),
    stat(tr("Überfüttert"), pet.overfeeds),
    stat(tr("Pflegefehler"), `${pet.mistakes} <small>${tr("/ {n} ges.", { n: pet.mistakes_total })}</small>`, pet.mistakes > 0),
    stat(tr("Kacke"), `${pet.poop} / 4`, pet.poop >= 3),
    stat(tr("Siege"), `${pet.wins} / ${pet.battles}`),
  ].join("") : "";

  let evo = "–", pct = 0;
  if (alive && pet.returned) evo = tr("pausiert – wartet auf dein OK");
  else if (alive && pet.frozen) evo = tr("pausiert (Kühlschrank)");
  else if (alive && pet.away) {
    evo = tr("unterwegs in {area} – zurück in {time}", { area: pet.away.area_name, time: duration(pet.away.minutes_left) });
    pct = 100 * (1 - pet.away.minutes_left / pet.away.minutes);
  }
  else if (alive && pet.everstone && pet.evolve_in !== null) {
    evo = tr("angehalten (Ewigstein)");
    pct = 100 * (1 - pet.evolve_in / pet.evolve_total);
  }
  else if (alive && pet.evolve_in !== null) {
    evo = pet.evolve_in > 0 ? tr("in {time}", { time: duration(pet.evolve_in) })
      : (pet.asleep ? tr("nach dem Aufwachen") : tr("gleich!"));
    pct = 100 * (1 - pet.evolve_in / pet.evolve_total);
    const g = pet.battle_goal;
    if (pet.needs_battles && g) {
      const todo = pet.battles_stage < g.battles || pet.wins_stage < g.wins;
      evo = (pet.evolve_in > 0 ? evo + " · " : "") +
        tr("Kämpfe {b}/{bg}, Siege {w}/{wg}", { b: pet.battles_stage, bg: g.battles, w: pet.wins_stage, wg: g.wins })
        + (todo ? "" : " ✓");
    }
  } else if (alive) evo = st.jogress_possible ? tr("nur per Jogress (Taste 9)") : tr("Endstufe");
  $("#evo-text").textContent = evo;
  $("#evo-fill").style.width = pct + "%";
  renderGoal(pet);
  if (!$("#wishlist").hidden) renderWishlist();

  $("#log").innerHTML = pet ? pet.log.slice().reverse()
    .map(e => `<li><time>${hhmm(e.t)}</time>${escapeHtml(e.text)}</li>`).join("") : "";

  if (!alive && S.mode !== "main") setMode("main");
  else if (S.mode === "battle" && !pet.battle && ["aim", "charge", "special"].includes(F.phase)) {
    // Kampf ist serverseitig schon vorbei (z. B. zu lange liegen gelassen)
    setMode("main");
    setMessage(tr("Der Kampf ist vorbei – das wilde Digimon ist weitergezogen."));
  } else if (S.mode === "scout" && (!pet.scout || pet.returned)) {
    setMode("main");
  } else if (alive && S.mode === "main" && pet.battle) {
    // angefangenen Kampf fortsetzen (z. B. nach Neuladen der Seite)
    startBattleView(pet.battle);
    setMode("battle");
    const incoming = Array.isArray(pet.battle.incoming) ? pet.battle.incoming : [];
    if (incoming.length) {
      // mitten im Gegenangriff neu geladen: der Angriff kommt jetzt – ausweichen!
      setMessage(tr("Der Kampf gegen {name} geht weiter – Achtung, ein Angriff kommt!", { name: pet.battle.name }));
      runSteps([{ phase: "pause", dur: 1200 }, ...attackSteps(incoming)]);
    } else {
      setMessage(tr("Der Kampf gegen {name} geht weiter! Lade deinen Schuss.", { name: pet.battle.name })
        + personalityText(""));
    }
  } else if (alive && S.mode === "main" && pet.scout && !pet.returned) {
    // ein wildes Digimon ist vom Erkunden mitgekommen: erst die Rückkehr bestätigen (OK), dann kämpfen
    setMode("scout");
    setMessage(tr("Ein wildes {name} wartet noch auf dich. Kämpfen oder fliehen?", { name: pet.scout.name }));
  } else renderKeys();
}

// ------------------------------------------------------------ Tasten
// Zahlentasten 1–9; weitere Einträge gibt es nur per Klick
function hotkey(i) { return i < 9 ? String(i + 1) : ""; }

function keyHtml(k) {
  return `<button class="key ${k.cls || ""}" data-key="${escapeHtml(k.id)}" ${k.hold ? 'data-hold="1"' : ""} ${k.disabled ? "disabled" : ""}>
    ${k.icon ? `<canvas data-icon="${k.icon}"></canvas>` : ""}
    <span>${escapeHtml(k.label)}${k.sub ? `<span class="sub">${escapeHtml(k.sub)}</span>` : ""}</span>
    ${k.hotkey ? `<small>${k.hotkey}</small>` : ""}
  </button>`;
}

function keysFor(mode) {
  const pet = S.state && S.state.pet;
  if (mode === "food") {
    return [
      { id: "meat", icon: "meat", label: tr("Fleisch"), sub: tr("Hunger +1, +1 g"), hotkey: "1" },
      { id: "protein", icon: "protein", label: "Protein", sub: tr("Kraft +1, +2 g"), hotkey: "2" },
      { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" },
    ];
  }
  if (mode === "scout") {
    return [
      { id: "fight", icon: "battle", label: tr("Kämpfen!"), sub: tr("kostet 1 Herz Hunger + 1 Kraft"), cls: "primary", hotkey: "1" },
      { id: "flee", icon: "back", label: tr("Fliehen"), sub: tr("kostet nichts"), hotkey: "Esc" },
    ];
  }
  if (mode === "battle" || mode === "duel") return fightKeys(mode === "duel");
  if (mode === "battlepick") {
    return [
      { id: "wild", icon: "battle", label: tr("Wildes Digimon"), sub: tr("zufälliger Gegner deiner Stufe"), hotkey: "1" },
      { id: "friends", icon: "star", label: tr("Freund herausfordern"), sub: tr("live gegeneinander"), hotkey: "2" },
      { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" },
    ];
  }
  if (mode === "friends") {
    const keys = (S.players || []).map((p, i) => ({
      id: "challenge:" + p.name, icon: "star", label: p.name, hotkey: hotkey(i),
      disabled: !p.online || !p.ready,
      sub: !p.online ? "offline" : !p.ready ? (p.why || tr("kann gerade nicht"))
        : tr("online · {partner} ({stage})", { partner: p.partner, stage: p.stage_de }),
    }));
    return [...keys, { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" }];
  }
  if (mode === "jogress") {
    const keys = (S.jogOpts || []).map((o, i) => ({
      id: "jog:" + i, icon: "star", label: o.to_name, hotkey: hotkey(i),
      disabled: !o.box.length && !o.friends.length,
      sub: tr("{stage} · braucht {need}", { stage: o.to_stage, need: o.need })
        + (o.box.length || o.friends.length ? "" : tr(" (keiner da)")),
    }));
    return [...keys, { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" }];
  }
  if (mode === "jogpartner") {
    const o = S.jogOpts[S.jogPick];
    const keys = [
      ...o.box.map(p => ({ id: "jogbox:" + p.id, icon: "egg", label: p.name, sub: tr("aus deiner Sammlung") })),
      ...o.friends.map(f => ({ id: "jogask:" + f.name, icon: "star", label: f.partner, sub: tr("von {name} (fragen)", { name: f.name }) })),
    ].map((k, i) => ({ ...k, hotkey: hotkey(i) }));
    return [...keys, { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" }];
  }
  if (mode === "jogwait") {
    return [{ id: "back", icon: "back", label: tr("Nicht mehr warten"), sub: tr("die Anfrage läuft von selbst ab"), cls: "wide", hotkey: "Esc" }];
  }
  if (mode === "jogask") {
    return [
      { id: "jog-yes", icon: "star", label: tr("Zustimmen"), sub: tr("dein Digimon bleibt, wie es ist"), cls: "primary", hotkey: "1" },
      { id: "jog-no", icon: "back", label: tr("Ablehnen"), hotkey: "2" },
    ];
  }
  if (mode === "duelwait") {
    return [{ id: "duel-cancel", icon: "back", label: tr("Zurückziehen"), sub: tr("Herausforderung abbrechen"),
      cls: "wide", hotkey: "Esc" }];
  }
  if (mode === "challenged") {
    return [
      { id: "duel-yes", icon: "battle", label: tr("Annehmen!"), sub: tr("kostet 1 Herz Hunger + 1 Kraft"), cls: "primary", hotkey: "1" },
      { id: "duel-no", icon: "back", label: tr("Ablehnen"), hotkey: "2" },
    ];
  }
  if (mode === "trainpick") {
    const sk = (pet && pet.skills) || {};
    const style = pet && pet.style;
    const mark = k => (style === k ? " ★" : "");
    return [
      { id: "tr:power", icon: "train", label: SKILL_NAME.power + mark("power"), hotkey: "1",
        sub: tr("Timing-Spiel · trifft öfter · {n}/10", { n: sk.power || 0 }) },
      { id: "tr:speed", icon: "explore", label: SKILL_NAME.speed + mark("speed"), hotkey: "2",
        sub: tr("Schnell drücken · weicht aus · {n}/10", { n: sk.speed || 0 }) },
      { id: "tr:defense", icon: "medicine", label: SKILL_NAME.defense + mark("defense"), hotkey: "3",
        sub: tr("Blocken · hält mehr aus · {n}/10", { n: sk.defense || 0 }) },
      { id: "back", icon: "back", label: tr("Zurück"), cls: "wide", hotkey: "Esc" },
    ];
  }
  if (mode === "train") {
    const label = { power: tr("Jetzt!"), speed: tr("Drücken!"), defense: tr("Blocken!") }[T.kind];
    return [
      { id: "hit", label, cls: "wide primary", hotkey: tr("Leertaste") },
      { id: "back", icon: "back", label: tr("Abbrechen"), cls: "wide", hotkey: "Esc" },
    ];
  }
  if (mode === "areas") {
    const keys = S.state.areas.map((a, i) => ({
      id: "area:" + a.key, icon: "explore", label: a.name, hotkey: String(i + 1), disabled: !a.unlocked,
      sub: a.unlocked ? tr("{n} Ei-Sorten", { n: a.eggs }) : tr("ab {stage}", { stage: a.min }),
    }));
    return [...keys, { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" }];
  }
  if (mode === "trip") {
    return [
      { id: "trip:30", icon: "explore", label: tr("{n} Min", { n: 30 }), sub: tr("1 Fundchance"), hotkey: "1" },
      { id: "trip:120", icon: "explore", label: tr("{n} Std", { n: 2 }), sub: tr("{n} Fundchancen", { n: 3 }), hotkey: "2" },
      { id: "trip:480", icon: "explore", label: tr("{n} Std", { n: 8 }), sub: tr("{n} Fundchancen", { n: 6 }), hotkey: "3" },
      { id: "back", icon: "back", label: tr("Zurück"), cls: "wide", hotkey: "Esc" },
    ];
  }
  if (mode === "bag") {
    // nur, was man auch hat (sonst wird die Liste zu lang); den Ewigstein kann man wieder abnehmen
    const holding = pet && pet.everstone;
    // ein Item antippen -> Benutzen oder Verkaufen (Modus "bagitem")
    const keys = S.state.inventory.filter(it => it.count && !(holding && it.key === "everstone")).map(it => ({
      id: "bagitem:" + it.key, icon: itemIcon(it),
      label: `${it.name} ×${it.count}`, sub: it.fits ? tr("passt zu deinem Digimon – jetzt digitieren!") : it.desc,
      cls: it.fits ? "primary" : "",
    }));
    if (pet && pet.everstone) {
      keys.unshift({ id: "item:everstone", icon: "stone", label: tr("Ewigstein abnehmen"),
        sub: tr("dann kann es wieder digitieren"), cls: "primary" });
    }
    return [...keys.map((k, i) => ({ ...k, hotkey: hotkey(i) })),
      { id: "back", icon: "back", label: tr("Zurück"), hotkey: "Esc" }];
  }
  if (mode === "bagitem" || mode === "sell") {
    const it = bagItem();
    if (!it) return [{ id: "back", icon: "back", label: tr("Zurück"), cls: "wide", hotkey: "Esc" }];
    if (mode === "bagitem") {
      // Ei-Scherben: 4 gleiche zusammensetzen -> Digi-Ei in die Sammlung
      const use = it.shard
        ? { id: "item:" + it.key, icon: "egg", label: tr("Zusammensetzen"), cls: it.count >= SHARDS_PER_EGG ? "primary" : "",
            disabled: it.count < SHARDS_PER_EGG, hotkey: "1",
            sub: it.count >= SHARDS_PER_EGG ? tr("{n} Scherben → 1 Digi-Ei", { n: SHARDS_PER_EGG })
              : tr("{have} von {n} – sammle noch {left}", { have: it.count, n: SHARDS_PER_EGG, left: SHARDS_PER_EGG - it.count }) }
        : { id: "item:" + it.key, icon: itemIcon(it), label: tr("Benutzen"), cls: it.fits ? "primary" : "",
            sub: it.fits ? tr("passt zu deinem Digimon – jetzt digitieren!") : it.desc, hotkey: "1" };
      return [
        use,
        { id: "sell-pick", icon: "coin", label: tr("Verkaufen"), disabled: !it.sell,
          sub: it.sell ? tr("{n} Bits pro Stück", { n: it.sell }) : tr("kann man nicht verkaufen"), hotkey: "2" },
        { id: "back", icon: "back", label: tr("Zurück"), cls: "wide", hotkey: "Esc" },
      ];
    }
    const n = Math.min(S.sellN, it.count);
    return [
      { id: "sell-minus", label: "− 1", disabled: n <= 1, hotkey: "1" },
      { id: "sell-plus", label: "+ 1", disabled: n >= it.count, hotkey: "2" },
      { id: "sell-all", label: tr("Alle ({n})", { n: it.count }), disabled: n >= it.count, hotkey: "3" },
      { id: "sell-ok", icon: "coin", label: tr("{n}× verkaufen", { n }), cls: "primary wide",
        sub: tr("+{n} Bits", { n: n * it.sell }), hotkey: "4" },
      { id: "back", icon: "back", label: tr("Zurück"), cls: "wide", hotkey: "Esc" },
    ];
  }
  if (!pet || !pet.alive) {
    if (S.state && !S.state.free_egg) {
      return [{ id: "collection", icon: "egg", label: tr("Zur Sammlung"), sub: tr("Dort warten noch Digimon oder Eier auf dich"),
        cls: "wide primary", hotkey: "1" }];
    }
    return [{ id: "new-egg", icon: "egg", label: tr("Neues Digi-Ei holen"), sub: tr("Welches es wird, entscheidet der Zufall"),
      cls: "wide primary", hotkey: "1" }];
  }
  if (pet.returned) {
    // zurück vom Erkunden: erst bestätigen, dann läuft die Zeit weiter
    return [{ id: "confirm-return", icon: "home", label: tr("OK – willkommen zurück!"),
      sub: tr("Bis dahin wartet dein Digimon: kein Hunger, keine Rufe"), cls: "wide primary", hotkey: "1" }];
  }
  if (pet.frozen) {
    return [{ id: "thaw", icon: "fridge", label: tr("Auftauen"), sub: tr("Aus dem Kühlschrank holen – die Zeit läuft weiter"),
      cls: "wide primary", hotkey: "1" }];
  }
  if (pet.away) {
    // unterwegs geht nur Zurückrufen – oder eine Sanduhr aus dem Rucksack
    return [{ id: "recall", icon: "home", label: tr("Zurückrufen"),
      sub: tr("kommt sofort heim – aber ohne Funde"), hotkey: "1" },
    { id: "bag", icon: "bag", label: tr("Rucksack"), sub: tr("z. B. Sanduhr: schneller zurück"), hotkey: "2" }];
  }
  const grown = BATTLE_STAGES.includes(pet.stage);
  return [
    { id: "food", icon: "food", label: tr("Futter"), hotkey: "1" },
    { id: "train", icon: "train", label: "Training", hotkey: "2" },
    { id: "clean", icon: "clean", label: tr("Putzen"), hotkey: "3" },
    { id: "light", icon: "light", label: tr("Licht"), sub: pet.light ? tr("aus = schlafen") : tr("an = aufwecken"), hotkey: "4" },
    { id: "medicine", icon: "medicine", label: tr("Medizin"), hotkey: "5" },
    grown ? { id: "battle", icon: "battle", label: tr("Kampf"), sub: tr("gegen wilde Digimon"), hotkey: "6" }
      : { id: "battle", icon: "battle", label: tr("Kampf"), sub: tr("ab Rookie"), disabled: true },
    grown ? { id: "explore", icon: "explore", label: tr("Erkunden"), sub: tr("Eier & Items finden"), hotkey: "7" }
      : { id: "explore", icon: "explore", label: tr("Erkunden"), sub: tr("ab Rookie"), disabled: true },
    { id: "bag", icon: "bag", label: tr("Rucksack"), hotkey: "8",
      sub: tr("{n} Items · {bits} Bits", { n: S.state.inventory.reduce((n, it) => n + it.count, 0), bits: S.state.bits || 0 }) },
    S.state.jogress_possible
      ? { id: "jogress", icon: "star", label: "Jogress", sub: tr("Fusion möglich!"), hotkey: "9", cls: "primary" }
      : { id: "jogress", icon: "star", label: "Jogress", sub: tr("gerade keine Fusion"), disabled: true },
  ];
}

// Kampf-Tasten: halten = laden (reagieren auf pointerdown/-up statt Klick, siehe bindHoldKey).
// Beim Gegenangriff heißen ↑/↓ Springen/Ducken, beim Spezial zählt jeder Druck.
function fightKeys(pvp) {
  const dodging = DODGE_PHASES.includes(F.phase);
  const mashing = F.phase === "special";
  const aimSub = tr("halten = laden, loslassen = Schuss");
  const keys = [
    { id: "aim-high", icon: "up", hold: true, cls: "primary", hotkey: "↑/W",
      label: dodging ? tr("Springen ↑") : mashing ? tr("Drücken!") : tr("Oben ↑"),
      sub: dodging ? tr("wenn der Ball unten kommt") : mashing ? "" : aimSub },
    { id: "aim-low", icon: "down", hold: true, cls: "primary", hotkey: "↓/S",
      label: dodging ? tr("Ducken ↓") : mashing ? tr("Drücken!") : tr("Unten ↓"),
      sub: dodging ? tr("wenn der Ball oben kommt") : mashing ? "" : aimSub },
  ];
  // Spezial gibt es nur mit voller Leiste
  if (F.myGauge >= SPECIAL_MAX || mashing) {
    keys.push({ id: "special", icon: "star", hold: true, cls: "primary span-m", hotkey: "E",
      label: mashing ? tr("Drücken!") : tr("Spezial: {name}", { name: F.specialName }),
      sub: mashing ? tr("so schnell wie möglich!") : tr("Leiste voll! Dann 2 Sekunden schnell drücken") });
  }
  if (pvp) keys.push({ id: "duel-giveup", icon: "back", label: tr("Aufgeben"), sub: tr("zählt als Niederlage"), cls: "wide" });
  return keys;
}

let keysSig = "";
function renderKeys() {
  document.body.classList.toggle("action", S.mode in ACTION_KEY);
  document.body.classList.toggle("fight", S.mode === "battle" || S.mode === "duel");
  const keys = keysFor(S.mode);
  const sig = S.mode + themeShown + JSON.stringify(keys);    // neues Design -> Symbole neu malen
  if (sig === keysSig) return;      // nicht unnötig neu zeichnen
  keysSig = sig;
  const box = $("#keys");
  box.innerHTML = keys.map(keyHtml).join("");
  box.querySelectorAll("canvas[data-icon]").forEach(paintIcon);
  box.querySelectorAll("[data-key]").forEach(b => {
    if (b.dataset.hold) return bindHoldKey(b);
    b.addEventListener("click", () => {
      if (performance.now() < S.keysLockedUntil) return;      // Klick-Pause nach Training/Kampf
      press(b.dataset.key);
    });
  });
}

// Kampf-Knöpfe reagieren schon beim Drücken (und beim Loslassen), nicht erst beim Klick
function bindHoldKey(b) {
  b.addEventListener("pointerdown", e => {
    if (e.button > 0 || performance.now() < S.keysLockedUntil) return;
    e.preventDefault();
    if (b.dataset.key === "special") return specialKey();
    holdStart(b.dataset.key === "aim-low" ? "low" : "high", "btn");
  });
  ["pointerup", "pointercancel", "pointerleave"].forEach(type => b.addEventListener(type, () => holdEnd("btn")));
  b.addEventListener("contextmenu", e => e.preventDefault());    // langes Drücken am Handy: kein Menü
}

const ACTION_KEY = { train: "hit", battle: "aim-high", duel: "aim-high" };
// Nach Training oder Kampf (wo man schnell hintereinander klickt) erscheint an derselben
// Stelle das Hauptmenü – damit kein Nachklicken aus Versehen Futter, Licht & Co. auslöst,
// nehmen die Tasten kurz keine Mausklicks an.
const CLICK_PAUSE = 1500;   // ms
S.keysLockedUntil = 0;

function setMode(mode) {
  const leaving = S.mode in ACTION_KEY && !(mode in ACTION_KEY);
  S.mode = mode;
  S.anim = null;
  if (mode !== "battle" && mode !== "duel") F.hold = F.mash = null;   // nichts bleibt „gedrückt“
  if (leaving) {
    S.keysLockedUntil = performance.now() + CLICK_PAUSE;
    $("#keys").classList.add("cooldown");
    clearTimeout(S.lockTimer);
    S.lockTimer = setTimeout(() => $("#keys").classList.remove("cooldown"), CLICK_PAUSE);
  }
  renderKeys();
}

// Aufs Display tippen = Aktionstaste (praktisch am Handy).
// Im Kampf: obere Hälfte = oben/springen, untere = unten/ducken (halten = laden).
// Die Grenze ist die Mitte des Spielfelds – die Symbolleiste oben zählt zur oberen Hälfte.
$(".lcd-canvas").addEventListener("pointerdown", e => {
  if (e.button > 0) return;
  if (S.mode === "battle" || S.mode === "duel") {
    e.preventDefault();
    const box = lcd.getBoundingClientRect();
    holdStart(e.clientY < box.top + box.height * (OY + 8) / LCD_H ? "high" : "low", "lcd");
    return;
  }
  const key = ACTION_KEY[S.mode];
  if (!key) return;
  e.preventDefault();
  press(key);
});
$(".lcd-canvas").addEventListener("pointerleave", () => holdEnd("lcd"));
$(".lcd-canvas").addEventListener("contextmenu", e => { if (S.mode === "battle" || S.mode === "duel") e.preventDefault(); });

function blocker() {
  const pet = S.state && S.state.pet;
  if (!pet) return tr("Du hast noch kein Digimon.");
  if (!pet.alive) return tr("Dein Digimon lebt nicht mehr.");
  if (pet.returned) return tr("{name} ist vom Erkunden zurück – erst mit OK bestätigen.", { name: pet.name });
  if (pet.frozen) return tr("{name} ist im Kühlschrank. Erst auftauen!", { name: pet.name });
  if (pet.away) return tr("{name} ist unterwegs in {area}.", { name: pet.name, area: pet.away.area_name });
  if (pet.stage === "Egg") return tr("Das Ei schlüpft gleich ...");
  if (pet.asleep && pet.nap) return tr("{name} macht ein Nickerchen. Licht an weckt es.", { name: pet.name });
  if (pet.asleep) return tr("{name} schläft gerade. Psst!", { name: pet.name });
  return null;
}

// Rucksack: geht auch im Schlaf und unterwegs (Sanduhr, Löschdiskette) – nur nicht ohne Digimon
function bagBlocker() {
  const pet = S.state && S.state.pet;
  if (!pet) return tr("Du hast noch kein Digimon.");
  if (!pet.alive) return tr("Dein Digimon lebt nicht mehr.");
  if (pet.frozen) return tr("{name} ist im Kühlschrank. Erst auftauen!", { name: pet.name });
  if (pet.stage === "Egg") return tr("Das Ei schlüpft gleich ...");
  return null;
}

// das im Rucksack gewählte Item (null, wenn keins mehr da ist)
function bagItem() {
  return ((S.state && S.state.inventory) || []).find(it => it.key === S.bagKey && it.count > 0) || null;
}

function bagItemText() {
  const it = bagItem();
  if (it && it.shard) {
    return tr("{item} ×{n}: {per} Stück ergeben ein Digi-Ei. Zusammensetzen oder verkaufen?",
      { item: it.name, n: it.count, per: SHARDS_PER_EGG });
  }
  return it ? tr("{item} ×{n}: benutzen oder verkaufen?", { item: it.name, n: it.count }) : "";
}

async function sellItem() {
  const it = bagItem();
  if (!it) return setMode("bag");
  try {
    const res = await api("/api/shop/sell", { item: it.key, amount: Math.min(S.sellN, it.count) });
    apply(res);
    sfx("reward");
    // noch welche übrig -> beim Item bleiben, sonst zurück in den Rucksack
    setMode(bagItem() ? "bagitem" : "bag");
    setMessage(res.message);
  } catch (e) {
    sfx("refuse");
    setMessage(e.message);
  }
}

async function press(id) {
  const pet = S.state && S.state.pet;
  if (id === "back" && S.mode === "scout") id = "flee";
  if (id === "back" && S.mode === "duelwait") id = "duel-cancel";
  if (id === "back" && S.mode === "challenged") id = "duel-no";
  if (id === "back" && S.mode === "jogask") id = "jog-no";
  if (id === "back" && (S.mode === "bagitem" || S.mode === "sell")) {
    // eine Ebene zurück: Verkaufen -> Item -> Rucksack
    sfx("cancel");
    const up = S.mode === "sell" && bagItem() ? "bagitem" : "bag";
    setMode(up);
    return setMessage(up === "bag" ? tr("Welches Item? Danach: benutzen oder verkaufen.") : bagItemText());
  }
  if (id === "back") {
    if (S.mode === "battle" || S.mode === "duel") return setMessage(tr("Mitten im Kampf gibt es kein Zurück!"));
    if (S.mode !== "main") sfx("cancel");
    setMode("main");
    setMessage("");
    return;
  }
  if (id === "hit") return trainingHit();
  if (id.startsWith("tr:")) { sfx("click"); return startTraining(id.slice(3)); }
  if (id === "fight") { sfx("click"); return startFight(); }
  if (id === "flee") {
    sfx("cancel");
    const res = await battleStep("flee");
    setMode("main");
    if (res) setMessage(res.message);
    return;
  }
  if (id === "battle") {
    const why = blocker();
    if (why) { sfx("refuse"); return setMessage(why); }
    sfx("menu");
    setMode("battlepick");
    return setMessage(tr("Gegen wen?"));
  }
  if (id === "jogress") {
    const why = blocker();
    if (why) { sfx("refuse"); return setMessage(why); }
    try {
      S.jogOpts = (await api("/api/jogress")).options;
      setMode("jogress");
      sfx("menu");
      return setMessage(tr("Welche Fusion? Dein Partner-Digimon bleibt dabei, wie es ist."));
    } catch (e) { return setMessage(e.message); }
  }
  if (id.startsWith("jog:")) {
    S.jogPick = Number(id.slice(4));
    setMode("jogpartner");
    return setMessage(tr("Mit wem zu {name} fusionieren?", { name: S.jogOpts[S.jogPick].to_name }));
  }
  if (id.startsWith("jogbox:")) {
    return jogressStep("box", { to: S.jogOpts[S.jogPick].to, partner_id: Number(id.slice(7)) });
  }
  if (id.startsWith("jogask:")) {
    const res = await jogressStep("ask", { to: S.jogOpts[S.jogPick].to, name: id.slice(7) });
    if (res) setMode("jogwait");
    return;
  }
  if (id === "jog-yes" || id === "jog-no") return jogressStep("answer", { accept: id === "jog-yes" });
  if (id === "wild") { sfx("click"); return scoutBattle(); }
  if (id === "friends") { sfx("click"); return showFriends(); }
  if (id.startsWith("challenge:")) { sfx("click"); return duelStep("challenge", { name: id.slice(10) }); }
  if (id === "duel-cancel") return duelStep("cancel");
  if (id === "duel-yes") return duelStep("answer", { accept: true });
  if (id === "duel-no") return duelStep("answer", { accept: false });
  if (id === "duel-giveup") {
    if (S.giveUp) { S.giveUp = false; return duelStep("forfeit"); }
    S.giveUp = true;
    setTimeout(() => { S.giveUp = false; }, 3000);
    return setMessage(tr("Wirklich aufgeben? Nochmal drücken zum Bestätigen."));
  }
  sfx("click");
  if (id === "meat" || id === "protein") {
    setMode("main");
    return act("feed", { food: id });
  }
  if (id === "new-egg") return newEgg("/api/egg");
  if (id === "collection") return openCollection();
  if (id === "explore" || id === "bag") {
    // Rucksack geht auch im Schlaf und unterwegs (Sanduhr, Löschdiskette, Leckerbissen weckt aus dem
    // Nickerchen) – ob ein Item gerade passt, sagt der Server
    const why = id === "bag" ? bagBlocker() : blocker();
    if (why) { sfx("refuse"); return setMessage(why); }
    setMode(id === "explore" ? "areas" : "bag");
    sfx("menu");
    if (id === "bag" && keysFor("bag").length === 1) {
      return setMessage(tr("Dein Rucksack ist leer. Im Shop (Münze oben) kannst du Items für Bits kaufen."));
    }
    return setMessage(id === "explore" ? tr("Wohin soll die Reise gehen?") : tr("Welches Item? Danach: benutzen oder verkaufen."));
  }
  if (id.startsWith("area:")) {
    S.tripArea = id.slice(5);
    setMode("trip");
    const area = S.state.areas.find(a => a.key === S.tripArea);
    return setMessage(tr("{area}: Wie lange? Längere Touren bringen mehr – kosten 1 Herz Hunger als Proviant.", { area: area.name }));
  }
  if (id.startsWith("trip:")) return expedition("/api/explore", { area: S.tripArea, minutes: Number(id.slice(5)) });
  if (id === "recall") return expedition("/api/explore/recall", {});
  if (id === "confirm-return") return expedition("/api/explore/confirm", {});
  if (id === "item:reset" && !S.resetSure) {
    // Reset-Kristall lässt sich nicht rückgängig machen -> zweimal drücken
    S.resetSure = true;
    setTimeout(() => { S.resetSure = false; }, 4000);
    sfx("alarm");
    return setMessage(tr("Wirklich? {name} wird wieder zu einem zufälligen Digi-Ei! Nochmal drücken zum Bestätigen.",
      { name: pet.name }));
  }
  if (id.startsWith("item:")) { S.resetSure = false; return expedition("/api/item", { item: id.slice(5) }); }
  // Rucksack: Item gewählt -> Benutzen oder Verkaufen
  if (id.startsWith("bagitem:")) {
    S.bagKey = id.slice(8);
    setMode("bagitem");
    return setMessage(bagItemText());
  }
  if (id === "sell-pick") {
    S.sellN = 1;
    setMode("sell");
    return setMessage(tr("Wie viele {item} verkaufen? Du hast {n}.", { item: bagItem().name, n: bagItem().count }));
  }
  if (id === "sell-minus" || id === "sell-plus" || id === "sell-all") {
    const max = bagItem().count;
    S.sellN = id === "sell-all" ? max : Math.max(1, Math.min(max, S.sellN + (id === "sell-plus" ? 1 : -1)));
    return renderKeys();
  }
  if (id === "sell-ok") return sellItem();
  if (id === "thaw") return setFridge(false);
  if (id === "food" || id === "train") {
    // Futter geht auch im Nickerchen: es wacht davon auf (im Nickerchen wird es ja hungrig)
    const why = id === "food" && pet && pet.nap ? null : blocker();
    if (why) { sfx("refuse"); return setMessage(why); }
    if (id === "food") {
      setMode("food");
      sfx("menu");
      return setMessage(pet.nap ? tr("Was soll es essen? Das Futter weckt es aus dem Nickerchen.") : tr("Was soll es essen?"));
    }
    if (pet.sick || pet.injured) return setMessage(tr("{name} ist nicht fit genug zum Trainieren.", { name: pet.name }));
    setMode("trainpick");
    sfx("menu");
    return setMessage(pet.style ? tr("Welches Training? Trainingsstil: {style} ★", { style: SKILL_NAME[pet.style] })
      : tr("Welches Training?"));
  }
  act(id);
}

async function expedition(path, body) {
  const from = S.state && S.state.pet && S.state.pet.dex;              // für die Armor-Digitation
  try {
    const res = await api(path, body);
    S.mode = "main";
    apply(res);
    setMessage(res.message);
    // Armor-Digitation: den Digitations-Ton spielt schon announce()
    if (res.anim !== "armor") sfx(path === "/api/explore" ? "confirm" : res.anim === "eat" ? "eat" : "happy");
    const pet = res.pet;
    if (res.anim && pet && pet.alive && !pet.asleep && !pet.away) {
      S.anim = { type: res.anim, food: body.item, from, start: S.tick };  // food: Leckerbissen
    }
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

async function newEgg(path) {
  try {
    const res = await api(path, {});
    S.mode = "main";
    S.anim = null;
    apply(res);
    sfx("confirm");
    setMessage(tr("Ein neues Digi-Ei! Was wohl daraus schlüpft ..."));
  } catch (e) { setMessage(e.message); }
}

// Tastatur: Zahlen = Tasten, Leertaste = Jetzt!, Esc = zurück
document.addEventListener("keydown", e => {
  if (!$("#quiz").hidden && $("#settings").hidden) return quizKeydown(e);
  if (!$("#cheats").hidden) { if (e.key === "Escape") closeCheats(); return; }
  if (!$("#collection").hidden) {
    if (e.key === "Escape") closeCollection();
    const typing = e.target.matches && e.target.matches("input, select, textarea");
    if (!typing && e.key === "ArrowLeft") showBox(S.pcBox - 1);
    if (!typing && e.key === "ArrowRight") showBox(S.pcBox + 1);
    return;
  }
  if (!$("#changelog").hidden) { if (e.key === "Escape") closeChangelog(); return; }
  if (!$("#ranking-panel").hidden) { if (e.key === "Escape") closeRanking(); return; }
  if (!$("#shop").hidden) { if (e.key === "Escape") closeShop(); return; }
  if (!$("#wishlist").hidden) { if (e.key === "Escape") closeWishlist(); return; }
  if (!$("#event-panel").hidden) { if (e.key === "Escape") closeEvent(); return; }
  if (!$("#friend-panel").hidden) { if (e.key === "Escape") closeFriend(); return; }
  if (!$("#settings").hidden) { if (e.key === "Escape") closeSettings(); return; }
  if (e.target.closest && e.target.closest("#nick-form")) {
    if (e.key === "Escape") $("#nick-form").hidden = true;
    return;                                         // beim Tippen des Spitznamens keine Tasten
  }
  if (e.key === "C" && e.shiftKey && S.state && S.state.user.admin && !$("#console").hidden
      && !e.target.closest("input")) {
    return openCheats();
  }
  if (!S.state || $("#console").hidden || e.target.closest("input")) return;
  if (e.key === "Escape") return press("back");
  if (e.key === " " && S.mode === "train") {
    e.preventDefault();
    if (e.repeat) return;               // Taste festhalten zählt nicht als viele Drücke
    return press("hit");
  }
  if (S.mode === "battle" || S.mode === "duel") {
    // ↑/W, ↓/S halten = laden (keyup schießt), Leertaste = oben laden, E = Spezial
    const k = FIGHT_KEYS[(e.key || "").toLowerCase()];
    if (k) {
      e.preventDefault();
      if (!e.repeat) fightKey(k);         // Festhalten startet das Laden nicht neu
      return;
    }
  }
  const n = parseInt(e.key, 10);
  if (!n || e.repeat) return;
  const keys = keysFor(S.mode).filter(k => !k.disabled && k.hotkey === String(n));
  if (keys.length) press(keys[0].id);
});

function paintIcon(canvas) {
  const rows = canvas.dataset.icon === "egg" ? EGG : ICONS[canvas.dataset.icon];
  const scale = Math.ceil(32 / rows[0].length) * 2;
  canvas.width = rows[0].length * scale;
  canvas.height = rows.length * scale;
  const color = getComputedStyle(canvas.parentElement).color;
  drawBitmap(canvas.getContext("2d"), rows, 0, 0, scale, color);
}

// ------------------------------------------------------------ Einstellungen (pro Gerät)
const SETTINGS_KEY = "vpet.settings";
const settings = Object.assign({ volume: 50, notify: false }, (() => {
  try { return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}; } catch { return {}; }
})());

function saveSettings() {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings)); } catch { /* egal */ }
}

// ------------------------------------------------------------ Soundeffekte
const sounds = {};
function sfx(name) {
  if (!settings.volume) return;
  if (!sounds[name]) sounds[name] = new Audio(`/sounds/${name}.wav`);
  const a = sounds[name].cloneNode();
  a.volume = settings.volume / 100;
  a.play().catch(() => { /* Browser erlaubt Ton erst nach dem ersten Klick */ });
}

// ------------------------------------------------------------ Browser-Benachrichtigungen
const canNotify = "Notification" in window;
let pushSubscription = null;
let pushActive = false;
let pushKey = null;
let pushUser = null;
let pushBusy = false;
const isIos = () => /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
const isStandalone = () => navigator.standalone === true || matchMedia("(display-mode: standalone)").matches;
const canPush = () => canNotify && "serviceWorker" in navigator && "PushManager" in window;

async function refreshPush() {
  if (pushBusy) return;
  const user = S.state && S.state.user.name;
  if (!user || !canPush()) return;
  try {
    const info = await request("/api/push");
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.getSubscription();
    if (!S.state || S.state.user.name !== user) return;
    pushKey = info.key;
    pushSubscription = sub;
    pushActive = !!sub && info.endpoints.includes(sub.endpoint) && Notification.permission === "granted";
  } catch { pushActive = false; }
  renderNotifySetting();
}

function notify(title, body, tag) {
  if (pushActive) return;             // der Server sendet bereits an dieses Gerät
  if (!settings.notify || !canNotify || Notification.permission !== "granted") return;
  if (!document.hidden && document.hasFocus()) return;   // du schaust gerade eh hin
  const pet = S.state && S.state.pet;
  let icon;
  if (pet && pet.dex && S.data) {
    // das aktuelle Digimon als Bild für die Benachrichtigung
    const c = document.createElement("canvas");
    c.width = c.height = 64;
    const g = c.getContext("2d");
    g.fillStyle = COLOR_BG;
    g.fillRect(0, 0, 64, 64);
    drawBitmap(g, sprite(pet.dex, "idle"), 0, 0, 4, COLOR_PX);
    icon = c.toDataURL();
  }
  const options = { body, tag, icon, renotify: true };
  try {
    const n = new Notification(title, options);
    n.onclick = () => { window.focus(); n.close(); };
  } catch {
    // Handys (Android/Chrome) erlauben das nur über den Service Worker
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.ready.then(reg => reg.showNotification(title, options)).catch(() => {});
    }
  }
}

// Was hat sich seit dem letzten Stand geändert? -> Ton + Benachrichtigung
function announce(before, pet) {
  if (!before || !pet || before.id !== pet.id) return;
  const name = pet.name;
  if (before.totem && !pet.totem && pet.alive && pet.frozen && !before.frozen) {
    // das Schutz-Totem hat es gerade vor dem Tod gerettet
    sfx("evolve");
    S.anim = { type: "totem_save", start: S.tick };
    return notify(tr("Das Schutz-Totem hat dein Digimon gerettet!"),
      tr("{name} wäre fast gestorben und wartet jetzt im Kühlschrank auf dich.", { name }), "death");
  }
  if (before.alive && !pet.alive) {
    sfx("death");
    if (before.dex) S.anim = { type: "death", from: before.dex, start: S.tick };
    return notify(tr("{name} ist gestorben", { name: before.name }), pet.death_cause, "death");
  }
  if (before.stage === "Egg" && pet.stage !== "Egg") {
    sfx("hatch");
    S.anim = { type: "hatch", start: S.tick };
    return notify(tr("Das Ei ist geschlüpft!"), tr("Es ist ein {name}!", { name }), "evolve");
  }
  if (before.stage !== "Egg" && pet.stage === "Egg") {
    // Reset-Kristall: wieder ein Ei (keine Digitation)
    sfx("evolve");
    S.anim = { type: "reset", from: before.dex, start: S.tick };
    return;
  }
  if (before.dex !== pet.dex) {
    sfx("evolve");
    if (before.dex && pet.dex) S.anim = { type: "evolve", from: before.dex, start: S.tick };
    return notify(tr("Digitation!"), tr("{old} hat sich zu {name} entwickelt!", { old: before.name, name }), "evolve");
  }
  if (!before.sick && pet.sick) {
    sfx("alarm");
    return notify(tr("{name} ist krank!", { name }), tr("Gib ihm schnell Medizin."), "sick");
  }
  const oldCalls = new Set((before.calls || []).map(c => c.what));
  const fresh = (pet.calls || []).filter(c => !oldCalls.has(c.what));
  if (fresh.length) {
    sfx("alarm");
    notify(tr("{name} ruft dich!", { name }), fresh.map(c => callText(c.what, name)).join(" "), "call");
  }
  if (pet.poop > before.poop) sfx("poop");
}

// ------------------------------------------------------------ Updates
// Der Server meldet einen Fingerabdruck seiner Dateien. Ändert der sich (neues
// Update eingespielt), zeigen wir oben "Update da! – Neu laden".
// Dazu die Versionsnummer für Menschen (release, z. B. "1.8" – neuester Changelog-Eintrag).
let loadedVersion = null;

function checkVersion(version, release) {
  if (!version) return;
  if (!loadedVersion) {
    loadedVersion = version;
    $("#version-label").textContent = release ? `Version ${release}` : "";
  }
  $("#update-bar").hidden = version === loadedVersion;
  $("#update-text").textContent = release ? tr("Version {v} ist da.", { v: release }) : tr("Es gibt eine neue Version des Spiels.");
}

$("#update-reload").addEventListener("click", async () => {
  try {
    // auch die App-Hülle (Service Worker) auf den neuen Stand bringen
    const reg = "serviceWorker" in navigator && await navigator.serviceWorker.getRegistration();
    if (reg) await reg.update();
  } catch { /* egal – Neuladen holt die Dateien trotzdem frisch vom Server */ }
  location.reload();
});

// ------------------------------------------------------------ Server
let posting = false;                 // läuft gerade eine Aktion? (gegen Doppelklicks)

async function api(path, body) {
  if (body === undefined) return request(path, body);
  if (posting) throw new Error(tr("Einen Moment ..."));
  posting = true;
  try { return await request(path, body); } finally { posting = false; }
}

async function request(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const json = await res.json().catch(() => ({ error: tr("Server-Fehler") }));
  if (res.status === 401 || (res.status === 503 && json.maintenance)) {
    // abgemeldet, gesperrt oder Wartungsarbeiten -> zurück zur Anmeldung
    if ($("#auth").hidden) {
      S.access = await (await fetch("/api/me")).json().catch(() => ({}));
      showAuth(false);
      $("#auth-error").textContent = json.error || "";
    }
    throw new Error(json.error);
  }
  if (!res.ok) throw new Error(json.error || tr("Server-Fehler"));
  return json;
}

function setMessage(text) { $("#message").textContent = text; }

function apply(state) {
  const before = S.state && S.state.pet;
  S.state = state;
  if (pushUser !== state.user.name) {
    pushUser = state.user.name;
    pushActive = false;
    refreshPush();
  }
  const pet = state.pet;
  // neue Tagebucheinträge (Entwicklung, Krankheit ...) als Nachricht zeigen
  if (before && pet && before.id === pet.id && pet.log.length) {
    const last = pet.log[pet.log.length - 1];
    const prev = before.log[before.log.length - 1];
    if (!prev || last.t !== prev.t || last.text !== prev.text) setMessage(last.text);
  }
  announce(before, pet);
  checkVersion(state.version, state.release);
  syncDuel(state);
  syncJogress(state);
  $("#open-collection").classList.toggle("badge-dot", !!state.trades_todo);
  const note = state.announcement || "";
  $("#announcement").hidden = !note && !state.maintenance;
  $("#announcement").innerHTML = (state.maintenance ? `<b>${tr("Wartungsmodus")}</b>${tr("nur Admins können gerade spielen.")} ` : "")
    + (note ? `<b>${tr("Nachricht")}</b>${escapeHtml(note)}` : "");
  applyTheme(state.theme);                       // V-Pet-Design des Kontos
  // laufendes Event: Leiste oben + eigene Farben (body.ev-halloween)
  const ev = state.event;
  // Banner lässt sich schließen (pro Event und Jahr gemerkt), der Event-Tab oben bleibt
  $("#event-bar").hidden = !ev || eventClosed(ev);
  $("#open-event").hidden = !ev;
  document.body.className = document.body.className.replace(/\bev-\S+/g, "").trim();
  if (ev) {
    document.body.classList.add(`ev-${ev.key}`);
    $("#event-name").textContent = tr("{name} – bis {until}", { name: ev.name, until: ev.until });
    $("#event-text").textContent = ev.text;
    for (const c of [$("#event-icon"), $("#open-event canvas")]) {
      if (c.dataset.icon !== ev.icon) { c.dataset.icon = ev.icon; paintIcon(c); }
    }
  }
  // neu geschaffte Erfolge (bringen Bits)
  if (state.achievements_new && state.achievements_new.length) {
    const text = state.achievements_new.map(a => tr("Erfolg: {name} (+{bits} Bits)", { name: a.name, bits: a.reward })).join(" · ");
    setTimeout(() => setMessage(text), 1200);       // nach der Meldung zur Aktion zeigen
    sfx("reward");
    notify(tr("Erfolg geschafft!"), text, "achievement");
  }
  if (state.report) {
    // zurück vom Erkunden
    setMessage(state.report.text);
    sfx("reward");
    if (pet && pet.alive && !pet.away && !pet.asleep) S.anim = { type: "return", start: S.tick };
    notify(pet ? tr("{name} ist zurück!", { name: pet.name }) : tr("Dein Digimon ist zurück!"), state.report.text, "explore");
  }
  if (state.box_reports && state.box_reports.length) {
    // Digimon aus der Sammlung zurück vom Erkunden
    const text = state.box_reports.join(" ");
    setMessage(state.report ? `${state.report.text} ${text}` : text);
    sfx("reward");
    notify(tr("Zurück vom Erkunden!"), text, "explore");
    if (!$("#collection").hidden) api("/api/box").then(col => { S.box = col.box; renderCollection(col); }).catch(() => {});
  }
  renderPanel();
  // offener Shop: neue Bits (z. B. vom Erkunden) gleich anzeigen
  if (!$("#shop").hidden && shopItems.length && String(state.bits || 0) !== $("#shop-bits").textContent) renderShop();
}

async function refresh() {
  if ($("#console").hidden) return;
  try {
    apply(await api("/api/state"));
  } catch (e) {
    if (!$("#console").hidden) setMessage(tr("Keine Verbindung zum Server. Läuft start.bat noch?"));
  }
}

// Meldung zeigen, ohne einen gerade angekommenen Erkundungs-Bericht zu überschreiben
function reply(res) {
  setMessage(res.report ? `${res.report.text} – ${res.message || ""}` : res.message || "");
}

const ACTION_SOUND = { eat: "eat", overfeed: "eat", refuse: "refuse", clean: "wash", medicine: "happy", wake: "happy" };

async function act(action, extra = {}) {
  // wie viele Haufen lagen da? (für den Besen – danach sind sie ja weg)
  const poop = S.state && S.state.pet ? S.state.pet.poop : 0;
  try {
    const res = await api("/api/action", { action, ...extra });
    apply(res);
    reply(res);
    if (ACTION_SOUND[res.anim]) sfx(ACTION_SOUND[res.anim]);
    const pet = res.pet;
    if (res.anim && pet && pet.alive && !pet.asleep && pet.stage !== "Egg") {
      S.anim = { type: res.anim, food: extra.food, poop, start: S.tick };
    }
  } catch (e) {
    setMessage(e.message);
  }
}

// ------------------------------------------------------------ Einstellungen-Fenster
function openSettings() {
  sfx("menu");
  $("#set-user").textContent = S.state ? S.state.user.name : "–";
  $("#volume").value = settings.volume;
  $("#volume-out").textContent = settings.volume + " %";
  renderNotifySetting();
  refreshPush();
  renderFridgeSetting();
  const admin = S.state && S.state.user.admin;
  $("#invite-section").hidden = !admin;
  $("#cheat-section").hidden = !admin;
  $("#admin-section").hidden = !admin;
  if (admin) api("/api/invite").then(r => { $("#invite-code").textContent = r.code; }).catch(() => {});
  $("#friend-msg").textContent = "";
  api("/api/friends").then(renderFriends).catch(() => {});
  $("#settings").hidden = $("#scrim").hidden = false;
  $("#close-settings").focus();
}

// ---- Freunde (Einstellungen): Freundescode, hinzufügen, entfernen
function renderFriends(res) {
  $("#friend-code").textContent = res.code;
  const list = $("#friend-list");
  if (!res.friends.length) {
    list.innerHTML = `<li class="hint">${tr("Noch keine Freunde. Tauscht eure Freundescodes aus!")}</li>`;
    return;
  }
  list.replaceChildren(...res.friends.map(f => {
    const li = document.createElement("li");
    li.innerHTML = `<span class="dot ${f.online ? "on" : ""}"></span><b>${escapeHtml(f.name)}</b>
      <small>${f.online ? tr("online") : tr("offline")}</small>`;
    const b = document.createElement("button");
    b.className = "small";
    b.textContent = tr("Entfernen");
    b.onclick = () => {
      // zweimal drücken: Freundschaft endet für beide
      if (!b.dataset.sure) {
        b.dataset.sure = "1";
        b.textContent = tr("Wirklich?");
        b.className = "small danger";
        setTimeout(() => { if (b.isConnected) { delete b.dataset.sure; b.textContent = tr("Entfernen"); b.className = "small"; } }, 3000);
        return;
      }
      friendAction("remove", { name: f.name });
    };
    const look = document.createElement("button");
    look.className = "small primary";
    look.textContent = tr("Ansehen");
    look.title = tr("Welche Digimon hat {name}?", { name: f.name });
    look.onclick = () => openFriend(f.name);
    li.append(look, b);
    return li;
  }));
}

// ---- Profil eines Freundes: Partner, Sammlung, Digidex – der Server zeigt es nur Freunden
async function openFriend(name) {
  sfx("menu");
  closeSettings();
  $("#friend-panel-title").textContent = name;
  $("#friend-body").innerHTML = `<p class="hint">${tr("Lade ...")}</p>`;
  $("#friend-panel").hidden = $("#scrim").hidden = false;
  $("#close-friend").focus();
  try {
    renderFriendProfile((await api("/api/friends/profile", { name })).profile);
  } catch (e) {
    $("#friend-body").innerHTML = `<p class="hint">${escapeHtml(e.message)}</p>`;
  }
}

function friendMon(p) {
  const fig = document.createElement("figure");
  fig.className = "friend-mon";
  fig.append(monCanvas(p));
  const cap = document.createElement("figcaption");
  cap.innerHTML = `<b>${escapeHtml(p.nickname || p.name)}</b><small>${escapeHtml(p.nickname ? `${p.name} · ${p.stage_de}` : p.stage_de)}</small>`;
  fig.append(cap);
  if (p.dex) {
    // antippen = Digidex-Eintrag
    const a = document.createElement("a");
    a.href = `hilfe.html#digimon/${p.dex}`;
    a.title = tr("Digidex-Eintrag öffnen");
    a.append(fig);
    return a;
  }
  return fig;
}

function renderFriendProfile(p) {
  const body = $("#friend-body");
  body.replaceChildren();
  const status = document.createElement("p");
  status.className = "friend-status";
  status.innerHTML = `<span class="dot ${p.online ? "on" : ""}"></span>${p.online ? tr("online") : tr("offline")}`;
  const stats = document.createElement("div");
  stats.className = "friend-stats";
  stats.innerHTML = [
    [tr("Digidex"), `${p.dex} / ${p.dex_total}`],
    [tr("Erfolge"), `${p.achievements} / ${p.achievements_total}`],
    [tr("Siege"), p.wins],
    [tr("Siege gegen Freunde"), p.pvp_wins],
  ].map(([k, v]) => `<div><small>${escapeHtml(k)}</small><b>${escapeHtml(String(v))}</b></div>`).join("");
  body.append(status, stats);

  const partner = document.createElement("section");
  partner.innerHTML = `<h3>${tr("Partner")}</h3>`;
  if (p.partner) {
    const card = friendMon(p.partner);
    card.classList.add("big");
    partner.append(card);
    if (p.partner.stage !== "Egg") {
      partner.append(Object.assign(document.createElement("p"), { className: "hint",
        textContent: tr("{w} Siege in {b} Kämpfen", { w: p.partner.wins, b: p.partner.battles }) }));
    }
  } else {
    partner.append(Object.assign(document.createElement("p"), { className: "hint", textContent: tr("Gerade kein Partner.") }));
  }
  body.append(partner);

  const box = document.createElement("section");
  box.innerHTML = `<h3>${tr("Sammlung ({n})", { n: p.box.length + p.eggs.length })}</h3>`;
  if (p.box.length) {
    const grid = document.createElement("div");
    grid.className = "friend-mons";
    grid.append(...p.box.map(friendMon));
    box.append(grid);
  }
  if (p.eggs.length) {
    // Eier zusammenfassen: "3× Digi-Ei" (nur Event-Eier verraten ihre Sorte)
    const count = {};
    p.eggs.forEach(e => { count[e.name] = (count[e.name] || 0) + 1; });
    box.append(Object.assign(document.createElement("p"), { className: "hint",
      textContent: tr("Eier: {list}", { list: Object.entries(count).map(([n, c]) => `${c}× ${n}`).join(", ") }) }));
  }
  if (!p.box.length && !p.eggs.length) {
    box.append(Object.assign(document.createElement("p"), { className: "hint", textContent: tr("Die Sammlung ist leer.") }));
  }
  body.append(box);
}

function closeFriend() {
  $("#friend-panel").hidden = $("#scrim").hidden = true;
}

$("#close-friend").addEventListener("click", closeFriend);
$("#scrim").addEventListener("click", closeFriend);
$("#friend-back").addEventListener("click", () => { closeFriend(); openSettings(); });

async function friendAction(step, body) {
  try {
    const res = await api(`/api/friends/${step}`, body);
    renderFriends(res);
    $("#friend-msg").textContent = res.message;
    sfx(step === "add" ? "reward" : "confirm");
    return true;
  } catch (e) {
    $("#friend-msg").textContent = e.message;
    sfx("refuse");
    return false;
  }
}

$("#friend-add").addEventListener("submit", async e => {
  e.preventDefault();
  const input = e.target.elements.code;
  if (await friendAction("add", { code: input.value })) input.value = "";
});
$("#friend-copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText($("#friend-code").textContent);
    $("#friend-copy").textContent = tr("Kopiert!");
    setTimeout(() => { $("#friend-copy").textContent = tr("Kopieren"); }, 1500);
  } catch { /* ohne Zwischenablage einfach abschreiben */ }
});
$("#friend-newcode").addEventListener("click", () => friendAction("newcode", {}));

function closeSettings() {
  $("#settings").hidden = $("#scrim").hidden = true;
}

// ------------------------------------------------------------ Sprache (Deutsch / English)
// Gilt pro Gerät (static/i18n.js) und wird im Konto gespeichert -> auf allen Geräten gleich.
function renderLangSwitch() {
  document.querySelectorAll("[data-lang]").forEach(b => b.classList.toggle("primary", b.dataset.lang === I18N.lang));
}

async function setLang(lang) {
  if (lang === I18N.lang) return;
  I18N.set(lang);
  if (S.state) { try { await api("/api/lang", { lang }); } catch { /* dann eben nur dieses Gerät */ } }
  location.reload();                  // alles neu in der anderen Sprache aufbauen
}

// beim Anmelden: Sprache des Kontos übernehmen (oder die des Geräts im Konto merken)
async function syncLang(accountLang) {
  if (I18N.fromUrl && accountLang !== I18N.lang) {   // Link mit ?lang=… gilt als bewusste Wahl
    api("/api/lang", { lang: I18N.lang }).catch(() => {});
    return false;
  }
  if (accountLang && accountLang !== I18N.lang) {
    I18N.set(accountLang);
    location.reload();
    return true;
  }
  if (!accountLang) api("/api/lang", { lang: I18N.lang }).catch(() => {});
  return false;
}

document.querySelectorAll("[data-lang]").forEach(b => b.addEventListener("click", () => setLang(b.dataset.lang)));
renderLangSwitch();

// ------------------------------------------------------------ Spitznamen
// id = null: aktives Digimon, sonst eins aus der Sammlung
async function setNickname(id, name) {
  try {
    const res = await api("/api/nickname", { id, name });
    apply(res);
    if (res.collection) { S.box = res.collection.box; renderCollection(res.collection); }
    setMessage(res.message);
    sfx("confirm");
    return true;
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
    return false;
  }
}

$("#nick-edit").addEventListener("click", () => {
  const form = $("#nick-form");
  form.hidden = !form.hidden;
  const pet = S.state && S.state.pet;
  form.elements.nick.value = (pet && pet.nickname) || "";
  if (!form.hidden) form.elements.nick.focus();
});
$("#nick-form").addEventListener("submit", async e => {
  e.preventDefault();
  if (await setNickname(null, e.target.elements.nick.value)) e.target.hidden = true;
});
$("#nick-clear").addEventListener("click", async () => {
  if (await setNickname(null, "")) $("#nick-form").hidden = true;
});

// ------------------------------------------------------------ Rangliste (eigener Knopf oben)
async function openRanking() {
  sfx("menu");
  closeSettings();
  $("#ranking-panel").hidden = $("#scrim").hidden = false;
  $("#close-ranking").focus();
  if (!$("#achievements-view").hidden) loadAchievements();
  try {
    const r = await api("/api/ranking");
    const me = S.state && S.state.user.name;
    $("#ranking").innerHTML = r.ranking.length ? r.ranking.map(row => `
      <li class="${row.name === me ? "me" : ""}">
        <span><b>${escapeHtml(row.name)}</b>${row.cheated ? ` <small>(${tr("gecheatet")})</small>` : ""}
          <small>${row.partner ? tr("Partner: {name}", { name: escapeHtml(row.partner) }) : tr("kein Partner")}</small></span>
        <span class="score">${tr("{wins} Siege / {battles}", { wins: row.wins, battles: row.battles })}</span>
      </li>`).join("") : `<li class="hint">${tr("Noch keine Spieler.")}</li>`;
  } catch (e) {
    $("#ranking").innerHTML = `<li class="hint">${tr("Die Rangliste konnte nicht geladen werden.")}</li>`;
  }
}

// ------------------------------------------------------------ Shop (Bits -> Items)
// Bits gibt es beim Erkunden, in Kämpfen und selten beim Putzen (game/shop.py).
let shopItems = [];

async function openShop() {
  sfx("menu");
  closeSettings();
  $("#shop").hidden = $("#scrim").hidden = false;
  $("#close-shop").focus();
  try {
    const res = await api("/api/shop");
    shopItems = res.shop;
    candyOffers = res.candy_offers || [];
  } catch (e) {
    $("#shop-list").innerHTML = `<p class="hint">${escapeHtml(e.message)}</p>`;
    return;
  }
  renderShop();
  renderCandyTrade();
}

// ---- Tausch gegen Event-Items (nur während eines Events, z. B. Gruselbonbons -> Halloween-Ei)
let candyOffers = [];

function renderCandyTrade() {
  const box = $("#candy-trade");
  box.hidden = !candyOffers.length;
  if (!candyOffers.length) return;
  const have = bagCounts();
  const first = candyOffers[0];
  box.innerHTML = `<h3><canvas data-icon="candy"></canvas>${tr("Bonbon-Tausch")}<span>${
    tr("Du hast {n}× {item}", { n: have[first.item] || 0, item: escapeHtml(first.item_name) })}</span></h3>`
    + candyOffers.map(o => `<div class="shop-item">
        <canvas data-icon="egg"></canvas>
        <div><b>${escapeHtml(o.name)}</b><small>${escapeHtml(o.desc)}</small></div>
        <div class="shop-buy"><span class="shop-price">${tr("{n}× {item}", { n: o.cost, item: escapeHtml(o.item_name) })}</span>
          <button class="small primary" data-candy="${o.key}" ${(have[o.item] || 0) < o.cost ? "disabled" : ""}>${tr("Tauschen")}</button></div>
      </div>`).join("")
    + `<p class="hint">${tr("Das Halloween-Design und die Fledermäuse gibt es für Gruselbonbons im Tab „V-Pet-Designs“.")}</p>`;
  box.querySelectorAll("canvas[data-icon]").forEach(paintIcon);
  box.querySelectorAll("[data-candy]").forEach(b => b.addEventListener("click", async () => {
    try {
      const res = await api("/api/shop/candy", { key: b.dataset.candy });
      apply(res);
      candyOffers = res.candy_offers || [];
      renderCandyTrade();
      setMessage(res.message);
      sfx("reward");
    } catch (e) { setMessage(e.message); sfx("refuse"); }
  }));
}

function closeShop() {
  $("#shop").hidden = $("#scrim").hidden = true;
}

function renderShop() {
  const bits = (S.state && S.state.bits) || 0;
  const have = bagCounts();
  $("#shop-bits").textContent = bits;
  $("#shop-list").replaceChildren(...shopItems.map(it => {
    const row = document.createElement("div");
    // Daily Steal: steht ganz oben, heute günstiger (alter Preis durchgestrichen)
    row.className = "shop-item" + (it.steal ? " steal" : "");
    const off = it.steal && it.regular ? Math.round((1 - it.price / it.regular) * 100) : 0;
    row.innerHTML = `<canvas data-icon="${itemIcon(it)}"></canvas>
      <div>${it.steal ? `<span class="steal-kicker">${tr("Daily Steal – heute −{p} %", { p: off })}</span>` : ""}
        <b>${escapeHtml(it.name)}${it.only_shop ? `<span class="tag">${tr("nur im Shop")}</span>` : ""}${
        it.event && S.state.event ? `<span class="tag">${tr("nur während {event}", { event: escapeHtml(S.state.event.name) })}</span>` : ""
      }</b><small>${escapeHtml(it.desc)}</small>
        <small>${tr("Im Rucksack: {n}", { n: have[it.key] || 0 })}</small></div>
      <div class="shop-buy"><span class="shop-price">${it.steal ? `<s>${it.regular}</s> ` : ""}${tr("{n} Bits", { n: it.price })}</span></div>`;
    const buttons = row.querySelector(".shop-buy");
    for (const amount of [1, 5]) {
      const b = document.createElement("button");
      b.className = "small" + (amount === 1 ? " primary" : "");
      b.textContent = amount === 1 ? tr("Kaufen") : tr("5× für {n}", { n: it.price * 5 });
      b.disabled = it.price * amount > bits;
      b.addEventListener("click", () => buy(it.key, amount));
      buttons.append(b);
    }
    return row;
  }));
  // erst jetzt malen: die Farbe kommt vom Element auf der Seite
  $("#shop-list").querySelectorAll("canvas[data-icon]").forEach(paintIcon);
}

async function buy(item, amount) {
  try {
    const res = await api("/api/shop/buy", { item, amount });
    apply(res);
    shopItems = res.shop;
    renderShop();
    setMessage(res.message);
    sfx("reward");
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

// ---- V-Pet-Designs (zweiter Tab im Shop)
let themeList = [];

function shopTab(which) {
  const designs = which === "themes";
  $("#tab-shop-items").classList.toggle("active", !designs);
  $("#tab-shop-themes").classList.toggle("active", designs);
  $("#shop-items-view").hidden = designs;
  $("#shop-themes-view").hidden = !designs;
  if (designs) loadThemes();
}

async function loadThemes() {
  try {
    const res = await api("/api/themes");
    themeList = res.themes;
    decorList = res.decor || [];
    renderThemes();
    renderDecorShop();
  } catch (e) { $("#theme-list").innerHTML = `<p class="hint">${escapeHtml(e.message)}</p>`; }
}

// ---- Deko (unter den Designs): kaufen und an-/ausschalten
let decorList = [];

function renderDecorShop() {
  const bits = (S.state && S.state.bits) || 0;
  const have = bagCounts();
  $("#decor-list").replaceChildren(...decorList.map(d => {
    const card = document.createElement("div");
    card.className = "decor-card" + (d.available && d.on ? " on" : "");
    const cost = d.item ? tr("{n}× {item}", { n: d.items, item: d.item_name }) : tr("{n} Bits", { n: d.price });
    let note = d.owned ? tr("gekauft") : escapeHtml(cost);
    if (d.event && !d.owned) note += " · " + tr("gratis während des Events");
    card.innerHTML = `<div><b>${escapeHtml(d.name)}</b><small>${escapeHtml(d.desc)}</small><small>${note}</small></div>`;
    const actions = document.createElement("div");
    actions.className = "decor-actions";
    if (d.available) {
      const t = document.createElement("button");
      t.className = "small" + (d.on ? " primary" : "");
      t.textContent = d.on ? tr("An") : tr("Aus");
      t.title = d.on ? tr("Ausschalten") : tr("Einschalten");
      t.onclick = () => decorAction("toggle", { key: d.key, on: !d.on });
      actions.append(t);
    }
    if (!d.owned) {
      const b = document.createElement("button");
      b.className = "small";
      b.textContent = tr("Kaufen");
      b.disabled = d.item ? (have[d.item] || 0) < d.items : bits < d.price;
      b.onclick = () => decorAction("buy", { key: d.key });
      actions.append(b);
    }
    card.append(actions);
    return card;
  }));
}

async function decorAction(step, body) {
  try {
    const res = await api(`/api/decor/${step}`, body);
    apply(res);
    decorList = res.decor_list;
    renderDecorShop();
    renderShop();
    setMessage(res.message);
    sfx(step === "buy" ? "reward" : "confirm");
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

// Vorschau: kleines Gerät in den Farben des Designs, darin dein Digimon
function themePreview(t) {
  const c = document.createElement("canvas");
  c.width = 120;
  c.height = 84;
  const g = c.getContext("2d");
  const grad = g.createLinearGradient(0, 0, 120, 84);
  grad.addColorStop(0, t.device[0]);
  grad.addColorStop(0.5, t.device[1]);
  grad.addColorStop(1, t.device[2]);
  g.fillStyle = grad;
  g.fillRect(0, 0, 120, 84);
  g.fillStyle = t.lcd;
  g.fillRect(8, 8, 104, 68);
  const pet = S.state && S.state.pet;
  // 16 x 16 Pixel, je 3 px groß -> 48 px, mittig im Display (Versatz in Sprite-Pixeln)
  drawBitmap(g, pet && pet.dex ? sprite(pet.dex, "idle") : EGG, 12, 6, 3, t.pixel);
  return c;
}

function renderThemes() {
  const bits = (S.state && S.state.bits) || 0;
  const have = bagCounts();
  $("#theme-list").replaceChildren(...themeList.map(t => {
    const card = document.createElement("div");
    card.className = "theme-card" + (t.active ? " active" : "");
    card.append(themePreview(t));
    const cost = t.item ? tr("{n}× {item}", { n: t.items, item: t.item_name })
      : t.price ? tr("{n} Bits", { n: t.price }) : tr("gratis");
    card.insertAdjacentHTML("beforeend", `<b>${escapeHtml(t.name)}</b><small>${t.owned ? tr("gekauft") : escapeHtml(cost)}</small>`);
    const b = document.createElement("button");
    b.className = "small" + (t.active ? "" : " primary");
    if (t.active) { b.textContent = tr("Aktiv ✓"); b.disabled = true; }
    else if (t.owned) { b.textContent = tr("Benutzen"); b.onclick = () => themeAction("use", t.key); }
    else {
      b.textContent = tr("Kaufen");
      b.disabled = t.item ? (have[t.item] || 0) < t.items : bits < t.price;
      b.onclick = () => themeAction("buy", t.key);
    }
    card.append(b);
    return card;
  }));
}

async function themeAction(step, key) {
  try {
    const res = await api(`/api/theme/${step}`, { key });
    apply(res);
    themeList = res.themes;
    renderThemes();
    renderShop();
    setMessage(res.message);
    sfx(step === "buy" ? "reward" : "confirm");
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

$("#tab-shop-items").addEventListener("click", () => shopTab("items"));
$("#tab-shop-themes").addEventListener("click", () => shopTab("themes"));
$("#open-shop").addEventListener("click", openShop);
$("#close-shop").addEventListener("click", closeShop);
$("#scrim").addEventListener("click", closeShop);

function closeRanking() {
  $("#ranking-panel").hidden = $("#scrim").hidden = true;
}

// Tabs im Pokal-Fenster: Rangliste | Erfolge (+ Sammel-Fortschritt)
function rankingTab(which) {
  const ach = which === "achievements";
  $("#tab-ranking").classList.toggle("active", !ach);
  $("#tab-achievements").classList.toggle("active", ach);
  $("#ranking-view").hidden = ach;
  $("#achievements-view").hidden = !ach;
  $("#ranking-title").textContent = ach ? tr("Erfolge") : tr("Rangliste");
  if (ach) loadAchievements();
}

async function loadAchievements() {
  try {
    const p = await api("/api/progress");
    const done = p.achievements.filter(a => a.done).length;
    $("#dex-progress").innerHTML = `<span>${tr("Gesammelt")}</span><b>${p.owned.length} / ${p.total}</b>`
      + `<span>${tr("Erfolge")}</span><b>${done} / ${p.achievements.length}</b>`;
    $("#achievements").innerHTML = p.achievements.map(a => `
      <li class="${a.done ? "done" : ""}">
        <span class="mark">${a.done ? "✓" : ""}</span>
        <span><b>${escapeHtml(a.name)}</b><small>${escapeHtml(a.desc)}</small>
          ${a.done || a.need <= 1 ? "" : `<i class="bar"><i style="width:${Math.round(100 * a.have / a.need)}%"></i></i>
            <small>${a.have} / ${a.need}</small>`}</span>
        <span class="reward">${tr("+{n} Bits", { n: a.reward })}</span>
      </li>`).join("");
  } catch (e) {
    $("#achievements").innerHTML = `<li class="hint">${escapeHtml(e.message)}</li>`;
  }
}

$("#tab-ranking").addEventListener("click", () => rankingTab("ranking"));
$("#tab-achievements").addEventListener("click", () => rankingTab("achievements"));
$("#open-ranking").addEventListener("click", openRanking);
$("#close-ranking").addEventListener("click", closeRanking);
$("#scrim").addEventListener("click", closeRanking);

function renderNotifySetting() {
  const btn = $("#notify-toggle");
  const text = $("#notify-text");
  const iosInstall = isIos() && !isStandalone();
  $("#notify-ios").hidden = !iosInstall;
  $("#notify-test").hidden = !pushActive;
  $("#notify-test").disabled = pushBusy;
  btn.disabled = pushBusy;
  if (iosInstall) {
    btn.hidden = true;
    text.textContent = tr("Auf dem iPhone: VPet zuerst zum Home-Bildschirm hinzufügen (ab iOS 16.4).");
    return;
  }
  if (!canNotify) {
    btn.hidden = true;
    text.textContent = tr("Dein Browser unterstützt keine Benachrichtigungen.");
    return;
  }
  if (Notification.permission === "denied") {
    btn.hidden = true;
    text.textContent = isIos()
      ? tr("Erlaube Mitteilungen unter iPhone-Einstellungen → Mitteilungen → V-Pet.")
      : tr("Benachrichtigungen sind im Browser blockiert. Erlaube sie über das Schloss-Symbol neben der Adresse.");
    return;
  }
  const on = pushActive || (settings.notify && Notification.permission === "granted");
  btn.hidden = false;
  btn.textContent = on ? tr("Ausschalten") : tr("Aktivieren");
  text.textContent = pushActive
    ? tr("An auf diesem Gerät – auch wenn die App geschlossen ist. Meldungen kommen bei Rufen, Krankheit, Schlüpfen, Digitation und Rückkehr vom Erkunden.")
    : canPush() && pushKey
      ? tr("Meldet sich auf diesem Gerät auch bei geschlossener App. Zum Einschalten auf „Aktivieren“ tippen.")
      : tr("Meldet sich, wenn dein Digimon ruft, krank wird oder sich entwickelt, solange die Seite in einem Tab offen ist.");
}

$("#open-settings").addEventListener("click", openSettings);
$("#close-settings").addEventListener("click", closeSettings);
$("#scrim").addEventListener("click", closeSettings);

$("#volume").addEventListener("input", e => {
  settings.volume = Number(e.target.value);
  $("#volume-out").textContent = settings.volume + " %";
  saveSettings();
});
$("#volume").addEventListener("change", () => sfx("happy"));
$("#sound-test").addEventListener("click", () => sfx("evolve"));

function pushFeedback(text) {
  $("#notify-status").textContent = text;
  $("#notify-status").hidden = !text;
}

$("#notify-toggle").addEventListener("click", async () => {
  if (pushBusy || !canNotify) return;
  pushBusy = true;
  try {
    // Safari verlangt die Abfrage unmittelbar beim Antippen, vor jedem await.
    const permission = !pushActive && !settings.notify ? Notification.requestPermission() : null;
    pushFeedback("");
    renderNotifySetting();
    if (pushActive || settings.notify) {
      if (pushSubscription) {
        await request("/api/push/off", { endpoint: pushSubscription.endpoint });
        await pushSubscription.unsubscribe();
      }
      pushActive = false;
      pushSubscription = null;
      settings.notify = false;
    } else {
      const perm = await permission;
      if (perm !== "granted") return;
      if (canPush()) {
        const info = await request("/api/push");
        pushKey = info.key;
        if (!pushKey) throw new Error(tr("Push-Mitteilungen sind auf diesem Server nicht verfügbar."));
        const reg = await navigator.serviceWorker.ready;
        const key = Uint8Array.from(atob((pushKey + "=".repeat((4 - pushKey.length % 4) % 4)).replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0));
        let sub = await reg.pushManager.getSubscription();
        if (sub) {
          await request("/api/push/off", { endpoint: sub.endpoint });
          await sub.unsubscribe();
          sub = null;
        }
        sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
        try { await request("/api/push", sub.toJSON()); }
        catch (err) { await sub.unsubscribe(); throw err; }
        pushSubscription = sub;
        pushActive = true;
        settings.notify = false;
        pushFeedback(tr("Benachrichtigungen sind an"));
      } else {
        settings.notify = true;
      }
    }
  } catch (err) {
    pushFeedback(err.message || tr("Mitteilungen konnten nicht eingeschaltet werden. Versuche es erneut."));
  } finally {
    pushBusy = false;
    saveSettings();
    renderNotifySetting();
    refreshPush();
  }
});

$("#notify-test").addEventListener("click", async () => {
  if (pushBusy || !pushSubscription) return;
  pushBusy = true;
  pushFeedback("");
  renderNotifySetting();
  try {
    await request("/api/push/test", { endpoint: pushSubscription.endpoint });
    pushFeedback(tr("Test-Mitteilung gesendet. Schau in deine Mitteilungen."));
  } catch (err) { pushFeedback(err.message); }
  finally { pushBusy = false; await refreshPush(); }
});

$("#invite-copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText($("#invite-code").textContent);
    $("#invite-copy").textContent = tr("Kopiert!");
    setTimeout(() => { $("#invite-copy").textContent = tr("Kopieren"); }, 1500);
  } catch { /* ohne Zwischenablage einfach abschreiben */ }
});
$("#invite-new").addEventListener("click", async () => {
  try { $("#invite-code").textContent = (await api("/api/invite/new", {})).code; } catch { /* egal */ }
});

$("#logout").addEventListener("click", async () => {
  try { await api("/api/logout", {}); }
  catch (err) { setMessage(err.message); return; }
  pushActive = false;
  pushUser = null;
  pushSubscription = null;
  settings.notify = false;
  saveSettings();
  closeSettings();
  S.state = null;
  showAuth(false);
});

// ------------------------------------------------------------ Passwort
$("#pw-form").addEventListener("submit", async e => {
  e.preventDefault();
  const f = e.target.elements;
  try {
    const res = await api("/api/password", { old: f.old.value, new: f.namedItem("new").value });
    f.old.value = f.namedItem("new").value = "";
    setMessage(res.message);
    sfx("confirm");
  } catch (err) { setMessage(err.message); sfx("refuse"); }
});

// ------------------------------------------------------------ Handy-App (installierbar)
let installPrompt = null;
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => { /* ohne geht's auch */ });
}
window.addEventListener("beforeinstallprompt", e => {
  e.preventDefault();
  installPrompt = e;
  $("#install-btn").hidden = false;
});
$("#install-btn").addEventListener("click", async () => {
  if (!installPrompt) return;
  installPrompt.prompt();
  await installPrompt.userChoice;
  installPrompt = null;
  $("#install-btn").hidden = true;
});
if (matchMedia("(display-mode: standalone)").matches) {
  $("#install-text").textContent = tr("Läuft schon als App.");
}

// ------------------------------------------------------------ Kühlschrank
async function setFridge(on) {
  try {
    const res = await api("/api/fridge", { on });
    S.anim = null;
    S.mode = "main";
    apply(res);
    // Tür auf, Digimon rein / raus, Tür zu
    if (res.pet && res.pet.alive) S.anim = { type: on ? "fridge_in" : "fridge_out", start: S.tick };
    setMessage(res.message);
    sfx(on ? "menu" : "happy");
    renderFridgeSetting();
  } catch (e) { setMessage(e.message); }
}

function renderFridgeSetting() {
  const pet = S.state && S.state.pet;
  const btn = $("#fridge-toggle");
  btn.disabled = !(pet && pet.alive);
  btn.textContent = pet && pet.frozen ? tr("Auftauen") : tr("In den Kühlschrank");
}

$("#fridge-toggle").addEventListener("click", () => {
  const pet = S.state && S.state.pet;
  closeSettings();
  setFridge(!(pet && pet.frozen));
});

// ------------------------------------------------------------ Sammlung
function monCanvas(pet) {
  const c = document.createElement("canvas");
  const rows = pet.dex ? sprite(pet.dex, "idle") : EGG;
  c.width = c.height = 48;
  const g = c.getContext("2d");
  g.fillStyle = COLOR_BG;
  g.fillRect(0, 0, 48, 48);
  drawBitmap(g, rows, 0, 0, 3, COLOR_PX);
  return c;
}

// "Digi-Ei Version 1" -> "Version 1" (die Daten können auch schon englisch sein: "Digi-Egg …")
function lineLabel(line) {
  return S.data.lines[line].name.replace(/^Digi-(Ei|Egg) /, "");
}

// Name eines Eis: nur Event-Eier (z. B. Halloween) verraten ihre Sorte, alle anderen
// heißen einfach "Digi-Ei" – was schlüpft, ist eine Überraschung (wie game/data.py egg_name)
function eggLabel(line) {
  const l = S.data.lines[line];
  return l && l.event ? `${tr("Digi-Ei")} ${lineLabel(line)}` : tr("Digi-Ei");
}

function monCard(pet, active) {
  const card = document.createElement("div");
  card.className = "mon-card" + (active ? " active" : "");
  card.append(monCanvas(pet));
  const info = document.createElement("div");
  const what = pet.stage === "Egg" ? tr("Ei")
    : `${pet.nickname ? pet.name + " · " : ""}${pet.stage_de} · ${lineLabel(pet.line)}`;
  const title = escapeHtml(pet.stage === "Egg" ? eggLabel(pet.line) : pet.nickname || pet.name);
  info.innerHTML = `<b>${pet.dex ? `<a class="dex-link" href="hilfe.html#digimon/${pet.dex}"
    title="${tr("Digidex-Eintrag öffnen")}">${title}</a>` : title}</b><span class="sub">${escapeHtml(what)}${
    pet.stage === "Egg" ? "" : " · " + tr("Hunger {h}/4 · Kraft {s}/4", { h: pet.hunger, s: pet.strength })}</span>`;
  card.append(info);
  if (!active) {
    const actions = document.createElement("div");
    actions.className = "actions";
    const pick = document.createElement("button");
    pick.className = "small primary";
    pick.textContent = pet.stage === "Egg" ? tr("Ausbrüten") : tr("Aktiv setzen");
    pick.onclick = () => boxAction("/api/box/switch", pet.id);
    const free = document.createElement("button");
    free.className = "small";
    free.textContent = tr("Freilassen");
    free.onclick = () => {
      if (free.dataset.sure) return boxAction("/api/box/release", pet.id);
      free.dataset.sure = "1";
      free.textContent = tr("Wirklich freilassen?");
      free.classList.add("danger");
    };
    const trade = document.createElement("button");
    trade.className = "small";
    trade.textContent = tr("Tauschen");
    trade.onclick = () => {
      card.append(tradeForm(pet));
      trade.remove();
    };
    if (pet.trip) {
      // unterwegs beim Erkunden: nur zurückrufen geht
      const back = document.createElement("button");
      back.className = "small";
      back.textContent = tr("Zurückrufen");
      back.title = tr("Kommt sofort zurück – aber ohne Funde");
      back.onclick = () => boxAction("/api/box/recall", pet.id);
      actions.append(Object.assign(document.createElement("p"), { className: "hint trip-note",
        textContent: tr("Erkundet {area} – zurück in {time}.", { area: pet.trip.area_name, time: duration(pet.trip.minutes_left) }) }), back);
    } else {
      actions.append(pick, trade, free);
      if (pet.stage !== "Egg" && S.col) actions.append(tripRow(pet), nickRow(pet));
    }
    // Sanduhr geht auch in der Sammlung (verkürzt die Reise und das Warten auf die Digitation)
    const glass = pet.stage !== "Egg" && hourglassRow(pet);
    if (glass) actions.append(glass);
    // in eine andere Box legen
    if (S.col && pet.box !== undefined) {
      const row = document.createElement("div");
      row.className = "move-row";
      const sel = document.createElement("select");
      sel.className = "cheat-select";
      sel.setAttribute("aria-label", tr("Ziel-Box"));
      S.col.boxes.forEach((n, i) => {
        if (i === pet.box) return;
        const full = S.col.box.filter(p => p.box === i).length >= S.col.per_box;
        sel.append(Object.assign(new Option(`${n}${full ? tr(" (voll)") : ""}`, i), { disabled: full }));
      });
      const go = document.createElement("button");
      go.className = "small";
      go.textContent = tr("Verschieben");
      go.onclick = async () => {
        await boxAction("/api/box/move", pet.id, { box: Number(sel.value) });
        S.pcPick = null;
        if (S.col) renderCollection(S.col);
      };
      row.append(sel, go);
      actions.append(row);
    }
    card.append(actions);
  }
  return card;
}

// Spitzname für ein Digimon aus der Sammlung
function nickRow(pet) {
  const form = document.createElement("form");
  form.className = "move-row nick-row";
  form.innerHTML = `<input class="cheat-select" name="nick" maxlength="12" placeholder="${tr("Spitzname")}" aria-label="${tr("Spitzname")}"
    autocomplete="off"><button class="small" type="submit">${tr("Name geben")}</button>`;
  form.elements.nick.value = pet.nickname || "";
  form.onsubmit = e => { e.preventDefault(); setNickname(pet.id, form.elements.nick.value); };
  return form;
}

// Sanduhr aus dem Rucksack für ein Digimon aus der Sammlung (nur, wenn man eine hat) –
// geht nur, während es erkundet; sonst steht da, warum nicht
function hourglassRow(pet) {
  const glasses = ((S.state && S.state.inventory) || []).filter(it => it.count && it.key.startsWith("hourglass"));
  if (!glasses.length) return null;
  if (!pet.trip) {
    return Object.assign(document.createElement("p"), { className: "hint",
      textContent: tr("Sanduhr: geht hier nur, während es erkundet – in der Sammlung steht die Zeit still.") });
  }
  const row = document.createElement("div");
  row.className = "move-row";
  const sel = document.createElement("select");
  sel.className = "cheat-select";
  sel.setAttribute("aria-label", tr("Sanduhr"));
  glasses.forEach(it => sel.append(new Option(`${it.name} ×${it.count}`, it.key)));
  const go = document.createElement("button");
  go.className = "small";
  go.textContent = tr("Benutzen");
  go.title = tr("Schneller zurück und früher digitieren");
  go.onclick = () => boxAction("/api/item", pet.id, { item: sel.value });
  row.append(sel, go);
  return row;
}

// Erkunden aus der Sammlung: Gebiet + Dauer wählen (höchstens S.col.max_trips gleichzeitig)
function tripRow(pet) {
  const row = document.createElement("div");
  row.className = "move-row trip-row";
  const away = S.col.box.filter(p => p.trip).length;
  if (!pet.areas.length) {
    row.innerHTML = `<p class="hint">${tr("Erkunden geht ab Rookie.")}</p>`;
    return row;
  }
  if (away >= S.col.max_trips) {
    row.innerHTML = `<p class="hint">${tr("Erkunden: Es sind schon {n} Digimon aus der Sammlung unterwegs.", { n: S.col.max_trips })}</p>`;
    return row;
  }
  const area = document.createElement("select");
  area.className = "cheat-select";
  area.setAttribute("aria-label", tr("Gebiet"));
  pet.areas.forEach(k => area.append(new Option(S.col.area_names[k], k)));
  const time = document.createElement("select");
  time.className = "cheat-select trip-time";
  time.setAttribute("aria-label", tr("Dauer"));
  [[30, tr("{n} Min", { n: 30 })], [120, tr("{n} Std", { n: 2 })], [480, tr("{n} Std", { n: 8 })]]
    .forEach(([m, label]) => time.append(new Option(label, m)));
  const go = document.createElement("button");
  go.className = "small primary";
  go.textContent = tr("Erkunden");
  go.title = tr("Unterwegs: {n} / {max}", { n: away, max: S.col.max_trips });
  go.onclick = () => boxAction("/api/box/explore", pet.id, { area: area.value, minutes: Number(time.value) });
  row.append(area, time, go);
  return row;
}

// Formular „an wen tauschen / verschenken?“ unter einer Sammlungs-Karte
function tradeForm(pet) {
  const form = document.createElement("form");
  form.className = "actions trade-form";
  const friends = (S.playersList || []).map(p => `<option>${escapeHtml(p.name)}</option>`).join("");
  form.innerHTML = friends
    ? `<select class="cheat-select" name="to">${friends}</select>
       <label class="check"><input type="checkbox" name="gift"> ${tr("als Geschenk")}</label>
       <button class="small primary" type="submit">${tr("Angebot schicken")}</button>`
    : `<p class="hint">${tr("Noch keine Freunde – tauscht eure Freundescodes aus (Einstellungen → Freunde).")}</p>`;
  form.onsubmit = e => {
    e.preventDefault();
    tradeAction("offer", { pet_id: pet.id, name: form.elements.to.value, gift: form.elements.gift.checked });
  };
  return form;
}

function petLabel(p) {
  return p ? `${p.name} (${p.what})` : "?";
}

function renderTrades(trades) {
  $("#trades-section").hidden = !trades.length;
  const myBox = (S.box || []).map(p => `<option value="${p.id}">${escapeHtml(
    p.stage === "Egg" ? eggLabel(p.line) : `${p.name} (${p.stage_de})`)}</option>`).join("");
  $("#trade-list").replaceChildren(...trades.map(t => {
    const card = document.createElement("div");
    card.className = "mon-card trade" + (t.todo !== "wait" ? " active" : "");
    let text, buttons = "";
    const v = { partner: escapeHtml(t.partner), offer: escapeHtml(petLabel(t.offer)), counter: escapeHtml(petLabel(t.counter)) };
    if (t.todo === "answer") {
      text = t.gift ? tr("<b>{partner}</b> schenkt dir {offer}!", v)
        : tr("<b>{partner}</b> bietet dir {offer} an – was gibst du dafür?", v);
      buttons = t.gift
        ? `<button class="small primary" data-trade="gift">${tr("Annehmen")}</button>`
        : (myBox ? `<select class="cheat-select" data-counter>${myBox}</select>
                    <button class="small primary" data-trade="counter">${tr("Gegenangebot")}</button>`
          : `<span class="hint">${tr("Deine Sammlung ist leer – nichts zum Tauschen.")}</span>`);
      buttons += `<button class="small" data-trade="decline">${tr("Ablehnen")}</button>`;
    } else if (t.todo === "confirm") {
      text = tr("<b>{partner}</b> gibt dir für {offer}: <b>{counter}</b>", v);
      buttons = `<button class="small primary" data-trade="confirm">${tr("Tausch bestätigen")}</button>
                 <button class="small" data-trade="decline">${tr("Ablehnen")}</button>`;
    } else {
      text = t.incoming
        ? tr("Warte, bis <b>{partner}</b> den Tausch bestätigt ({counter} gegen {offer}).", v)
        : tr("Wartet auf <b>{partner}</b>: {offer}", v) + (t.gift ? tr(" (Geschenk)") : "");
      buttons = `<button class="small" data-trade="decline">${t.incoming ? tr("Ablehnen") : tr("Zurückziehen")}</button>`;
    }
    card.innerHTML = `<div class="trade-text">${text}</div><div class="actions">${buttons}</div>`;
    card.querySelectorAll("[data-trade]").forEach(b => b.addEventListener("click", () => {
      const step = b.dataset.trade;
      const extra = step === "counter" ? { pet_id: Number(card.querySelector("[data-counter]").value) } : {};
      tradeAction(step, { id: t.id, ...extra });
    }));
    return card;
  }));
}

async function tradeAction(step, body) {
  try {
    const res = await api(`/api/trade/${step}`, body);
    apply(res);
    S.box = res.collection.box;
    renderCollection(res.collection);
    renderTrades(res.trades);
    setMessage(res.message);
    sfx(step === "decline" ? "cancel" : "confirm");
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

// Die Sammlung ist in Boxen aufgeteilt wie der PC bei Pokémon: oben blättern (◀ ▶ oder
// Pfeiltasten), Digimon antippen -> darunter erscheinen Infos und Knöpfe.
function renderCollection(col) {
  S.col = col;
  const pet = S.state && S.state.pet;
  $("#box-active").replaceChildren(pet && pet.alive ? monCard(pet, true)
    : Object.assign(document.createElement("p"), { className: "hint", textContent: tr("Gerade kein lebendes Digimon.") }));
  const away = col.box.filter(p => p.trip).length;
  $("#box-title").textContent = tr("In der Sammlung ({n} / {max})", { n: col.box.length, max: col.box_size })
    + (away ? " · " + tr("{n} / {max} erkunden", { n: away, max: col.max_trips }) : "");
  const names = col.boxes, per = col.per_box;
  S.pcBox = Math.min(Math.max(S.pcBox || 0, 0), names.length - 1);
  const count = i => col.box.filter(p => p.box === i).length;
  const here = col.box.filter(p => p.box === S.pcBox);
  $("#box-name").innerHTML = `${escapeHtml(names[S.pcBox])}<small>${here.length}/${per}</small>`;
  $("#box-rename").hidden = true;
  $("#box-list").replaceChildren(...Array.from({ length: per }, (_, i) => {
    const slot = document.createElement("button");
    slot.className = "pc-slot";
    const p = here[i];
    if (!p) { slot.disabled = true; slot.setAttribute("aria-label", tr("leerer Platz")); return slot; }
    slot.append(monCanvas(p));
    slot.title = p.stage === "Egg" ? eggLabel(p.line)
      : `${p.nickname ? `${p.nickname} (${p.name})` : p.name} · ${p.stage_de}`;
    if (p.trip) {
      slot.classList.add("away");                      // beim Erkunden: blass + Wegweiser
      slot.title += " · " + tr("erkundet {area}", { area: p.trip.area_name });
      const mark = document.createElement("canvas");
      mark.className = "trip-mark";
      mark.width = mark.height = 8;
      drawBitmap(mark.getContext("2d"), ICONS.explore, 0, 0, 1, COLOR_PX);
      slot.append(mark);
    }
    slot.setAttribute("aria-label", slot.title);
    slot.classList.toggle("on", p.id === S.pcPick);
    slot.onclick = () => { S.pcPick = S.pcPick === p.id ? null : p.id; sfx("click"); renderCollection(col); };
    return slot;
  }));
  $("#box-tabs").replaceChildren(...names.map((n, i) => {
    const b = document.createElement("button");
    b.textContent = i + 1;
    b.title = `${n} (${count(i)}/${per})`;
    b.className = (i === S.pcBox ? "on" : "") + (count(i) >= per ? " full" : "");
    b.onclick = () => showBox(i);
    return b;
  }));
  const picked = col.box.find(p => p.id === S.pcPick);
  $("#box-detail").replaceChildren(...(picked ? [monCard(picked, false)] : []));
  $("#box-new-egg").hidden = !(S.state && S.state.free_egg);
  // Übersicht: was die Digimon aus der Sammlung zuletzt vom Erkunden mitgebracht haben
  const trips = col.trip_reports || [];
  $("#box-trips-section").hidden = !trips.length;
  $("#box-trips").innerHTML = trips.map(r =>
    `<li><time>${escapeHtml(new Date(r.t * 60000).toLocaleString(I18N.locale(), { day: "2-digit", month: "2-digit",
      hour: "2-digit", minute: "2-digit" }))}</time>${escapeHtml(r.text)}</li>`).join("");
  $("#box-memories-section").hidden = !col.memories.length;
  $("#box-memories").innerHTML = col.memories.map(m =>
    `<li><b>${escapeHtml(m.name)}</b> – ${escapeHtml(m.cause || tr("gestorben"))}${m.died ? ` (${new Date(m.died * 60000).toLocaleDateString(I18N.locale())})` : ""}</li>`).join("");
}

async function openCollection() {
  sfx("menu");
  closeSettings();
  try {
    const [col, trades, players] = await Promise.all([api("/api/box"), api("/api/trades"), api("/api/players")]);
    S.box = col.box;
    S.playersList = players.players;
    renderCollection(col);
    renderTrades(trades.trades);
    $("#collection").hidden = $("#scrim").hidden = false;
    $("#close-collection").focus();
  } catch (e) { setMessage(e.message); }
}

function closeCollection() {
  $("#collection").hidden = $("#scrim").hidden = true;
}

function showBox(i) {
  if (!S.col) return;
  const n = S.col.boxes.length;
  S.pcBox = (i + n) % n;
  S.pcPick = null;
  sfx("menu");
  renderCollection(S.col);
}

$("#box-prev").addEventListener("click", () => showBox(S.pcBox - 1));
$("#box-next").addEventListener("click", () => showBox(S.pcBox + 1));
$("#box-name").addEventListener("click", () => {
  const form = $("#box-rename");
  form.hidden = !form.hidden;
  form.elements.name.value = S.col.boxes[S.pcBox];
  if (!form.hidden) form.elements.name.select();
});
$("#box-rename").addEventListener("submit", async e => {
  e.preventDefault();
  try {
    const res = await api("/api/box/name", { box: S.pcBox, name: e.target.elements.name.value });
    renderCollection(res.collection);
    setMessage(res.message);
    sfx("confirm");
  } catch (err) { setMessage(err.message); sfx("refuse"); }
});

async function boxAction(path, id, extra = {}) {
  try {
    const res = await api(path, { id, ...extra });
    S.anim = null;
    S.mode = "main";
    apply(res);
    S.box = res.collection.box;
    renderCollection(res.collection);
    setMessage(res.message);
    sfx("confirm");
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

$("#open-collection").addEventListener("click", openCollection);
$("#close-collection").addEventListener("click", closeCollection);
$("#scrim").addEventListener("click", closeCollection);
$("#box-new-egg").addEventListener("click", async () => {
  await newEgg("/api/egg");
  try { renderCollection(await api("/api/box")); } catch (e) { setMessage(e.message); }
});

// ------------------------------------------------------------ Cheat-Menü (nur Admin)
const STAGE_ORDER = ["Fresh", "InTraining", "Rookie", "Champion", "Armor", "Ultimate", "Mega"];
const STAGE_SHORT = { Fresh: "Baby I", InTraining: "Baby II", Rookie: "Rookie",
  Champion: "Champion", Armor: "Armor", Ultimate: tr("Ultra"), Mega: "Mega" };

function fillCheatLists() {
  if ($("#cheat-mon").options.length || !S.data) return;
  const lineName = l => S.data.lines[l].name.replace(/^Digi-Ei /, "");
  for (const line of Object.keys(S.data.lines)) {
    const group = document.createElement("optgroup");
    group.label = lineName(line);
    const seen = new Set();
    S.data.evolutions.filter(e => e.line === line)
      .sort((a, b) => STAGE_ORDER.indexOf(a.stage) - STAGE_ORDER.indexOf(b.stage))
      .forEach(e => {
        if (seen.has(e.to)) return;
        seen.add(e.to);
        group.append(new Option(`${S.data.digimon[e.to].name} (${STAGE_SHORT[e.stage]})`, `${line}:${e.to}`));
      });
    $("#cheat-mon").append(group);
    $("#cheat-egg").append(new Option(lineName(line), line));
  }
  for (const it of (S.state && S.state.inventory) || []) $("#cheat-item").append(new Option(it.name, it.key));
}

function fillCheatValues() {
  const pet = S.state && S.state.pet;
  $("#cheat-day").checked = !!(S.state && S.state.always_day);
  $("#cheat-event").checked = !!(S.state && S.state.event_forced);
  if (!pet) return;
  const f = $("#cheat-values").elements;
  for (const key of ["hunger", "strength", "weight", "mistakes", "mistakes_total", "trainings",
    "overfeeds", "battles_stage", "wins_stage", "poop"]) {
    f[key].value = pet[key];
  }
  for (const key of ["power", "speed", "defense"]) f[key].value = pet.skills[key];
  $("#cheat-immortal").checked = pet.immortal;
  if (pet.dex) $("#cheat-mon").value = `${pet.line}:${pet.dex}`;
  $("#cheat-egg").value = pet.line;
}

function openCheats() {
  closeSettings();
  fillCheatLists();
  fillCheatValues();
  $("#cheats").hidden = $("#scrim").hidden = false;
  $("#close-cheats").focus();
}

function closeCheats() {
  $("#cheats").hidden = $("#scrim").hidden = true;
}

async function cheat(op, extra = {}) {
  try {
    const res = await api("/api/cheat", { op, ...extra });
    S.anim = null;
    apply(res);
    setMessage(res.message);
    sfx("confirm");
    fillCheatValues();
  } catch (e) {
    setMessage(e.message);
    sfx("refuse");
  }
}

$("#open-cheats").addEventListener("click", openCheats);
$("#close-cheats").addEventListener("click", closeCheats);
$("#scrim").addEventListener("click", closeCheats);
document.querySelectorAll("[data-warp]").forEach(b =>
  b.addEventListener("click", () => cheat("warp", { minutes: Number(b.dataset.warp) })));
document.querySelectorAll("[data-status]").forEach(b =>
  b.addEventListener("click", () => cheat("status", { what: b.dataset.status })));
$("#cheat-evolve").addEventListener("click", () => cheat("evolve_now"));
$("#cheat-values").addEventListener("submit", e => {
  e.preventDefault();
  const values = Object.fromEntries([...new FormData(e.target)].map(([k, v]) => [k, Number(v)]));
  cheat("set", { values });
});
$("#cheat-immortal").addEventListener("change", e => cheat("flags", { immortal: e.target.checked }));
$("#cheat-day").addEventListener("change", e => cheat("day", { on: e.target.checked }));
$("#cheat-event").addEventListener("change", e => cheat("event", { key: e.target.checked ? "halloween" : "" }));
$("#cheat-item-btn").addEventListener("click", () =>
  cheat("item", { item: $("#cheat-item").value, amount: Number($("#cheat-amount").value) || 1 }));
$("#cheat-bits").addEventListener("click", () => cheat("bits", { amount: 10 }));      // 10 × 10 Bits
$("#cheat-become").addEventListener("click", () => {
  const [line, dex] = $("#cheat-mon").value.split(":");
  cheat("become", { line, dex: Number(dex) });
});
$("#cheat-egg-btn").addEventListener("click", () => cheat("egg", { line: $("#cheat-egg").value }));
$("#cheat-revive").addEventListener("click", () => cheat("revive"));

// ------------------------------------------------------------ Anmeldung
let authMode = "login";

function showAuth(firstUser) {
  $("#console").hidden = true;
  $("#quiz").hidden = true;
  $("#auth").hidden = false;
  setAuthMode(firstUser ? "register" : authMode, firstUser);
}

function setAuthMode(mode, firstUser = false) {
  authMode = mode;
  const access = S.access || {};
  const closed = access.registration === "closed" && !firstUser;
  if (closed && mode === "register") mode = authMode = "login";
  $("#tab-register").hidden = closed;
  $("#tab-login").classList.toggle("active", mode === "login");
  $("#tab-register").classList.toggle("active", mode === "register");
  $("#invite-field").hidden = mode !== "register" || firstUser || access.registration === "open";
  $("#auth-form").elements.password.autocomplete = mode === "login" ? "current-password" : "new-password";
  $("#auth-submit").textContent = mode === "login" ? tr("Anmelden") : tr("Konto erstellen");
  $("#auth-hint").textContent = (access.maintenance ? tr("Gerade laufen Wartungsarbeiten – nur Admins können spielen.") + " " : "")
    + (access.announcement ? tr("Nachricht: {text}", { text: access.announcement }) + " " : "")
    + (firstUser ? tr("Du bist der Erste hier: Dein Konto braucht keinen Einladungscode und du wirst Admin.")
      : mode === "register" && access.registration !== "open"
        ? tr("Den Einladungscode bekommst du von dem, der den Server betreibt.") : "");
  $("#auth-error").textContent = "";
}

$("#tab-login").addEventListener("click", () => setAuthMode("login"));
$("#tab-register").addEventListener("click", async () => {
  const me = await api("/api/me").catch(() => ({}));
  S.access = me;
  setAuthMode("register", !!me.first_user);
});

$("#auth-form").addEventListener("submit", async e => {
  e.preventDefault();
  const f = e.target.elements;     // (form.name wäre der Formularname, nicht das Feld)
  $("#auth-submit").disabled = true;
  try {
    await api(authMode === "login" ? "/api/login" : "/api/register",
      { name: f.namedItem("name").value, password: f.password.value, invite: f.invite.value, lang: I18N.lang });
    f.password.value = "";
    sfx("confirm");
    await showGame();
  } catch (err) {
    $("#auth-error").textContent = err.message;
    sfx("refuse");
  } finally {
    $("#auth-submit").disabled = false;
  }
});

async function showGame() {
  $("#auth").hidden = true;
  $("#console").hidden = false;
  S.mode = "main";
  keysSig = "";
  await refresh();
  if (S.state && await syncLang(S.state.lang)) return;
  if (S.state && S.state.starter) return showQuiz();     // neues Konto: erst die Fragen, dann das Ei
  // mitten im Kampf neu geladen: die Kampf-Meldung stehen lassen, keine Begrüßung drüberschreiben
  if (S.mode !== "main") { checkNews(); return; }
  const pet = S.state && S.state.pet;
  const name = pet && pet.name;
  if (!pet) setMessage(tr("Hol dir dein erstes Digi-Ei!"));
  else if (pet.returned) setMessage(tr("{name} ist vom Erkunden zurück! Drück OK, dann geht's weiter.", { name }));
  else if (pet.frozen) setMessage(tr("{name} liegt im Kühlschrank. Taste 1 taut es auf.", { name }));
  else if (pet.away) {
    setMessage(tr("{name} ist unterwegs in {area} und kommt in {time} zurück.",
      { name, area: pet.away.area_name, time: duration(pet.away.minutes_left) }));
  }
  else if (pet.stage === "Egg") setMessage(tr("Dein Digi-Ei! Was wohl daraus schlüpft ..."));
  else if (pet.nap) setMessage(tr("{name} macht ein Nickerchen. Licht an weckt es.", { name }));
  else if (pet.alive && pet.call) setMessage(tr("{name} hat auf dich gewartet!", { name }));
  else if (pet.alive) setMessage(tr("{name} freut sich, dass du da bist!", { name }));
  checkNews();
}

// ------------------------------------------------------------ Fragenkatalog beim ersten Start
// Wie bei Pokémon Mystery Dungeon: ein paar Fragen -> Persönlichkeitstyp -> passendes
// erstes Digi-Ei. Fragen und Auswertung kommen vom Server (game/starter.py).
// Ablauf: Begrüßung (step -1) -> Fragen (step 0 …) -> Ergebnis (Q.result).
const Q = { questions: [], answers: [], step: -1, result: null, busy: false };

async function showQuiz() {
  $("#console").hidden = true;
  $("#auth").hidden = true;
  $("#quiz").hidden = false;
  $("#lcd-name").textContent = "???";
  Object.assign(Q, { questions: [], answers: [], step: -1, result: null, busy: false });
  renderQuiz();
  try {
    Q.questions = (await api("/api/starter")).questions;
  } catch (e) {
    $("#quiz-error").textContent = e.message;
  }
  renderQuiz();
}

function quizKey(label, hotkey, onClick, cls = "") {
  const b = document.createElement("button");
  b.className = `key ${cls}`;
  b.dataset.hotkey = hotkey;
  b.innerHTML = `<span>${escapeHtml(label)}</span>${hotkey ? `<small>${escapeHtml(hotkey)}</small>` : ""}`;
  b.addEventListener("click", onClick);
  return b;
}

function renderQuiz() {
  const total = Q.questions.length;
  const text = $("#quiz-text");
  const answers = $("#quiz-answers");
  const foot = $("#quiz-foot");
  answers.replaceChildren();
  foot.replaceChildren();
  text.classList.toggle("question", !Q.result && Q.step >= 0);
  // Fortschritt: ein Balken pro Frage (nur während der Fragen)
  $("#quiz-progress").hidden = Q.result || Q.step < 0 || !total;
  $("#quiz-progress").innerHTML = Array.from({ length: total }, (_, i) =>
    `<i class="${i < Q.step ? "on" : i === Q.step ? "now" : ""}"></i>`).join("");

  if (Q.result) {
    $("#quiz-kicker").textContent = tr("Dein Ergebnis");
    $("#quiz-title").innerHTML = tr("Du bist {type}!", { type: `<span class="quiz-type">${escapeHtml(Q.result.name)}</span>` });
    text.innerHTML = `${escapeHtml(Q.result.text)}<span class="quiz-egg">${
      tr("Dieses Digi-Ei passt zu dir: {egg}", { egg: `<b>${escapeHtml(Q.result.egg)}</b>` })}</span>`;
    answers.append(quizKey(tr("Ei annehmen!"), "1", finishQuiz, "primary"));
    return;
  }
  if (Q.step < 0) {
    $("#quiz-kicker").textContent = tr("Willkommen in der Digital World");
    $("#quiz-title").textContent = tr("Hallo, Tamer!");
    text.textContent = tr("Bevor dein Abenteuer beginnt, möchte ich dich kennenlernen. Beantworte {n} Fragen – "
      + "ganz ehrlich, es gibt kein Richtig oder Falsch. Danach bekommst du ein Digi-Ei, das zu dir passt.",
    { n: total || 6 });
    const go = quizKey(tr("Los geht's!"), "1", () => { sfx("confirm"); Q.step = 0; renderQuiz(); }, "primary");
    go.disabled = !total;
    answers.append(go);
    foot.append(Object.assign(document.createElement("button"), {
      className: "small", textContent: tr("Abmelden"), onclick: () => $("#logout").click() }));
    return;
  }
  const q = Q.questions[Q.step];
  $("#quiz-kicker").textContent = tr("Frage {n} von {total}", { n: Q.step + 1, total });
  $("#quiz-title").textContent = "";
  text.textContent = q.text;
  q.answers.forEach((label, i) => answers.append(quizKey(label, String(i + 1), () => answerQuiz(i))));
  if (Q.step > 0) {
    foot.append(Object.assign(document.createElement("button"), {
      className: "small", textContent: tr("← Vorherige Frage"),
      onclick: () => { sfx("cancel"); Q.step--; renderQuiz(); } }));
  }
}

function answerQuiz(i) {
  if (Q.busy) return;
  Q.answers[Q.step] = [Q.questions[Q.step].id, i];
  Q.answers.length = Q.step + 1;
  if (Q.step + 1 < Q.questions.length) {
    sfx("menu");
    Q.step++;
    return renderQuiz();
  }
  submitQuiz();
}

async function submitQuiz() {
  Q.busy = true;
  $("#quiz-kicker").textContent = tr("Einen Moment …");
  try {
    const res = await api("/api/starter", { answers: Q.answers });
    Q.result = res.result;
    apply(res);                          // das neue Ei steht jetzt auf dem Display
    $("#lcd-name").textContent = res.pet ? res.pet.name : "???";
    sfx("evolve");
  } catch (e) {
    $("#quiz-error").textContent = e.message;
    sfx("refuse");
  } finally {
    Q.busy = false;
  }
  renderQuiz();
}

function finishQuiz() {
  sfx("confirm");
  $("#quiz").hidden = true;
  showGame();
}

// Tasten im Fragenkatalog: Zahlen = Antworten, Enter = Hauptknopf, Esc = vorherige Frage
function quizKeydown(e) {
  if (e.repeat) return;
  const keys = [...$("#quiz-answers").querySelectorAll("button:not(:disabled)")];
  const hit = e.key === "Enter" ? keys.find(b => b.classList.contains("primary"))
    : keys.find(b => b.dataset.hotkey === e.key);
  if (hit) { e.preventDefault(); hit.click(); return; }
  if (e.key === "Escape" && !Q.result && Q.step > 0) { Q.step--; renderQuiz(); }
}

// ------------------------------------------------------------ Changelog ("Was ist neu?")
// Einträge stehen in static/changelog.json (neueste zuerst). Was man schon gesehen
// hat, merkt sich das Gerät – Neues wird einmal oben angekündigt.
const NEWS_KEY = "vpet.newsSeen";
let changelog = null;

async function loadChangelog() {
  if (!changelog) changelog = await (await fetch("/changelog.json", { cache: "no-store" })).json();
  return changelog;
}

// Titel / Punkte eines Eintrags in der gewählten Sprache (englisch, falls vorhanden)
const entryTitle = e => (I18N.lang === "en" && e.title_en) || e.title;
const entryItems = e => (I18N.lang === "en" && e.items_en && e.items_en.length ? e.items_en : e.items) || [];

function newsSeen() {
  try { return localStorage.getItem(NEWS_KEY); } catch { return null; }
}

function markNewsSeen() {
  $("#news-bar").hidden = true;
  $("#open-changelog").classList.remove("badge-dot");
  if (!changelog || !changelog.length) return;
  try { localStorage.setItem(NEWS_KEY, changelog[0].id); } catch { /* egal */ }
}

async function checkNews() {
  try {
    const list = await loadChangelog();
    if (!list.length || newsSeen() === list[0].id) return;
    // alles vor dem zuletzt gesehenen Eintrag ist neu – mehr als einer? dann sagen
    const seenAt = list.findIndex(e => e.id === newsSeen());
    const more = (seenAt === -1 ? 1 : seenAt) - 1;
    $("#news-title").textContent = entryTitle(list[0]) + (more > 0 ? tr(" (+{n} weitere)", { n: more }) : "");
    $("#news-bar").hidden = false;
    $("#open-changelog").classList.add("badge-dot");          // Punkt am Knopf: es gibt Neues
  } catch { /* ohne Changelog geht's auch */ }
}

async function openChangelog() {
  sfx("menu");
  closeSettings();
  const seen = newsSeen();
  const box = $("#changelog-list");
  try {
    const list = await loadChangelog();
    // alles bis zum zuletzt gesehenen Eintrag ist "neu"
    const seenAt = list.findIndex(e => e.id === seen);
    box.innerHTML = list.map((e, i) => `
      <section class="entry${seenAt === -1 ? (i === 0 ? " fresh" : "") : i < seenAt ? " fresh" : ""}">
        <time datetime="${escapeHtml(e.date)}">${e.version ? `Version ${escapeHtml(e.version)} · ` : ""}${
          new Date(e.date + "T12:00").toLocaleDateString(I18N.locale(), { day: "numeric", month: "long", year: "numeric" })}</time>
        <h3>${escapeHtml(entryTitle(e))}</h3>
        <ul>${entryItems(e).map(it => `<li>${escapeHtml(it)}</li>`).join("")}</ul>
      </section>`).join("");
  } catch {
    box.innerHTML = `<p class="hint">${tr("Der Changelog konnte nicht geladen werden.")}</p>`;
  }
  $("#changelog").hidden = $("#scrim").hidden = false;
  $("#close-changelog").focus();
  markNewsSeen();
}

function closeChangelog() {
  $("#changelog").hidden = $("#scrim").hidden = true;
}

// ------------------------------------------------------------ Merkliste
// Im Digimon-Finder gemerkte Ziele. Gezeigt wird der Weg vom aktuellen Digimon dorthin:
// erledigte Schritte fallen nach jeder Digitation weg, der nächste Schritt zeigt live,
// was schon passt.
function wishTargets() {
  return (S.state && S.state.wishlist) || [];
}

// Rucksack als {Item-Key: Anzahl} (für Armor-Eier auf der Merkliste)
function bagCounts() {
  return Object.fromEntries(((S.state && S.state.inventory) || []).map(it => [it.key, it.count]));
}

// Wie steht das aktuelle Digimon zu einem Ziel? {state: "reached"|"path"|"unreachable"|"wait", path}
function wishStatus(pet, target) {
  if (!pet || !pet.alive) return { state: "wait", text: tr("Dafür brauchst du ein lebendes Digimon.") };
  if (!pet.dex) return { state: "wait", text: tr("Dein Ei schlüpft gleich – dann geht's los.") };
  if (pet.dex === target) return { state: "reached" };
  const path = Rules.pathTo(pet.dex, target, pet.line);
  return path ? { state: "path", path } : { state: "unreachable" };
}

// kurzer Hinweis unter "Nächste Digitation": NUR das Ziel dieses Digimon (pet.goal) –
// Pläne anderer Digimon aus der Merkliste stehen hier nicht mehr
function renderGoal(pet) {
  const box = $("#goal");
  if (!S.data || !pet || !pet.alive || !pet.dex) { box.hidden = true; return; }
  const target = pet.goal;
  if (!target || !S.data.digimon[target]) {
    // noch kein Ziel: dezenter Hinweis, falls auf der Merkliste etwas steht – mit ✕ wegklickbar
    // (gilt dann für alle Digimon auf diesem Gerät; ein festgelegtes Ziel wird weiter angezeigt)
    box.hidden = !wishTargets().length || noGoalHintHidden();
    box.innerHTML = `<b>★</b> ${tr("Kein Ziel für {name} – tippe hier, um eins aus der Merkliste festzulegen.",
      { name: escapeHtml(pet.nickname || pet.name) })}<span class="goal-x" data-hide-goal role="button"
      title="${tr("Hinweis ausblenden")}" aria-label="${tr("Hinweis ausblenden")}">✕</span>`;
    return;
  }
  const st = wishStatus(pet, target);
  const name = S.data.digimon[target].name;
  if (st.state === "reached") {
    box.innerHTML = `<b>★ ${tr("Ziel erreicht")}</b> ${tr("Du hast {name}!", { name: escapeHtml(name) })}`;
  } else if (st.state === "path") {
    const step = st.path[0];
    const next = Rules.nextForm(pet);
    // Armor-Digitation: auf Kurs, sobald das Armor-Ei im Rucksack ist
    const onTrack = step.rule.item ? bagCounts()[step.rule.item] > 0 : next && next.to === step.to;
    const how = step.rule.item ? tr("„{item}“ benutzen", { item: Rules.itemName(step.rule.item) }) : Rules.ruleText(step.rule);
    box.innerHTML = `<b>★ ${tr("Ziel {name}", { name: escapeHtml(name) })}</b> `
      + tr("Als Nächstes {name}:", { name: escapeHtml(S.data.digimon[step.to].name) }) + " "
      + `${escapeHtml(how)}<span class="${onTrack ? "ok" : "warn"}">`
      + `${onTrack ? (step.rule.item ? tr("im Rucksack ✓") : tr("auf Kurs ✓")) : tr("noch nicht ✗")}</span>`;
  } else {
    box.innerHTML = `<b>★ ${tr("Ziel {name}", { name: escapeHtml(name) })}</b> `
      + `<span class="warn">${tr("von hier aus nicht mehr erreichbar ✗")}</span>`;
  }
  box.hidden = false;
}

function renderWishlist() {
  const box = $("#wish-list");
  const pet = S.state && S.state.pet;
  const targets = wishTargets();
  if (!targets.length) {
    box.innerHTML = `<p class="hint">${tr("Noch nichts gemerkt. Öffne den Digimon-Finder und tippe bei einem Digimon auf <b>☆ Merken</b>.")}</p>`;
    return;
  }
  box.innerHTML = "";
  // Ziel des aktiven Digimon ganz oben und aufgeklappt, die anderen eingeklappt
  const goal = pet && pet.alive && pet.dex ? pet.goal : null;
  const who = pet ? escapeHtml(pet.nickname || pet.name) : "";
  if (pet && pet.alive && pet.dex && !goal) {
    box.insertAdjacentHTML("beforeend", `<p class="hint">${tr("Wähle ein Ziel für {name} – dann zeigt das Spiel nur noch diesen Weg an.", { name: who })}</p>`);
  }
  for (const target of [...targets].sort((a, b) => (b === goal) - (a === goal))) {
    const d = S.data.digimon[target];
    const isGoal = target === goal;
    const card = document.createElement("section");
    card.className = "wish" + (isGoal ? " wish-goal" : "");
    const head = document.createElement("header");
    head.append(monCanvas({ dex: target }));
    const goalBtn = !pet || !pet.alive || !pet.dex ? ""
      : isGoal ? `<button class="small primary" data-goal="" title="${tr("Ziel entfernen")}">${tr("Ziel ✓")}</button>`
        : `<button class="small" data-goal="${target}">${tr("Als Ziel")}</button>`;
    head.insertAdjacentHTML("beforeend", `<span class="wish-name"><b>${escapeHtml(d.name)}</b>
      <small>${isGoal ? tr("Ziel von {name}", { name: who }) + " · " : ""}${Rules.STAGE_DE[d.stage]}${
        Rules.ATTR_DE[d.attribute] ? " · " + Rules.ATTR_DE[d.attribute] : ""}</small></span>
      <span class="wish-actions">${goalBtn}
        <a class="small" href="hilfe.html?ziel=${target}#finder">Finder</a>
        <button class="small" data-unwish="${target}" aria-label="${tr("Von der Merkliste nehmen")}">✕</button></span>`);
    card.append(head);
    // andere Ziele: Weg nur auf Wunsch (eingeklappt)
    const body = isGoal ? card : document.createElement("details");
    if (!isGoal) {
      body.insertAdjacentHTML("beforeend", `<summary>${tr("Weg anzeigen")}</summary>`);
      card.append(body);
    }
    if (!isGoal) {
      // offen bleiben, auch wenn die Liste neu gezeichnet wird (alle paar Sekunden)
      body.open = S.wishOpen.has(target);
      body.addEventListener("toggle", () => { if (body.open) S.wishOpen.add(target); else S.wishOpen.delete(target); });
    }
    const st = wishStatus(pet, target);
    if (st.state === "wait") body.insertAdjacentHTML("beforeend", `<p class="hint">${escapeHtml(st.text)}</p>`);
    else if (st.state === "reached") body.insertAdjacentHTML("beforeend", `<p class="ok">${tr("Geschafft – das ist dein Digimon!")}</p>`);
    else if (st.state === "unreachable") {
      const eggs = [...new Set(S.data.evolutions.filter(e => e.to === target).map(e => lineLabel(e.line)))];
      body.insertAdjacentHTML("beforeend", `<p class="warn">${tr("Von {name} aus nicht mehr erreichbar.", { name: escapeHtml(pet.name) })}</p>
        <p class="hint">${tr("Kommt aus: {eggs}.", { eggs: eggs.map(l => tr("Digi-Ei {line}", { line: escapeHtml(l) })).join(", ") })}</p>`);
    } else {
      const ol = document.createElement("ol");
      ol.className = "wish-steps";
      st.path.forEach((step, i) => {
        const li = document.createElement("li");
        li.append(monCanvas({ dex: step.to }));
        const stop = Rules.blocked(step.rule);
        let html = `<div><b>${escapeHtml(S.data.digimon[step.to].name)}</b>
          <small>${Rules.STAGE_DE[step.stage]}</small>${stop ? `<span class="tag">${stop}</span>` : ""}
          <p>${tr("Bedingung: {rule}", { rule: escapeHtml(Rules.ruleText(step.rule)) })}</p>`;
        if (i === 0) {
          // der nächste Schritt: was passt schon, was fehlt noch?
          li.classList.add("now");
          html += `<ul class="checks">${Rules.progress(step.rule, pet, bagCounts()).map(p =>
            `<li class="${p.ok ? "ok" : "warn"}">${p.ok ? "✓" : "✗"} ${escapeHtml(p.text)}</li>`).join("")}</ul>`;
          const next = Rules.nextForm(pet);
          if (step.rule.item) {
            html += `<p class="hint">${tr("Ohne Armor-Ei digitiert es nach Ablauf der Zeit ganz normal weiter – also rechtzeitig benutzen.")}</p>`;
          } else if (next && next.to !== step.to) {
            html += `<p class="warn">${tr("Stand jetzt würde es zu {name}.", { name: escapeHtml(S.data.digimon[next.to].name) })}</p>`;
          } else if (next) html += `<p class="ok">${tr("Stand jetzt klappt es!")}</p>`;
          if (pet.evolve_in) html += `<p class="hint">${tr("Digitation in {time}.", { time: duration(pet.evolve_in) })}</p>`;
        } else {
          const r = Rules.recipe(step);
          if (r.example && !stop) html += `<p class="hint">${tr("Z. B. {example}.", { example: escapeHtml(Rules.exampleText(r.example)) })}</p>`;
        }
        li.insertAdjacentHTML("beforeend", html + "</div>");
        ol.append(li);
      });
      body.append(ol);
    }
    box.append(card);
  }
}
S.wishOpen = new Set();          // aufgeklappte Wege in der Merkliste

// Ziel für das aktive Digimon setzen (dex) oder entfernen (null)
async function setGoal(dex) {
  try {
    const res = await api("/api/goal", { dex });
    apply(res);
    renderWishlist();
    setMessage(res.message);
    sfx("confirm");
  } catch (err) { setMessage(err.message); sfx("refuse"); }
}

// ------------------------------------------------------------ Event-Tab (Story, Belohnungen, Angebote)
const EVENT_CLOSED_KEY = "vpet.eventClosed";

function eventTag(ev) {
  return `${ev.key}-${new Date().getFullYear()}`;
}

function eventClosed(ev) {
  try { return localStorage.getItem(EVENT_CLOSED_KEY) === eventTag(ev); } catch { return false; }
}

function setEventClosed(closed) {
  const ev = S.state && S.state.event;
  if (!ev) return;
  try {
    if (closed) localStorage.setItem(EVENT_CLOSED_KEY, eventTag(ev));
    else localStorage.removeItem(EVENT_CLOSED_KEY);
  } catch { /* ohne Speicher: nur bis zum Neuladen */ }
  $("#event-bar").hidden = closed;
}

async function openEvent() {
  sfx("menu");
  closeSettings();
  $("#event-panel").hidden = $("#scrim").hidden = false;
  $("#close-event").focus();
  try {
    renderEvent((await api("/api/event")).event);
  } catch (e) {
    $("#event-body").innerHTML = `<p class="hint">${escapeHtml(e.message)}</p>`;
  }
}

function closeEvent() {
  $("#event-panel").hidden = $("#scrim").hidden = true;
}

// kleines LCD mit einem Digimon (für die Reihe des Event-Eis)
function eventSprite(dex) {
  const c = document.createElement("canvas");
  c.width = c.height = 48;
  const g = c.getContext("2d");
  g.fillStyle = COLOR_BG;
  g.fillRect(0, 0, 48, 48);
  drawBitmap(g, sprite(dex, "idle"), 0, 0, 3, COLOR_PX);
  c.title = S.data.digimon[dex].name;
  return c;
}

function renderEvent(ev) {
  const body = $("#event-body");
  if (!ev) {
    $("#event-panel-title").textContent = tr("Event");
    body.innerHTML = `<p class="hint">${tr("Gerade läuft kein Event.")}</p>`;
    return;
  }
  $("#event-panel-title").textContent = ev.name;
  const days = ev.days_left === 1 ? tr("letzter Tag!") : tr("noch {n} Tage", { n: ev.days_left });
  const offers = ev.offers.map(o => `<li>${escapeHtml(o.text)}${o.owned ? ` <span class="tag">${tr("gekauft")}</span>` : ""}</li>`).join("");
  const egg = ev.egg && S.data ? `<section class="ev-egg">
      <h3>${escapeHtml(ev.egg.name)}</h3>
      <p class="hint">${tr("Aus diesem Ei wird immer dieselbe Reihe – egal, wie du dich kümmerst:")}</p>
      <div class="ev-chain" id="ev-chain"></div>
      <p class="hint">${escapeHtml(ev.egg.chain.map(d => S.data.digimon[d].name).join(" → "))}</p>
    </section>` : "";
  body.innerHTML = `
    <section class="ev-hero">
      <canvas data-icon="${escapeHtml(ev.icon)}"></canvas>
      <div><b>${escapeHtml(ev.from)} – ${escapeHtml(ev.until)}</b><span>${days}</span></div>
      <button class="small" id="ev-banner">${eventClosed(ev) ? tr("Banner wieder anzeigen") : tr("Banner ausblenden")}</button>
    </section>
    <section class="ev-story">
      <h3>${tr("Die Geschichte")}</h3>
      ${ev.story.map(p => `<p>${escapeHtml(p)}</p>`).join("")}
    </section>
    <section>
      <h3>${tr("Belohnungen")}</h3>
      <p class="hint">${tr("{p} % der wilden Digimon sind gerade Geister (Liste unten).", { p: ev.ghost_chance })}</p>
      <ul class="ev-list">${ev.rewards.map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul>
    </section>
    ${egg}
    <section>
      <h3>${tr("Im Shop & zum Tauschen")}</h3>
      <ul class="ev-list">${offers}</ul>
      <div class="row">
        <button class="small primary" data-ev-shop="items">${tr("Zum Shop")}</button>
        <button class="small" data-ev-shop="themes">${tr("Designs & Deko")}</button>
      </div>
    </section>
    <section>
      <h3>${tr("Geister")}</h3>
      <p class="ev-ghosts">${ev.ghosts.map(d => `<span>${escapeHtml(S.data ? S.data.digimon[d].name : String(d))}</span>`).join("")}</p>
    </section>`;
  body.querySelectorAll("canvas[data-icon]").forEach(paintIcon);
  if (ev.egg && S.data) $("#ev-chain").append(...ev.egg.chain.map(eventSprite));
  body.querySelectorAll("[data-ev-shop]").forEach(b => b.addEventListener("click", async () => {
    closeEvent();
    await openShop();
    shopTab(b.dataset.evShop);
  }));
  $("#ev-banner").addEventListener("click", () => {
    setEventClosed(!eventClosed(ev));
    renderEvent(ev);
  });
}

$("#open-event").addEventListener("click", openEvent);
$("#event-more").addEventListener("click", openEvent);
$("#close-event").addEventListener("click", closeEvent);
$("#scrim").addEventListener("click", closeEvent);
$("#event-close").addEventListener("click", () => {
  setEventClosed(true);
  setMessage(tr("Banner ausgeblendet – das Event findest du jederzeit oben in der Leiste (Event-Symbol)."));
});

function openWishlist() {
  sfx("menu");
  closeSettings();
  renderWishlist();
  $("#wishlist").hidden = $("#scrim").hidden = false;
  $("#close-wishlist").focus();
}

function closeWishlist() {
  $("#wishlist").hidden = $("#scrim").hidden = true;
}

$("#open-wishlist").addEventListener("click", openWishlist);
// „Kein Ziel“-Hinweis: ✕ blendet ihn aus (pro Gerät), der Rest öffnet die Merkliste
const NO_GOAL_KEY = "vpet.noGoalHintHidden";

function noGoalHintHidden() {
  if (S.noGoalHidden) return true;
  try { return localStorage.getItem(NO_GOAL_KEY) === "1"; } catch { return false; }
}

$("#goal").addEventListener("click", e => {
  if (e.target.closest("[data-hide-goal]")) {
    S.noGoalHidden = true;
    try { localStorage.setItem(NO_GOAL_KEY, "1"); } catch { /* ohne Speicher: bis zum Neuladen */ }
    $("#goal").hidden = true;
    sfx("cancel");
    return setMessage(tr("Hinweis ausgeblendet – ein Ziel legst du jederzeit in der Merkliste (★ oben) fest."));
  }
  openWishlist();
});
$("#close-wishlist").addEventListener("click", closeWishlist);
$("#scrim").addEventListener("click", closeWishlist);
$("#wish-list").addEventListener("click", async e => {
  const goalBtn = e.target.closest("[data-goal]");
  if (goalBtn) return setGoal(goalBtn.dataset.goal ? Number(goalBtn.dataset.goal) : null);
  const btn = e.target.closest("[data-unwish]");
  if (!btn) return;
  try {
    const res = await api("/api/wishlist", { dex: Number(btn.dataset.unwish), on: false });
    S.state.wishlist = res.wishlist;
    if (S.state.pet && S.state.pet.goal === Number(btn.dataset.unwish)) S.state.pet.goal = null;
    renderWishlist();
    renderGoal(S.state.pet);
  } catch (err) { setMessage(err.message); }
});

$("#open-changelog").addEventListener("click", openChangelog);
$("#news-open").addEventListener("click", openChangelog);
$("#news-close").addEventListener("click", markNewsSeen);
$("#close-changelog").addEventListener("click", closeChangelog);
$("#scrim").addEventListener("click", closeChangelog);

// ------------------------------------------------------------ Datenregen im Hintergrund
function startRain() {
  const c = $("#rain");
  const g = c.getContext("2d");
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const CHARS = "01ABCDEF<>/{}#";
  const SIZE = 16;
  let drops = [];
  const resize = () => {
    c.width = c.clientWidth;
    c.height = c.clientHeight;
    drops = Array.from({ length: Math.ceil(c.width / SIZE) }, () => Math.random() * c.height / SIZE);
  };
  new ResizeObserver(resize).observe(c);
  resize();
  const frame = () => {
    g.fillStyle = RAIN.fade;                    // alte Zeichen verblassen
    g.fillRect(0, 0, c.width, c.height);
    g.font = `${SIZE - 2}px Silkscreen, monospace`;
    drops.forEach((y, i) => {
      g.fillStyle = Math.random() < .04 ? RAIN.b : RAIN.a;   // Farben aus dem V-Pet-Design
      g.fillText(CHARS[Math.floor(Math.random() * CHARS.length)], i * SIZE, y * SIZE);
      drops[i] = y * SIZE > c.height && Math.random() > .97 ? 0 : y + 1;
    });
  };
  if (still) { for (let i = 0; i < 60; i++) frame(); return; }
  setInterval(frame, 70);
}

// ------------------------------------------------------------ Start
I18N.translatePage();                  // feste Texte aus index.html (nur bei Englisch)
document.querySelectorAll("canvas[data-icon]").forEach(paintIcon);

async function start() {
  fitLcd();
  startRain();
  // Digimon-Daten laden – klappt es nicht (Server startet noch?), nach kurzer Zeit nochmal
  for (let tries = 1; !S.data; tries++) {
    try {
      const res = await fetch("/data/digimon.json");
      if (!res.ok) throw new Error(res.status);
      S.data = await res.json();
      Rules.use(S.data);                   // Regeln erklären / Wege finden (static/rules.js)
    } catch {
      setMessage(tr("Keine Verbindung zum Server. Neuer Versuch ..."));
      await new Promise(ok => setTimeout(ok, Math.min(10000, 1000 * tries)));
    }
  }
  setInterval(refresh, 3000);
  // während eines Kampfs gegen Freunde öfter nachfragen
  setInterval(() => { if (FAST_POLL_MODES.includes(S.mode)) refresh(); }, 700);
  setInterval(() => {
    S.tick++;
    if (S.tick % 5 === 0) stepWalk();
    tickBattle();
    render();
  }, 100);
  requestAnimationFrame(fastFrame);       // im Kampf zusätzlich flüssig zeichnen
  const me = await api("/api/me").catch(() => ({ user: null }));
  checkVersion(me.version, me.release);
  S.access = me;
  if (me.user) await showGame();
  else showAuth(me.first_user);
}

start();
