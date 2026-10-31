"use strict";
// Admin-Bereich: Übersicht, Spieler, Spielregeln, Zugang, Backups, Protokoll.

const $ = sel => document.querySelector(sel);
const A = { users: [], settings: null, lines: [], items: [] };

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const json = await res.json().catch(() => ({ error: "Server-Fehler" }));
  if (!res.ok) throw new Error(json.error || "Server-Fehler");
  return json;
}

let msgTimer;
function message(text, bad = false) {
  const el = $("#msg");
  el.textContent = text;
  el.className = "admin-msg" + (bad ? " bad" : "");
  el.hidden = false;
  clearTimeout(msgTimer);
  msgTimer = setTimeout(() => { el.hidden = true; }, 8000);
}

async function run(fn) {
  try { await fn(); } catch (e) { message(e.message, true); }
}

function ago(seconds) {
  if (!seconds) return "noch nie";
  const d = Date.now() / 1000 - seconds;
  if (d < 90) return "gerade eben";
  if (d < 3600) return `vor ${Math.round(d / 60)} Min`;
  if (d < 86400) return `vor ${Math.round(d / 3600)} Std`;
  return `vor ${Math.round(d / 86400)} Tagen`;
}

const when = sec => new Date(sec * 1000).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" });
const gameTime = min => new Date(min * 60000).toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" });

// ------------------------------------------------------------ Reiter
document.querySelectorAll("[data-tab]").forEach(btn => btn.addEventListener("click", () => showTab(btn.dataset.tab)));

function showTab(name) {
  document.querySelectorAll("[data-tab]").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".pane").forEach(p => { p.hidden = p.id !== `pane-${name}`; });
  history.replaceState(null, "", `#${name}`);
  ({ overview: loadOverview, players: loadPlayers, rules: loadSettings, prices: loadPrices, access: loadSettings,
    backups: loadBackups, log: loadLog })[name]();
}

// ------------------------------------------------------------ Übersicht
async function loadOverview() {
  await run(async () => {
    const [o, u] = await Promise.all([api("/api/admin/overview"), api("/api/admin/users")]);
    const card = (label, value, sub = "") => `<div class="stat-card"><span>${label}</span><b>${value}</b><small>${sub}</small></div>`;
    $("#stats").innerHTML = [
      card("Spieler", o.users, `${o.online} online`),
      card("Lebende Digimon", o.alive, `${o.eggs} Eier · ${o.dead} verstorben`),
      card("Kämpfe gegen Freunde", o.duels),
      card("Tausche", o.trades, `${o.jogress} Jogress`),
      card("Spielstand", `${o.db_kb} KB`, `${o.backups} Backups`),
      card("Server läuft seit", o.uptime_min < 120 ? `${o.uptime_min} Min` : `${Math.round(o.uptime_min / 60)} Std`),
      card("Digimon im Spiel", o.digimon_total, `${o.lines_total} Ei-Sorten`),
      card("Letztes Backup", o.last_backup ? ago(o.last_backup) : "–", o.last_backup ? when(o.last_backup) : "noch keins"),
    ].join("");
    A.users = u.users;
    const online = u.users.filter(x => x.online);
    $("#online-list").innerHTML = online.length
      ? online.map(x => `<li><span class="dot on"></span><b>${esc(x.name)}</b> ${x.partner ? `– ${esc(x.partner.name)} (${esc(x.partner.stage_de)})` : ""}</li>`).join("")
      : "<li class='hint'>Gerade niemand.</li>";
  });
}

// ------------------------------------------------------------ Spieler
async function loadPlayers() {
  await run(async () => {
    const [u, s] = await Promise.all([api("/api/admin/users"), A.lines.length ? null : api("/api/admin/settings")]);
    if (s) Object.assign(A, { settings: s.settings, lines: s.lines, items: s.items });
    A.users = u.users;
    renderPlayers();
  });
}

function status(p) {
  if (!p) return "kein Digimon";
  if (!p.alive) return `verstorben (${p.death_cause || "?"})`;
  const bits = [];
  if (p.sick) bits.push("krank/verletzt");
  if (p.frozen) bits.push("Kühlschrank");
  if (p.away) bits.push("unterwegs");
  bits.push(`Hunger ${p.hunger}/4 · Kraft ${p.strength}/4`);
  return bits.join(" · ");
}

function renderPlayers() {
  const q = $("#player-filter").value.trim().toLowerCase();
  const me = $("#admin-user").dataset.name;
  const list = A.users.filter(u => !q || u.name.toLowerCase().includes(q));
  const items = A.items.map(i => `<option value="${i.key}">${esc(i.name)}</option>`).join("");
  const lines = A.lines.map(l => `<option value="${l.key}">${esc(l.name.replace(/^Digi-Ei /, ""))}</option>`).join("");
  $("#players").innerHTML = list.map(u => {
    const p = u.partner;
    const self = u.name === me;
    return `<article class="player" data-name="${esc(u.name)}">
      <header>
        <span class="dot ${u.online ? "on" : ""}"></span>
        <b>${esc(u.name)}</b>
        ${u.admin ? '<span class="tag">Admin</span>' : ""}
        ${u.banned ? '<span class="tag bad">gesperrt</span>' : ""}
        ${u.cheated ? '<span class="tag dim">gecheatet</span>' : ""}
        ${self ? '<span class="tag dim">du</span>' : ""}
      </header>
      <p class="player-info">
        ${p ? `<b>${esc(p.name)}</b> (${esc(p.stage_de)}) – ${esc(status(p))}` : "kein Digimon"}<br>
        Sammlung: ${u.box} · Siege: ${u.wins}/${u.battles} · zuletzt aktiv: ${u.online ? "jetzt" : ago(u.last_seen)}
        · dabei seit ${u.created ? when(u.created).split(",")[0] : "?"}
      </p>
      <div class="actions">
        <button class="small" data-act="feed" ${p && p.alive ? "" : "disabled"}>Füttern</button>
        <button class="small" data-act="heal" ${p && p.alive && p.sick ? "" : "disabled"}>Heilen</button>
        <button class="small" data-act="revive" ${p && !p.alive ? "" : "disabled"}>Wiederbeleben</button>
        ${self ? "" : `<button class="small" data-act="reset_pw" data-confirm="Wirklich neues Passwort?">Passwort zurücksetzen</button>`}
        ${self ? "" : `<button class="small" data-act="kick">Abmelden</button>`}
        ${self ? "" : u.admin ? `<button class="small" data-act="remove_admin" data-confirm="Wirklich entziehen?">Admin entziehen</button>`
                             : `<button class="small" data-act="make_admin" data-confirm="Wirklich alle Rechte geben?">Zum Admin machen</button>`}
        ${self ? "" : u.banned ? `<button class="small" data-act="unban">Entsperren</button>`
                              : `<button class="small danger" data-act="ban" data-confirm="Wirklich sperren?">Sperren</button>`}
        ${self ? "" : `<button class="small danger" data-act="delete" data-confirm="Wirklich ${esc(u.name)} löschen?">Konto löschen</button>`}
      </div>
      <div class="actions gift">
        <select class="admin-input" data-item>${items}</select>
        <input class="admin-input num" data-count type="number" min="1" max="20" value="1">
        <button class="small" data-act="gift_item">Item schenken</button>
        <select class="admin-input" data-line>${lines}</select>
        <button class="small" data-act="gift_egg">Ei schenken</button>
      </div>
      <p class="hint result"></p>
    </article>`;
  }).join("") || "<p class='hint'>Keine Spieler gefunden.</p>";
}

$("#player-filter").addEventListener("input", renderPlayers);

// Zweimal klicken zum Bestätigen – nach ein paar Sekunden ist der Knopf wieder "entschärft"
function confirmed(btn, question) {
  if (btn.dataset.sure) return true;
  const label = btn.textContent;
  btn.dataset.sure = "1";
  btn.textContent = question;
  setTimeout(() => {
    if (!btn.isConnected) return;
    delete btn.dataset.sure;
    btn.textContent = label;
  }, 4000);
  return false;
}

// Neues Passwort bleibt stehen, bis man es wegklickt (nicht nur kurz als Meldung)
function showPassword(name, password) {
  let box = $("#pw-note");
  if (!box) {
    box = document.createElement("div");
    box.id = "pw-note";
    box.className = "pw-note";
    $("#players").before(box);
    box.addEventListener("click", e => { if (e.target.closest("[data-close]")) box.remove(); });
  }
  box.innerHTML = `Neues Passwort für <b>${esc(name)}</b>: <code class="code">${esc(password)}</code>
    – gib es weiter, es wird nicht noch einmal angezeigt.
    <button class="small" data-close>Notiert</button>`;
}

$("#players").addEventListener("click", e => {
  const btn = e.target.closest("[data-act]");
  if (!btn) return;
  const card = btn.closest(".player");
  const name = card.dataset.name;
  const action = btn.dataset.act;
  if (btn.dataset.confirm && !confirmed(btn, btn.dataset.confirm)) return;
  const body = { name, action };
  if (action === "gift_item") Object.assign(body, { item: card.querySelector("[data-item]").value,
    count: Number(card.querySelector("[data-count]").value) });
  if (action === "gift_egg") body.line = card.querySelector("[data-line]").value;
  run(async () => {
    const res = await api("/api/admin/user", body);
    A.users = res.users;
    renderPlayers();
    message(res.message);
    if (res.password) showPassword(name, res.password);
  });
});

// ------------------------------------------------------------ Spielregeln & Zugang
async function loadSettings() {
  await run(async () => {
    const s = await api("/api/admin/settings");
    Object.assign(A, { settings: s.settings, lines: s.lines, items: s.items });
    const r = $("#rules-form").elements;
    const opts = (sel, values, fmt) => { sel.innerHTML = values.map(v => `<option value="${v}">${fmt(v)}</option>`).join(""); };
    opts(r.need_speed, s.allowed.need_speed, v => `${v}×` + (v < 1 ? " (entspannter)" : v > 1 ? " (stressiger)" : " (normal)"));
    opts(r.explore_luck, s.allowed.explore_luck, v => `${v}×`);
    r.death.checked = s.settings.death;
    r.need_speed.value = s.settings.need_speed;
    r.explore_luck.value = s.settings.explore_luck;
    r.battle_egg_chance.value = s.settings.battle_egg_chance;
    r.free_egg.checked = s.settings.free_egg;
    $("#egg-chance-out").textContent = Math.round(s.settings.battle_egg_chance * 100) + " %";
    const a = $("#access-form").elements;
    a.registration.value = s.settings.registration;
    a.maintenance.checked = s.settings.maintenance;
    a.announcement.value = s.settings.announcement;
    $("#invite").textContent = s.invite;
  });
}

$("#rules-form").battle_egg_chance.addEventListener("input", e => {
  $("#egg-chance-out").textContent = Math.round(e.target.value * 100) + " %";
});

async function saveSettings(changes) {
  await run(async () => {
    const res = await api("/api/admin/settings", { changes });
    A.settings = res.settings;
    message("Gespeichert – gilt sofort für alle Spieler.");
  });
}

$("#rules-form").addEventListener("submit", e => {
  e.preventDefault();
  const f = e.target.elements;
  saveSettings({ death: f.death.checked, need_speed: Number(f.need_speed.value),
    explore_luck: Number(f.explore_luck.value), battle_egg_chance: Number(f.battle_egg_chance.value),
    free_egg: f.free_egg.checked });
});

$("#access-form").addEventListener("submit", e => {
  e.preventDefault();
  const f = e.target.elements;
  saveSettings({ registration: f.registration.value, maintenance: f.maintenance.checked,
    announcement: f.announcement.value });
});

$("#invite-new").addEventListener("click", e => confirmed(e.currentTarget, "Alter Code wird ungültig – sicher?") && run(async () => {
  $("#invite").textContent = (await api("/api/admin/invite/new", {})).code;
  message("Neuer Einladungscode – der alte gilt nicht mehr.");
}));
$("#invite-copy").addEventListener("click", () => run(async () => {
  await navigator.clipboard.writeText($("#invite").textContent);
  message("Einladungscode kopiert.");
}));

// ------------------------------------------------------------ Shop & Preise (Daily Steal)
function renderPrices(p) {
  const d = p.daily;
  $("#steal-discount").textContent = p.discount;
  $("#steal-today").innerHTML = `Heute: <b>${esc(d.today_name)}</b> für <b>${d.price} Bits</b>
    statt <s>${d.regular}</s> (−${p.discount} %)${d.pin === "auto" ? " · wechselt um Mitternacht" : " · festgelegt"}`;
  $("#daily-select").innerHTML = `<option value="auto">Automatisch (jeden Tag ein anderes)</option>`
    + p.daily_items.map(i => `<option value="${i.key}">${esc(i.name)}</option>`).join("");
  $("#daily-select").value = d.pin;
  // in Gruppen: Items, Designs, Deko (Designs/Deko kosten Bits oder Event-Items)
  const groups = [["items", "Items"], ["themes", "V-Pet-Designs"], ["decor", "Deko"]];
  $("#price-table").innerHTML = groups.map(([g, title]) => `<h3 class="price-group">${title}</h3>`
    + p.prices.filter(r => r.group === g).map(r => `
    <div class="price-row ${r.price !== r.default ? "changed" : ""}" data-key="${esc(r.key)}">
      <span><b>${esc(r.name)}</b>${r.event ? ` <span class="tag dim" title="nur während ${esc(r.event)}">Event</span>` : ""}
        <small>Standard: ${r.default} ${esc(r.unit)}</small></span>
      <input class="admin-input num" type="number" min="1" max="100000" step="1" value="${r.price}" data-default="${r.default}"
        aria-label="Preis für ${esc(r.name)}">
      <span class="price-unit">${esc(r.unit)}</span>
      <button class="small" type="button" data-reset>Standard</button>
    </div>`).join("")).join("");
}

async function loadPrices() {
  await run(async () => renderPrices(await api("/api/admin/prices")));
}

$("#price-table").addEventListener("click", e => {
  const btn = e.target.closest("[data-reset]");
  if (!btn) return;
  const input = btn.parentElement.querySelector("input");
  input.value = input.dataset.default;
  btn.parentElement.classList.remove("changed");
});
$("#price-table").addEventListener("input", e => {
  const row = e.target.closest(".price-row");
  if (row) row.classList.toggle("changed", e.target.value !== e.target.dataset.default);
});

$("#prices-form").addEventListener("submit", e => {
  e.preventDefault();
  const prices = {};
  for (const row of document.querySelectorAll(".price-row")) {
    const value = Number(row.querySelector("input").value);
    if (!Number.isInteger(value) || value < 1) return message(`Ungültiger Preis bei ${row.querySelector("b").textContent}.`, true);
    prices[row.dataset.key] = value;
  }
  run(async () => {
    const res = await api("/api/admin/prices", { prices, daily: $("#daily-select").value });
    renderPrices(res);
    message(res.message);
  });
});

// ------------------------------------------------------------ Backups
function renderBackups(list) {
  $("#backups").innerHTML = list.map(b => `
    <li>
      <span><b>${esc(b.name.replace(/^[a-z-]+?-(?=\d)/, "").replace(/\.db$/, ""))}</b>
        <small>${when(b.time)} · ${b.size_kb} KB</small></span>
      <span class="actions">
        <a class="small" href="/api/admin/backup/download?name=${encodeURIComponent(b.name)}">Herunterladen</a>
        <button class="small" data-restore="${esc(b.name)}">Einspielen</button>
        <button class="small danger" data-delete="${esc(b.name)}">Löschen</button>
      </span>
    </li>`).join("") || "<li class='hint'>Noch keine Backups.</li>";
}

async function loadBackups() {
  await run(async () => renderBackups((await api("/api/admin/backups")).backups));
}

$("#backup-now").addEventListener("click", () => run(async () => {
  const res = await api("/api/backup", {});
  renderBackups(res.backups);
  message(res.message);
}));

$("#backups").addEventListener("click", e => {
  const btn = e.target.closest("[data-restore], [data-delete]");
  if (!btn) return;
  if (!confirmed(btn, btn.dataset.restore ? "Wirklich einspielen? (alle Spieler!)" : "Wirklich löschen?")) return;
  run(async () => {
    if (btn.dataset.restore) {
      const res = await api("/api/admin/backup/restore", { name: btn.dataset.restore });
      message(res.message + " Seite lädt neu ...");
      setTimeout(() => location.reload(), 2500);
    } else {
      const res = await api("/api/admin/backup/delete", { name: btn.dataset.delete });
      renderBackups(res.backups);
      message(res.message);
    }
  });
});

// ------------------------------------------------------------ Protokoll
async function loadLog() {
  await run(async () => {
    const res = await api("/api/admin/activity");
    $("#activity").innerHTML = res.activity.map(a =>
      `<li><time>${when(a.time)}</time><b>${esc(a.who)}</b> ${esc(a.text)}</li>`).join("") || "<li class='hint'>Noch nichts passiert.</li>";
    $("#diary").innerHTML = res.diary.map(d =>
      `<li><time>${gameTime(d.t)}</time><b>${esc(d.who)}</b>: ${esc(d.text)}</li>`).join("") || "<li class='hint'>Noch keine Einträge.</li>";
  });
}

// ------------------------------------------------------------ Start
(async () => {
  const me = await api("/api/me").catch(() => ({}));
  if (!me.user || !me.user.admin) {
    document.querySelector(".admin").innerHTML =
      `<p class="admin-msg bad">Nur für Admins. <a href="/">Zurück zum Spiel</a></p>`;
    return;
  }
  $("#admin-user").textContent = `Angemeldet als ${me.user.name}`;
  $("#admin-user").dataset.name = me.user.name;
  const tab = location.hash.slice(1);
  showTab(["overview", "players", "rules", "prices", "access", "backups", "log"].includes(tab) ? tab : "overview");
})();
