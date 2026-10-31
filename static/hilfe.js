"use strict";
// Hilfe-Seite: Anleitung, Digimon-Finder (mit Merkliste) und Digidex.
// Die Regel-Logik (Bedingungen erklären, Wege finden) steckt in rules.js.
// Zweisprachig: Texte über tr() (static/i18n.js, englisch in static/i18n/en-help.js);
// die englische Anleitung steht als <template id="anleitung-en"> in hilfe.html.

const { STAGES, STAGE_DE, STAGE_TIME, ATTR_DE, esc, when, ruleParts, ruleText, needsFusion, needsItem, itemName,
  blocked, routes, optionsOf, recipe, exampleText, styleHint } = Rules;

const $ = sel => document.querySelector(sel);
let D;                        // digimon.json
let wish = null;              // gemerkte Digimon (null = nicht angemeldet)
let owned = null;             // gesammelte Digimon (Set; null = nicht angemeldet)
let mine = [];                // eigene geschlüpfte Digimon {dex, line, name, active} – aktives zuerst
// Namen der Events, zu denen es besondere Eier gibt (game/events.py)
const EVENT_NAMES = { halloween: tr("Halloween") };

// ------------------------------------------------------------ V-Pet-Design
// Das Spiel merkt sich das Design auf dem Gerät (localStorage "vpet.theme") – hier dieselben Farben
try {
  const t = JSON.parse(localStorage.getItem("vpet.theme"));
  if (t && t.ui) {
    const root = document.documentElement.style;
    const vars = { "--deep": t.ui.deep, "--bg": t.ui.bg, "--panel": t.ui.panel, "--panel-2": t.ui.panel2,
      "--line": t.ui.line, "--cyan": t.ui.accent, "--orange": t.ui.accent2, "--muted": t.ui.muted,
      "--lcd": t.lcd, "--lcd-pixel": t.pixel };
    Object.entries(vars).forEach(([k, v]) => v && root.setProperty(k, v));
  }
} catch { /* Standard-Design */ }

// ------------------------------------------------------------ Sprache
// Englisch: Anleitung aus dem Template einsetzen, feste Texte übersetzen
if (I18N.lang === "en") {
  $('[data-view="anleitung"]').innerHTML = $("#anleitung-en").innerHTML;
  I18N.translatePage();
}
document.querySelectorAll("[data-lang]").forEach(b => {
  b.classList.toggle("primary", b.dataset.lang === I18N.lang);
  b.addEventListener("click", async () => {
    if (b.dataset.lang === I18N.lang) return;
    I18N.set(b.dataset.lang);
    if (wish) {               // angemeldet: auch fürs Konto merken
      await fetch("/api/lang", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lang: b.dataset.lang }) }).catch(() => {});
    }
    location.reload();
  });
});

// ------------------------------------------------------------ Hilfsfunktionen
function lineName(line) {
  return D.lines[line].name.replace(/^Digi-Ei /, "");
}

const eggName = line => tr("Digi-Ei {name}", { name: lineName(line) });

function spriteCanvas(dex, scale = 3) {
  const c = document.createElement("canvas");
  const rows = D.digimon[dex].frames[0];
  c.width = rows[0].length * scale;
  c.height = rows.length * scale;
  const g = c.getContext("2d");
  const css = getComputedStyle(document.documentElement);
  g.fillStyle = css.getPropertyValue("--lcd").trim();
  g.fillRect(0, 0, c.width, c.height);
  g.fillStyle = css.getPropertyValue("--lcd-pixel").trim();
  rows.forEach((row, y) => {
    for (let x = 0; x < row.length; x++) if (row[x] === "1") g.fillRect(x * scale, y * scale, scale, scale);
  });
  return c;
}

function stageOf(dex) {
  return dex === null ? "Egg" : D.digimon[dex].stage;
}

// alle Digimon, die es im Spiel gibt
const allDigimon = () => [...new Set(D.evolutions.map(e => e.to))];

const wishLabel = on => (on ? tr("★ Gemerkt") : tr("☆ Merken"));
const wishTitle = () => (wish ? tr("Auf die Merkliste im Spiel") : tr("Zum Merken erst im Spiel anmelden"));

// ------------------------------------------------------------ Bereiche (Tabs)
// #anleitung, #finder, #digidex, #digimon/93 (ein Digidex-Eintrag) – Anker in der
// Anleitung (#training ...) öffnen die Anleitung
const VIEWS = ["anleitung", "finder", "digidex"];
const OLD_ANCHORS = { linien: "digidex", eier: "digidex" };       // alte Links
// alte Kapitel-Anker aus der früheren Anleitung
const OLD_CHAPTERS = { ziel: "schnellstart", start: "schnellstart", tasten: "pflege" };

function showView() {
  const hash = location.hash.slice(1);
  const entry = /^digimon\/(\d+)$/.exec(hash);
  const view = entry ? "digimon" : VIEWS.includes(hash) ? hash : OLD_ANCHORS[hash] || "anleitung";
  document.querySelectorAll(".view").forEach(v => { v.hidden = v.dataset.view !== view; });
  const tab = view === "digimon" ? "digidex" : view;
  document.querySelectorAll(".help-tabs a").forEach(a => a.classList.toggle("on", a.dataset.tab === tab));
  if (view === "anleitung") showChapter(OLD_CHAPTERS[hash] || hash);
  window.scrollTo(0, 0);
  if (view === "digidex") renderDex();
  if (view === "digimon") renderEntry(Number(entry[1]));
}

// ------------------------------------------------------------ Anleitung in Kapiteln
// Statt einer langen Seite immer nur ein Abschnitt; Inhaltsverzeichnis + Blättern.
function showChapter(id) {
  const chapters = [...document.querySelectorAll(".help-body > section")];
  const current = chapters.find(s => s.id === id) || chapters[0];
  chapters.forEach(s => { s.hidden = s !== current; });
  document.querySelectorAll(".toc a").forEach(a => a.classList.toggle("on", a.getAttribute("href") === `#${current.id}`));
  const i = chapters.indexOf(current);
  const link = (s, label) => s ? `<a class="small" href="#${s.id}">${label}</a>` : "<span></span>";
  const title = s => s.querySelector("h2").textContent;
  $("#chapter-nav").innerHTML = link(chapters[i - 1], chapters[i - 1] ? `← ${esc(title(chapters[i - 1]))}` : "")
    + `<span class="hint">${tr("Kapitel {n} von {total}", { n: i + 1, total: chapters.length })}</span>`
    + link(chapters[i + 1], chapters[i + 1] ? `${esc(title(chapters[i + 1]))} →` : "");
  const active = document.querySelector(".toc a.on");
  if (active) active.scrollIntoView({ block: "nearest", inline: "center" });   // Handy: Leiste mitscrollen
}

// ------------------------------------------------------------ Merkliste
async function loadWishlist() {
  try {
    const me = await (await fetch("/api/me")).json();
    if (!me.user) return;
    wish = (await (await fetch("/api/wishlist")).json()).wishlist || [];
    owned = new Set((await (await fetch("/api/progress")).json()).owned || []);
    // eigene Digimon (aktiv + Sammlung): der Finder zeigt den Weg von ihnen aus
    const [state, box] = await Promise.all([fetch("/api/state").then(r => r.json()), fetch("/api/box").then(r => r.json())]);
    const label = p => p.nickname ? `${p.nickname} (${p.name})` : p.name;
    const hatched = p => p && p.alive && p.dex && D.digimon[p.dex];
    mine = [
      ...(hatched(state.pet) ? [{ dex: state.pet.dex, line: state.pet.line, name: label(state.pet), active: true }] : []),
      ...(box.box || []).filter(hatched).map(p => ({ dex: p.dex, line: p.line, name: label(p), active: false })),
    ];
  } catch { /* ohne Anmeldung kein Merken */ }
}

async function toggleWish(dex) {
  const on = !wish.includes(dex);
  const res = await fetch("/api/wishlist", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ dex, on }),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) { alert(json.error || tr("Das hat nicht geklappt.")); return; }
  wish = json.wishlist;
  renderFinderHead();
  if (!$('[data-view="digimon"]').hidden) renderEntry(dex);
}

// ------------------------------------------------------------ Finder
function selected() {
  return Number($("#target").value);
}

// Kopf: großes Bild, Name, Stufe, Attribut, ☆ Merken
function renderFinderHead() {
  const dex = selected();
  const d = D.digimon[dex];
  const box = $("#finder-head");
  box.innerHTML = "";
  box.append(spriteCanvas(dex, 5));
  const on = wish && wish.includes(dex);
  box.insertAdjacentHTML("beforeend", `<div>
      <h2>${esc(d.name)}</h2>
      <p class="hint">${STAGE_DE[d.stage]}${ATTR_DE[d.attribute] ? " · " + ATTR_DE[d.attribute] : ""}</p>
    </div>
    <a class="small" href="#digimon/${dex}">${tr("Digidex-Eintrag")}</a>
    <button class="small ${on ? "primary" : ""}" id="wish-toggle" ${wish ? "" : "disabled"}
      title="${wishTitle()}">${wishLabel(on)}</button>`);
  if (!wish) box.insertAdjacentHTML("beforeend", `<p class="hint wish-login">${tr("Zum Merken erst im Spiel anmelden.")}</p>`);
  $("#wish-toggle").addEventListener("click", () => toggleWish(dex));
}

// Der Finder zeigt für ein Digimon: zuerst den Weg von deinen eigenen Digimon aus (angemeldet),
// dann für JEDES Ei den einfachsten Weg (aufklappbar) und zuletzt, was daraus werden kann.
// (Früher nur die 6 einfachsten Wege insgesamt – dann fehlten bei vielen Digimon ganze Eier.)
const effort = route => route.reduce((n, s) => n + (blocked(s.rule) ? 10 : 0) + ruleParts(s.rule).length, 0);

function routeList(route) {
  const ol = document.createElement("ol");
  route.forEach(step => ol.append(stepItem(step)));
  return ol;
}

// Wege von deinen Digimon (aktiv + Sammlung) zum Ziel – kürzester Weg in ihrer Ei-Linie
function renderMine(dex, box) {
  if (!mine.length) return;
  const name = D.digimon[dex].name;
  const have = mine.filter(m => m.dex === dex);
  const reach = mine.filter(m => m.dex !== dex).map(m => ({ ...m, path: Rules.pathTo(m.dex, dex, m.line) }))
    .filter(m => m.path && m.path.length);
  if (!have.length && !reach.length) return;
  const card = document.createElement("div");
  card.className = "route mine";
  card.insertAdjacentHTML("beforeend", `<h3>${tr("Von deinen Digimon aus")}</h3>`);
  if (have.length) {
    card.insertAdjacentHTML("beforeend", `<p class="ok">${tr("Du hast {name} schon: {who}.", {
      name: esc(name), who: have.map(m => esc(m.name)).join(", ") })}</p>`);
  }
  reach.slice(0, 3).forEach((m, i) => {
    const d = document.createElement("details");
    d.open = i === 0;
    d.insertAdjacentHTML("beforeend", `<summary>${tr("Von {who}{where}", { who: `<b>${esc(m.name)}</b>`,
      where: m.active ? "" : " " + tr("(Sammlung)") })} – ${tr("{n} Schritte", { n: m.path.length })}</summary>`);
    d.append(routeList(m.path));
    card.append(d);
  });
  if (reach.length > 3) {
    card.insertAdjacentHTML("beforeend", `<p class="hint">${tr("Auch erreichbar von: {who}.", {
      who: reach.slice(3).map(m => esc(m.name)).join(", ") })}</p>`);
  }
  box.append(card);
}

function renderRoutes() {
  const dex = selected();
  renderFinderHead();
  const all = Object.keys(D.lines).flatMap(line => routes(line, dex).map(route => ({ line, route })));
  const box = $("#routes");
  box.innerHTML = "";
  renderMine(dex, box);
  if (!all.length) { box.append(tr("Dafür ist kein Weg bekannt.")); renderNext(dex, box); return; }

  // pro Ei der einfachste Weg (wenige Kampf-/Fusionsstufen, dann wenige Bedingungen)
  const perEgg = new Map();
  for (const r of all) {
    const best = perEgg.get(r.line);
    if (!best) perEgg.set(r.line, { ...r, count: 1 });
    else {
      best.count++;
      if (effort(r.route) < effort(best.route)) best.route = r.route;
    }
  }
  const eggs = [...perEgg.values()].sort((a, b) => effort(a.route) - effort(b.route));
  const name = D.digimon[dex].name;
  const head = document.createElement("p");
  head.className = "hint";
  head.textContent = eggs.length === 1
    ? tr("{name} kommt aus dem {egg}.", { name, egg: eggName(eggs[0].line) })
    : tr("{name} kann aus {n} Eiern kommen. Hier steht für jedes Ei der einfachste Weg – antippen zum Aufklappen.",
      { name, n: eggs.length });
  box.append(head);

  eggs.forEach(({ line, route, count }, i) => {
    const card = document.createElement("details");
    card.className = "route egg-route";
    card.open = i === 0;
    const event = D.lines[line].event;
    // Event-Ei: gibt es nur während des Events – und die Reihe ist fest
    const tag = event ? ` <span class="tag">${tr("nur während {event}", { event: EVENT_NAMES[event] || event })}</span>` : "";
    card.insertAdjacentHTML("beforeend", `<summary><b>${tr("Aus dem {egg}", { egg: esc(eggName(line)) })}</b>${tag}
      <small>${route.map(s => esc(D.digimon[s.to].name)).join(" → ")}</small></summary>`);
    card.append(routeList(route));
    if (count > 1) {
      card.insertAdjacentHTML("beforeend", `<p class="hint">${tr("In diesem Ei gibt es noch {n} andere Wege dorthin.", { n: count - 1 })}</p>`);
    }
    box.append(card);
  });
  renderNext(dex, box);
}

// Ein Entwicklungsschritt: Bild, Name, Zeit, Bedingung, sicheres Beispiel, Warnungen
function stepItem(step) {
  const li = document.createElement("li");
  const fromStage = stageOf(step.from);
  const fromName = step.from === null ? tr("dem Ei") : D.digimon[step.from].name;
  const r = recipe(step);
  const stop = blocked(step.rule);
  li.append(spriteCanvas(step.to));
  const text = document.createElement("div");
  const how = step.from === null
    ? tr("Schlüpft nach <b>{time}</b> aus dem Ei.", { time: when(STAGE_TIME.Egg) })
    : needsItem(step.rule)
      ? tr("Armor-Digitation: <b>sofort</b>, wenn du {from} „{item}“ gibst (Rucksack) – jederzeit, solange es {from} ist.",
        { from: esc(fromName), item: esc(itemName(step.rule.item)) })
    : needsFusion(step.rule) || !STAGE_TIME[fromStage]
      ? tr("Entsteht per Fusion aus {from} – sobald ein passender Partner da ist.", { from: esc(fromName) })
      : tr("Digitiert nach <b>{time}</b> als {from}.", { time: when(STAGE_TIME[fromStage]), from: esc(fromName) });
  const sure = r.example && step.from !== null && !stop && (ruleParts(step.rule).length || r.choices > 1)
    ? `<p class="ok">${tr("So klappt's sicher: {example}", { example: esc(exampleText(r.example)) })}${
      r.battleRivals ? tr(", keine Kämpfe in dieser Stufe") : ""}${r.mixed
      ? tr(" – und dabei gemischt trainieren (keine Trainingsart mit 60 % oder mehr)") : ""}.</p>` : "";
  text.innerHTML = `
    <b>${esc(D.digimon[step.to].name)}</b> <span class="stage">${STAGE_DE[step.stage]}</span>
    ${stop ? `<span class="tag">${stop}</span>` : ""}
    <p>${how}</p>
    <p>${tr("Bedingung: {rule}.", { rule: esc(ruleText(step.rule)) })}</p>
    ${sure}
    ${!r.example && step.from !== null && !stop
      ? `<p class="warn">${tr("Mit diesen Regeln kommt hier immer eine andere Form zuerst dran.")}</p>` : ""}
    ${styleHint(step)}
    ${r.rivals.length ? `<p class="warn">${tr("Vorsicht: {list}.", { list: r.rivals.map(e =>
      tr("{name} hat Vorrang, wenn {rule} passt", { name: esc(D.digimon[e.to].name), rule: esc(ruleText(e.rule)) }))
      .join("; ") })}</p>` : ""}`;
  li.append(text);
  return li;
}

// Was kann aus dem gewählten Digimon werden? (in jedem Ei dasselbe – anklickbar)
function renderNext(dex, box) {
  const next = optionsOf(dex);
  const card = document.createElement("div");
  card.className = "route next";
  const h = document.createElement("h3");
  h.textContent = tr("Daraus kann werden");
  card.append(h);
  const hint = document.createElement("p");
  hint.className = "hint";
  hint.textContent = !next.length
    ? tr("{name} ist eine Endstufe – weiter geht es hier nicht.", { name: D.digimon[dex].name })
    : next.length === 1 ? tr("Tipp die Form an, um zu sehen, wie es danach weitergeht.")
      : tr("{n} Möglichkeiten. Passen mehrere, gewinnt die obere – außer dein Trainingsstil ★ bevorzugt eine andere. "
        + "Tipp eine Form an, um weiterzuschauen.", { n: next.length });
  card.append(hint);
  if (next.length) {
    const ol = document.createElement("ol");
    next.forEach(step => {
      const li = stepItem(step);
      li.classList.add("pickable");
      li.title = tr("{name} auswählen", { name: D.digimon[step.to].name });
      li.addEventListener("click", () => pick(step.to));
      ol.append(li);
    });
    card.append(ol);
  }
  box.append(card);
}

function fillTargets() {
  const sel = $("#target");
  // jedes Digimon genau einmal, nach Stufe gruppiert und alphabetisch
  const all = allDigimon();
  for (const stage of STAGES) {
    const group = document.createElement("optgroup");
    group.label = STAGE_DE[stage];
    all.filter(dex => D.digimon[dex].stage === stage)
      .sort((a, b) => D.digimon[a].name.localeCompare(D.digimon[b].name))
      .forEach(dex => {
        const o = document.createElement("option");
        o.value = String(dex);
        o.textContent = `${D.digimon[dex].name} (${STAGE_DE[stage]})`;
        group.append(o);
      });
    sel.append(group);
  }
  sel.addEventListener("change", () => {
    renderRoutes();
    history.replaceState(null, "", `?ziel=${sel.value}#finder`);
  });
  // Suche: erstes Digimon, dessen Name passt (Anfang vor Mitte)
  $("#search").addEventListener("input", e => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) return;
    const opts = [...sel.options];
    const name = o => o.textContent.toLowerCase();
    const hit = opts.find(o => name(o).startsWith(q)) || opts.find(o => name(o).includes(q));
    if (hit && hit.value !== sel.value) {
      sel.value = hit.value;
      sel.dispatchEvent(new Event("change"));
    }
  });
  // ?ziel=93 (alte Links: ?ziel=ver1:93)
  const wanted = (new URLSearchParams(location.search).get("ziel") || "").split(":").pop();
  const greymon = [...sel.options].find(o => o.textContent.startsWith("Greymon ("));
  sel.value = [...sel.options].some(o => o.value === wanted) ? wanted : greymon ? greymon.value : sel.options[0].value;
  renderRoutes();
}

// ein Digimon im Finder öffnen (aus dem Digidex oder "Daraus kann werden")
function pick(dex) {
  $("#target").value = String(dex);
  renderRoutes();
  history.pushState(null, "", `?ziel=${dex}#finder`);
  showView();
}

// ------------------------------------------------------------ Digidex
// alle Digimon als Raster – mit Suche und Filtern statt endlos langer Seite
const DEX_PAGE = 96;
const dexFilter = { stage: "", attr: "", own: "", shown: DEX_PAGE };

function chips(box, options, key) {
  box.innerHTML = options.map(([value, label]) =>
    `<button class="chip ${dexFilter[key] === value ? "on" : ""}" data-value="${value}">${label}</button>`).join("");
  box.onclick = e => {
    const b = e.target.closest(".chip");
    if (!b) return;
    dexFilter[key] = b.dataset.value;
    dexFilter.shown = DEX_PAGE;
    renderDex();
  };
}

function renderDex() {
  chips($("#dex-stage"), [["", tr("Alle Stufen")], ...STAGES.map(s => [s, STAGE_DE[s]])], "stage");
  chips($("#dex-attr"), [["", tr("Alle Attribute")], ...["Vaccine", "Data", "Virus", "Free"].map(a => [a, ATTR_DE[a]])],
    "attr");
  // Sammel-Fortschritt (angemeldet): Filter "gesammelt / fehlt noch"
  $("#dex-own").hidden = !owned;
  if (owned) chips($("#dex-own"), [["", tr("Alle")], ["have", tr("Gesammelt")], ["miss", tr("Fehlt noch")]], "own");
  $("#dex-wish").disabled = !wish;
  const q = $("#dex-search").value.trim().toLowerCase();
  const onlyWish = $("#dex-wish").checked && wish;
  const all = allDigimon();
  const list = all
    .filter(n => {
      const d = D.digimon[n];
      return (!dexFilter.stage || d.stage === dexFilter.stage) && (!dexFilter.attr || d.attribute === dexFilter.attr)
        && (!q || d.name.toLowerCase().includes(q)) && (!onlyWish || wish.includes(n))
        && (!owned || !dexFilter.own || (dexFilter.own === "have") === owned.has(n));
    })
    .sort((a, b) => STAGES.indexOf(D.digimon[a].stage) - STAGES.indexOf(D.digimon[b].stage)
      || D.digimon[a].name.localeCompare(D.digimon[b].name));
  $("#dex-count").textContent = `${list.length} Digimon` + (owned
    ? " · " + tr("Gesammelt: {n} / {total}", { n: all.filter(n => owned.has(n)).length, total: all.length }) : "");
  const grid = $("#dex-grid");
  grid.innerHTML = "";
  for (const n of list.slice(0, dexFilter.shown)) {
    const d = D.digimon[n];
    const b = document.createElement("button");
    b.className = "mon dex-card" + (owned && !owned.has(n) ? " missing" : "");
    b.title = tr("{name}: Digidex-Eintrag", { name: d.name });
    b.append(spriteCanvas(n, 2));
    b.insertAdjacentHTML("beforeend", `<span>${esc(d.name)}${wish && wish.includes(n) ? " ★" : ""}
      <small>${STAGE_DE[d.stage]}${ATTR_DE[d.attribute] ? " · " + ATTR_DE[d.attribute] : ""}</small></span>`);
    b.addEventListener("click", () => { location.hash = `#digimon/${n}`; });
    grid.append(b);
  }
  const more = list.length - dexFilter.shown;
  $("#dex-more").hidden = more <= 0;
  $("#dex-more").textContent = tr("{n} weitere anzeigen (noch {left})", { n: Math.min(more, DEX_PAGE), left: more });
}

$("#dex-search").addEventListener("input", () => { dexFilter.shown = DEX_PAGE; renderDex(); });
$("#dex-wish").addEventListener("change", () => { dexFilter.shown = DEX_PAGE; renderDex(); });
$("#dex-more").addEventListener("click", () => { dexFilter.shown += DEX_PAGE; renderDex(); });

// ------------------------------------------------------------ Digidex-Eintrag
// Wie ein Digidex: Artwork + Pixel-Sprite, Stufe/Attribut/Typ, Datenlog (Beschreibung),
// Attacken, Felder, vorherige und nächste Formen. Texte: static/digidex.json
// (Daten von der Digi-API, Beschreibungen ins Deutsche übersetzt) bzw. auf Englisch
// static/digidex_en.json (Original-Beschreibungen der Digi-API).
let DEX = null;

async function loadDigidex() {
  if (!DEX) {
    const file = I18N.lang === "en" ? "/digidex_en.json" : "/digidex.json";
    try { DEX = await (await fetch(file)).json(); } catch { DEX = {}; }
  }
  return DEX;
}

const MAX_SKILLS = 10;

function miniCard(n, note = "") {
  const d = D.digimon[n];
  return `<a class="mon" href="#digimon/${n}" data-sprite="${n}">
    <span>${esc(d.name)}<small>${STAGE_DE[d.stage]}${note ? " · " + esc(note) : ""}</small></span></a>`;
}

async function renderEntry(n) {
  const box = $("#dex-entry");
  const d = D.digimon[n];
  if (!d) { box.innerHTML = `<p class="hint">${tr("Dieses Digimon gibt es nicht.")}</p>`; return; }
  const info = (await loadDigidex())[n] || {};
  const on = wish && wish.includes(n);
  const prior = [...new Set(D.evolutions.filter(e => e.to === n && e.from !== null).map(e => e.from))];
  const next = optionsOf(n);
  const skills = info.skills || [];
  const name = esc(d.name);
  box.innerHTML = `
    <div class="dex-hero">
      <div class="dex-art">
        ${info.image ? `<img src="${esc(info.image)}" alt="${name}" referrerpolicy="no-referrer"
          onerror="this.remove()">` : ""}
        <div class="dex-pixel" title="${tr("So sieht {name} im Spiel aus", { name })}"></div>
      </div>
      <div class="dex-info">
        <h1>${name}</h1>
        <div class="badges">
          <span>${STAGE_DE[d.stage]}</span>
          ${ATTR_DE[d.attribute] ? `<span>${ATTR_DE[d.attribute]}</span>` : ""}
          ${(info.types || []).map(t => `<span>${esc(t)}</span>`).join("")}
        </div>
        <section class="dex-log">
          <h2>${tr("Datenlog")}</h2>
          <p>${esc(info.description || tr("Zu diesem Digimon gibt es noch keinen Eintrag."))}</p>
        </section>
        <div class="dex-actions">
          <button class="small primary" id="entry-finder">${tr("Wie bekomme ich {name}?", { name })}</button>
          <button class="small ${on ? "primary" : ""}" id="entry-wish" ${wish ? "" : "disabled"}
            title="${wishTitle()}">${wishLabel(on)}</button>
        </div>
      </div>
    </div>
    ${skills.length ? `<section class="dex-block"><h2>${tr("Attacken")}</h2>
      <div class="chips">${skills.slice(0, MAX_SKILLS).map(s => `<span class="chip">${esc(s)}</span>`).join("")}
      ${skills.length > MAX_SKILLS ? `<button class="chip more" id="more-skills">${
        tr("+{n} weitere", { n: skills.length - MAX_SKILLS })}</button>` : ""}
      </div></section>` : ""}
    ${(info.fields || []).length ? `<section class="dex-block"><h2>${tr("Felder")}</h2>
      <div class="chips">${info.fields.map(f => `<span class="chip">${esc(f)}</span>`).join("")}</div></section>` : ""}
    <section class="dex-block"><h2>${tr("Vorherige Formen")}</h2>
      ${prior.length ? `<div class="dex-grid">${prior.map(p => miniCard(p)).join("")}</div>`
        : `<p class="hint">${tr("Keine – {name} schlüpft aus einem Ei.", { name })}</p>`}</section>
    <section class="dex-block"><h2>${tr("Nächste Formen")}</h2>
      ${next.length ? `<div class="dex-grid">${next.map(e => miniCard(e.to,
        e.rule.item ? tr("Armor-Digitation mit „{item}“", { item: itemName(e.rule.item) }) : ruleText(e.rule))).join("")}</div>`
        : `<p class="hint">${tr("Keine – {name} ist eine Endstufe.", { name })}</p>`}</section>
    <p class="hint dex-source">${tr("Beschreibung, Typ, Attacken und Bild:")} <a href="https://digi-api.com" target="_blank"
      rel="noopener">Digi-API</a>${tr(" (Beschreibung übersetzt).")} Digimon © Bandai / Toei Animation.</p>`;
  // Pixel-Sprites (Canvas) einsetzen
  box.querySelector(".dex-pixel").append(spriteCanvas(n, 6));
  box.querySelectorAll("[data-sprite]").forEach(a => a.prepend(spriteCanvas(Number(a.dataset.sprite), 2)));
  $("#entry-finder").addEventListener("click", () => pick(n));
  $("#entry-wish").addEventListener("click", () => toggleWish(n));
  const more = $("#more-skills");
  if (more) more.addEventListener("click", () => {
    more.insertAdjacentHTML("beforebegin", skills.slice(MAX_SKILLS).map(s => `<span class="chip">${esc(s)}</span>`).join(""));
    more.remove();
  });
}

// ------------------------------------------------------------ Start
window.addEventListener("hashchange", showView);
window.addEventListener("popstate", () => {
  const wanted = new URLSearchParams(location.search).get("ziel");
  if (wanted && $("#target").value !== wanted) { $("#target").value = wanted; renderRoutes(); }
});

(async () => {
  D = await (await fetch("/data/digimon.json")).json();
  Rules.use(D);
  await loadWishlist();
  fillTargets();
  showView();
})();
