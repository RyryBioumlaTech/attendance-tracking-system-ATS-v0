const CACHE_NAME = "ats-cache-v1";  
const urlsToCache = [
  "/", // page d’accueil Flask
  "/scanner", // ta route Flask
  "/static/style/bootstrap.min.css",
  "/static/style/login.css",
  "/static/js/scanner.js",
  "/static/js/bootstrap.bundle.min.js",
  "/static/js/login.js",
  "/static/js/socket.io.min.js",
  "/static/js/html5-qrcode.min.js",
  "/static/icons/bootstrap-icons.css",
  "/static/icons/qr-code.png"
];

// 1️⃣ Installation -> mettre en cache les fichiers essentiels
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// 2️⃣ Activation -> nettoyer les anciens caches si nécessaire
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
      );
    })
  );
});