/* Dietario · funcionamiento sin conexión.
   Páginas: primero la red y, si no hay conexión, la copia guardada. Archivos estáticos: la copia guardada y se actualiza en segundo plano.
   No se guarda nada que el usuario escriba: el registro de presión y glicemia vive en localStorage, no aquí. */
var V = "dietario-v2-2";
var CORE = ["/index.html", "/assets/app.css", "/assets/app.js", "/assets/favicon.svg", "/salud/index.html", "/registro/index.html",
  "/assets/registro.js", "/assets/qrcode.js", "/dietas/index.html", "/dietas/dash.html", "/dietas/fodmap.html", "/assets/ficha.css", "/nosotros.html"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(V).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== V; }).map(function (k) { return caches.delete(k); })); })
    .then(function () { return self.clients.claim(); }));
});
function guardable(r) { return r && r.ok && r.type === "basic" && !r.redirected; }
self.addEventListener("fetch", function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || url.pathname.indexOf("/api/") === 0) return;
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(function (r) {
      if (guardable(r)) { var c = r.clone(); caches.open(V).then(function (k) { k.put(req, c); }); }
      return r;
    }).catch(function () { return caches.match(req, { ignoreSearch: true }).then(function (m) { return m || caches.match("/index.html"); }); }));
    return;
  }
  e.respondWith(caches.match(req).then(function (m) {
    var red = fetch(req).then(function (r) { if (guardable(r)) { var c = r.clone(); caches.open(V).then(function (k) { k.put(req, c); }); } return r; }).catch(function () { return m; });
    return m || red;
  }));
});
