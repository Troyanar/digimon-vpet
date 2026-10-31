// Service Worker: macht das Spiel als App installierbar und lÃ¤dt die
// Spieldateien auch bei kurzem Funkloch. Immer zuerst das Netz fragen, damit
// Updates sofort ankommen; nur wenn das nicht klappt, die gespeicherte Kopie.
const CACHE = "vpet-v8";
const SHELL = ["/", "/index.html", "/style.css", "/i18n.js", "/i18n/en-game.js", "/i18n/en-rules.js",
  "/i18n/en-help.js", "/game.js", "/rules.js", "/hilfe.html", "/hilfe.js",
  "/data/digimon.json", "/manifest.webmanifest", "/icons/icon-192.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  // Spielstand (API) nie aus dem Speicher â€“ der muss immer frisch sein
  if (e.request.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        // nur gute Antworten merken â€“ keine Fehlerseiten
        if (res.ok && res.status === 200 && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});

// Klick auf eine Benachrichtigung (Handy): Spiel Ã¶ffnen bzw. nach vorne holen
self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
    const open = list.find(c => new URL(c.url).origin === location.origin);
    return open ? open.focus() : self.clients.openWindow("/");
  }));
});
