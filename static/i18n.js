"use strict";
// Sprache: Deutsch (Standard) oder Englisch.
// Im Code stehen alle Texte auf Deutsch; tr("…") liefert sie in der gewählten Sprache.
// Die englischen Fassungen kommen aus static/i18n/en-*.js (I18N.add({deutsch: englisch})).
// Schlüssel ist der deutsche Text MIT Platzhaltern:  tr("{name} schläft.", { name })
// Fehlt eine Übersetzung, bleibt es deutsch.
//
// Feste Texte in den HTML-Seiten übersetzt I18N.translatePage(): Text-Knoten und die
// Attribute title / aria-label / placeholder, deren (deutscher) Text im Wörterbuch steht.
// Absätze mit <b> & Co. bekommen data-i18n – dann ist das ganze innerHTML der Schlüssel.
//
// Die Sprache gilt pro Gerät (Cookie "vpet_lang", damit auch der Server sie kennt) und
// wird zusätzlich im Konto gespeichert (/api/lang), damit sie auf allen Geräten gilt.

const I18N = (() => {
  const COOKIE = "vpet_lang";
  const LANGS = ["de", "en"];
  const EN = Object.create(null);

  function readLang() {
    const m = /(?:^|;\s*)vpet_lang=(de|en)/.exec(document.cookie);
    if (m) return m[1];
    try {
      const saved = localStorage.getItem("vpet.lang");
      if (LANGS.includes(saved)) return saved;
    } catch { /* ohne localStorage: Standard */ }
    return "de";
  }

  let lang = readLang();
  document.documentElement.lang = lang;
  // Cookie bei jedem Besuch erneuern: Safari & Co. löschen Cookies aus JavaScript nach ein paar
  // Tagen – dann käme die Sprache nur noch aus localStorage und der Server spräche Deutsch
  // (Tagebuch, Berichte …), obwohl das Spiel Englisch zeigt
  writeCookie(lang);

  function writeCookie(value) {
    document.cookie = `${COOKIE}=${value}; Path=/; Max-Age=${5 * 365 * 86400}; SameSite=Lax`;
  }

  function add(dict) { Object.assign(EN, dict); }

  const norm = s => s.replace(/\s+/g, " ").trim();

  function tr(de, vars) {
    let s = lang === "en" && EN[de] !== undefined ? EN[de] : de;
    if (vars) s = s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m));
    return s;
  }

  // Sprache wechseln (Cookie + localStorage); neu laden muss der Aufrufer
  function set(value) {
    if (!LANGS.includes(value)) return;
    lang = value;
    writeCookie(value);
    try { localStorage.setItem("vpet.lang", value); } catch { /* egal */ }
    document.documentElement.lang = value;
  }

  // feste Texte einer Seite übersetzen (nur nötig, wenn Englisch gewählt ist)
  function translatePage(root = document.body) {
    if (lang !== "en" || !root) return;
    root.querySelectorAll("[data-i18n]").forEach(el => {
      const key = norm(el.innerHTML);
      if (EN[key] !== undefined) el.innerHTML = EN[key];
    });
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (node.parentElement && node.parentElement.closest("[data-i18n], script, style, template, [data-no-i18n]")) continue;
      const key = norm(node.nodeValue);
      if (key && EN[key] !== undefined) {
        const lead = /^\s*/.exec(node.nodeValue)[0], tail = /\s*$/.exec(node.nodeValue)[0];
        node.nodeValue = lead + EN[key] + tail;
      }
    }
    for (const attr of ["title", "aria-label", "placeholder"]) {
      root.querySelectorAll(`[${attr}]`).forEach(el => {
        const key = norm(el.getAttribute(attr));
        if (EN[key] !== undefined) el.setAttribute(attr, EN[key]);
      });
    }
    if (root === document.body && EN[document.title] !== undefined) document.title = EN[document.title];
  }

  // Link mit ?lang=en (z. B. für Freunde ohne Deutsch) stellt die Sprache gleich um
  // (danach aus der Adresse entfernen, sonst gewinnt der Link bei jedem Neuladen)
  const params = new URLSearchParams(location.search);
  const fromUrl = LANGS.includes(params.get("lang"));
  if (fromUrl) {
    set(params.get("lang"));
    params.delete("lang");
    const query = params.toString();
    history.replaceState(history.state, "", location.pathname + (query ? `?${query}` : "") + location.hash);
  }

  return {
    get lang() { return lang; },
    fromUrl,                  // Sprache kam gerade aus dem Link -> fürs Konto übernehmen
    LANGS, add, tr, set, translatePage,
    // für Datum/Uhrzeit (toLocaleString)
    locale: () => (lang === "en" ? "en-GB" : "de-DE"),
  };
})();

const tr = I18N.tr;
