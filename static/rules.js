"use strict";
// Entwicklungsregeln verstehen und erklären – gemeinsam für Hilfe-Seite und Spiel.
// Muss zu game/pet.py passen (next_form, _rule_ok, partner_fits, Trainingsstil).
// Benutzung:  Rules.use(digimonJson);  dann z. B. Rules.ruleText(rule)
// Texte zweisprachig über tr() (static/i18n.js, englisch in static/i18n/en-rules.js).

const Rules = (() => {
  let D = null;                // digimon.json
  let LIMITS = null;

  const STAGES = ["Fresh", "InTraining", "Rookie", "Champion", "Armor", "Ultimate", "Mega"];
  // (Name STAGE_DE von früher – enthält die Stufen in der gewählten Sprache)
  const STAGE_DE = { Egg: tr("Ei"), Fresh: "Baby I", InTraining: "Baby II", Rookie: "Rookie",
    Champion: "Champion", Armor: "Armor", Ultimate: tr("Ultra"), Mega: "Mega" };
  // muss zu STAGE_TIME in game/pet.py passen (Minuten)
  const STAGE_TIME = { Egg: 1, Fresh: 10, InTraining: 720, Rookie: 1440, Champion: 2160, Ultimate: 2880 };
  const ATTR_DE = { Vaccine: tr("Serum"), Data: tr("Daten"), Virus: "Virus", Free: tr("Frei") };
  // Trainingsstil: muss zu ELEMENT_SKILL und STYLE_MIN in game/pet.py passen
  const ELEMENT_STYLE = { Fire: "power", Thunder: "power", Metal: "power", Wind: "speed", Light: "speed",
    Dark: "speed", Earth: "defense", Ice: "defense", Wood: "defense", Water: "defense" };
  // "Kraft" ist im Deutschen auch die Kraft-Anzeige (englisch "Strength") – daher hier direkt
  const STYLE_DE = I18N.lang === "en" ? { power: "Power", speed: "Speed", defense: "Defense" }
    : { power: "Kraft", speed: "Tempo", defense: "Verteidigung" };
  const STYLE_MIN = 5;

  function use(data) { D = data; LIMITS = null; }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function when(min) {
    return min < 60 ? tr("{n} Min", { n: min }) : tr("{n} Std", { n: min / 60 });
  }

  // ---------------------------------------------------------- Regeln in Worte fassen
  function rangeText([lo, hi]) {
    if (hi === null) return lo === 0 ? tr("beliebig viele") : tr("mindestens {n}", { n: lo });
    if (lo === hi) return tr("genau {n}", { n: lo });
    if (lo === 0) return tr("höchstens {n}", { n: hi });
    return tr("{lo} bis {hi}", { lo, hi });
  }

  // muss zu partner_fits in game/pet.py passen ("None" = ohne Attribut, gleiche Stufe)
  function jogressText(j) {
    if (typeof j === "number") {
      return D.digimon[j] ? tr("Fusion (Jogress) mit {name}", { name: D.digimon[j].name })
        : tr("Fusion (Jogress) mit einem Digimon, das es im Spiel (noch) nicht gibt");
    }
    const attrs = j.split("/");
    const named = attrs.filter(a => a !== "None").map(a => ATTR_DE[a] || a);
    const kinds = [];
    if (named.length) kinds.push(tr("einem {attrs}-Digimon", { attrs: named.join(tr("- oder ")) }));
    if (attrs.includes("None")) kinds.push(tr("einem Digimon ohne Attribut"));
    return tr("Fusion (Jogress) mit {kinds} derselben Stufe", { kinds: kinds.join(tr(" oder ")) });
  }

  // Armor-Ei (Item aus dem Rucksack): Name wie "Armor-Ei des Mutes"
  function itemName(key) {
    return tr((D.items && D.items[key] && D.items[key].name) || "Armor-Ei");
  }

  function ruleParts(rule) {
    if (rule.any) return [rule.any.map(ruleText).join(tr(" ODER "))];
    if (rule.item) {
      return [tr("Armor-Digitation: „{item}“ aus dem Rucksack benutzen (findet man beim Erkunden)",
        { item: itemName(rule.item) })];
    }
    const out = [];
    if (rule.cm) out.push(tr("{n} Pflegefehler", { n: rangeText(rule.cm) }));
    if (rule.tr) out.push(tr("{n} Trainings", { n: rangeText(rule.tr) }));
    if (rule.of) out.push(tr("{n}× überfüttert", { n: rangeText(rule.of) }));
    if (rule.btl) out.push(tr("{n} Kämpfe", { n: rangeText(rule.btl) }));
    if (rule.wins) out.push(tr("{n} Siege", { n: rangeText(rule.wins) }));
    if (rule.win) out.push(tr("{battles} Kämpfe, davon mindestens {wins} Siege", rule.win));
    if (rule.jogress) out.push(jogressText(rule.jogress));
    return out;
  }

  function ruleText(rule) {
    const parts = ruleParts(rule);
    return parts.length ? parts.join(", ") : tr("keine – nur gut versorgen und warten");
  }

  const needsBattle = r => r.any ? r.any.every(needsBattle) : !!(r.win || r.btl || r.wins);
  const needsFusion = r => r.any ? r.any.every(needsFusion) : !!r.jogress;
  // wie needs_battles in game/pet.py: geht es OHNE Kampf und Fusion gar nicht?
  const needsEither = r => r.any ? r.any.every(needsEither) : needsBattle(r) || needsFusion(r);
  const needsItem = r => r.any ? r.any.every(needsItem) : !!r.item;
  const blocked = rule => needsItem(rule) ? tr("Armor-Ei nötig")
    : needsFusion(rule) ? tr("Jogress nötig")
    : needsBattle(rule) ? tr("Kämpfe nötig")
    : needsEither(rule) ? tr("Kämpfe oder Jogress nötig") : null;

  // ---------------------------------------------------------- Wege finden
  // alle Wege vom Ei einer Linie zu einem Digimon
  function routes(line, dex, seen = new Set()) {
    if (seen.has(dex)) return [];          // Sicherheitsnetz gegen Kreise
    const into = D.evolutions.filter(e => e.line === line && e.to === dex);
    const out = [];
    for (const e of into) {
      if (e.from === null) out.push([e]);
      else for (const r of routes(line, e.from, new Set([...seen, dex]))) out.push([...r, e]);
    }
    return out;
  }

  // nächste Formen eines Digimon. Fast immer in jedem Ei gleich – das Spiel rechnet aber pro
  // Ei-Linie (game/pet.py evolutions_from); mit `line` (z. B. die Linie deines Digimon) zählt
  // diese, sonst die erste Linie, in der es vorkommt
  function optionsOf(dex, line = null) {
    const has = l => D.evolutions.some(e => e.line === l && e.from === dex);
    const home = line && has(line) ? line : (D.evolutions.find(e => e.from === dex) || {}).line;
    const seen = new Set();
    return D.evolutions.filter(e => e.line === home && e.from === dex && !seen.has(e.to) && seen.add(e.to));
  }

  // kürzester Weg von einem Digimon zu einem anderen (möglichst ohne Fusion) – Liste von Schritten.
  // `line` = Ei-Linie des Digimon (es bleibt beim Digitieren in seiner Linie)
  function pathTo(from, to, line = null) {
    from = Number(from);
    to = Number(to);
    if (from === to) return [];
    for (const withFusion of [false, true]) {
      const prev = new Map([[from, null]]);
      const queue = [from];
      while (queue.length) {
        const node = queue.shift();
        for (const e of optionsOf(node, line)) {
          if (!withFusion && needsFusion(e.rule)) continue;
          if (prev.has(e.to)) continue;
          prev.set(e.to, e);
          if (e.to === to) {
            const path = [];
            for (let step = e; step; step = prev.get(step.from)) path.unshift(step);
            return path;
          }
          queue.push(e.to);
        }
      }
    }
    return null;
  }

  // ---------------------------------------------------------- Entscheidung nachspielen
  // v = {cm, tr, of, style, battles}; battles = true: Kampf-Bedingungen gelten als erfüllt
  function inRange(v, r) { return !r || (v >= r[0] && (r[1] === null || v <= r[1])); }
  function noBattlesOk(rule) {
    return inRange(0, rule.btl) && inRange(0, rule.wins) && (!rule.win || rule.win.battles <= 0);
  }
  const noBattlesOkAll = rule => rule.any ? rule.any.some(noBattlesOkAll) : noBattlesOk(rule);
  function matches(rule, v, ignoreTr = false) {
    if (rule.any) return rule.any.some(r => matches(r, v, ignoreTr));
    return inRange(v.cm, rule.cm) && (ignoreTr || inRange(v.tr, rule.tr)) && inRange(v.of, rule.of)
      && !rule.jogress && !rule.item && (v.battles || noBattlesOk(rule));
  }

  function winner(siblings, v) {
    if (v.style) {
      const fav = siblings.find(s => ELEMENT_STYLE[D.digimon[s.to].element] === v.style && matches(s.rule, v, true));
      if (fav) return fav;
    }
    return siblings.find(s => matches(s.rule, v));
  }

  const stylesAt = tr => tr < STYLE_MIN ? [null] : [null, "power", "speed", "defense"];

  // Suchbereich: größte Grenze aus den Regeln + 1
  function limits() {
    if (LIMITS) return LIMITS;
    LIMITS = { cm: 4, tr: 30, of: 6 };
    const walk = r => {
      if (r.any) return r.any.forEach(walk);
      for (const k of ["cm", "tr", "of"]) {
        if (r[k]) LIMITS[k] = Math.max(LIMITS[k], r[k][0] + 1, (r[k][1] ?? 0) + 1);
      }
    };
    D.evolutions.forEach(e => walk(e.rule));
    return LIMITS;
  }

  function* grid() {
    const L = limits();
    for (let cm = 0; cm <= L.cm; cm++)
      for (let tr = 0; tr <= L.tr; tr++)
        for (let of = 0; of <= L.of; of++) yield { cm, tr, of };
  }

  // Ein sicheres Beispiel (klappt bei jedem Trainingsstil) – sonst eins, bei dem man
  // gemischt trainieren muss. Dazu die Formen, die Vorrang haben können.
  function recipe(step) {
    const siblings = D.evolutions.filter(e => e.line === step.line && e.from === step.from);
    const earlier = siblings.slice(0, siblings.indexOf(step));
    let safe = null, mixed = null;
    const rivals = new Set();
    for (const v of grid()) {
      if (matches(step.rule, v)) {                 // Beispiel ohne Kämpfe (hat man selbst in der Hand)
        const results = stylesAt(v.tr).map(style => winner(siblings, { ...v, style }));
        if (results.every(w => w === step)) { if (!safe) safe = v; }
        else if (results[0] === step) { if (!mixed) mixed = v; }
      }
      const fought = { ...v, battles: true };      // wer kann sich davordrängeln – auch durch Kämpfe?
      if (matches(step.rule, fought)) {
        const plain = winner(siblings, fought);
        if (plain && plain !== step) rivals.add(plain);
      }
    }
    return {
      example: safe || mixed, mixed: !safe && !!mixed, choices: siblings.length,
      battleRivals: siblings.some(s => s !== step && !noBattlesOkAll(s.rule)),
      rivals: earlier.filter(e => rivals.has(e)),
    };
  }

  function exampleText(v) {
    return tr("{cm} Pflegefehler, {tr} Trainings, {of}× überfüttert", v);
  }

  // Mit dem passenden Trainingsstil zu dieser Form? (nur wenn es wirklich klappt) – HTML
  function styleHint(step) {
    const style = ELEMENT_STYLE[D.digimon[step.to].element];
    if (!style || step.from === null || blocked(step.rule)) return "";
    const siblings = D.evolutions.filter(e => e.line === step.line && e.from === step.from);
    if (new Set(siblings.map(e => e.to)).size < 2) return "";       // keine Auswahl -> Stil egal
    let any = null, trFree = null;
    const L = limits();
    for (let cm = 0; cm <= L.cm && !trFree; cm++) {
      for (let of = 0; of <= L.of && !trFree; of++) {
        let all = true;
        for (let tr = STYLE_MIN; tr <= L.tr; tr++) {
          const hit = winner(siblings, { cm, tr, of, style }) === step;
          if (hit && !any) any = { cm, tr, of };
          all = all && hit;
        }
        if (all) trFree = { cm, of };
      }
    }
    const name = `<b>${STYLE_DE[style]} ★</b>`;
    if (trFree) {
      return `<p class="ok">${tr("Oder mit Trainingsstil {name} (mind. 5 Erfolge, 60 % deiner Erfolge) – dann ist die "
        + "Trainingszahl egal (bei {cm} Pflegefehlern, {of}× überfüttert).", { name, ...trFree })}</p>`;
    }
    if (any) return `<p class="ok">${tr("Auch mit Trainingsstil {name} möglich, z. B. {example}.", { name, example: exampleText(any) })}</p>`;
    return "";
  }

  // ---------------------------------------------------------- Live: dein Digimon jetzt
  // wie _rule_ok in game/pet.py, mit den echten Zählern des Digimon
  function ruleOk(rule, pet, ignoreTr = false) {
    if (rule.any) return rule.any.some(r => ruleOk(r, pet, ignoreTr));
    if (rule.jogress || rule.item) return false;
    const w = rule.win;
    return inRange(pet.mistakes, rule.cm) && (ignoreTr || inRange(pet.trainings, rule.tr))
      && inRange(pet.overfeeds, rule.of) && inRange(pet.battles_stage, rule.btl)
      && inRange(pet.wins_stage, rule.wins)
      && (!w || (pet.battles_stage >= w.battles && pet.wins_stage >= w.wins));
  }

  // Wozu würde es mit den jetzigen Werten digitieren? (wie next_form in game/pet.py)
  function nextForm(pet) {
    const options = optionsOf(pet.dex, pet.line);
    if (pet.style) {
      const fav = options.find(e => ELEMENT_STYLE[D.digimon[e.to].element] === pet.style && ruleOk(e.rule, pet, true));
      if (fav) return fav;
    }
    return options.find(e => ruleOk(e.rule, pet)) || null;
  }

  // Fortschritt für eine Bedingung: [{text, ok}] je Teil (bei ODER: die beste Möglichkeit).
  // have = Rucksack {Item-Key: Anzahl} (für Armor-Eier)
  function progress(rule, pet, have = {}) {
    if (rule.item) {
      return have[rule.item] > 0
        ? [{ text: tr("„{item}“ ist im Rucksack – benutze es (Taste 8)", { item: itemName(rule.item) }), ok: true }]
        : [{ text: tr("„{item}“ fehlt noch – beim Erkunden finden", { item: itemName(rule.item) }), ok: false }];
    }
    if (rule.any) {
      const alts = rule.any.map(r => progress(r, pet, have));
      return alts.reduce((best, a) => (a.filter(x => x.ok).length / Math.max(1, a.length)
        > best.filter(x => x.ok).length / Math.max(1, best.length) ? a : best));
    }
    const out = [];
    const part = (label, have, range) => out.push({
      text: tr("{label}: {have} (nötig: {need})", { label, have, need: rangeText(range) }), ok: inRange(have, range) });
    if (rule.cm) part(tr("Pflegefehler"), pet.mistakes, rule.cm);
    if (rule.tr) part(tr("Trainings"), pet.trainings, rule.tr);
    if (rule.of) part(tr("Überfüttert"), pet.overfeeds, rule.of);
    if (rule.btl) part(tr("Kämpfe"), pet.battles_stage, rule.btl);
    if (rule.wins) part(tr("Siege"), pet.wins_stage, rule.wins);
    if (rule.win) {
      out.push({ text: `${tr("Kämpfe")}: ${pet.battles_stage} / ${rule.win.battles}`, ok: pet.battles_stage >= rule.win.battles });
      out.push({ text: `${tr("Siege")}: ${pet.wins_stage} / ${rule.win.wins}`, ok: pet.wins_stage >= rule.win.wins });
    }
    if (rule.jogress) out.push({ text: jogressText(rule.jogress), ok: false });
    return out;
  }

  return {
    STAGES, STAGE_DE, STAGE_TIME, ATTR_DE, ELEMENT_STYLE, STYLE_DE,
    use, esc, when, rangeText, ruleParts, ruleText, needsBattle, needsFusion, needsItem, itemName, blocked,
    routes, optionsOf, pathTo, recipe, exampleText, styleHint, matches, winner,
    ruleOk, nextForm, progress,
  };
})();
