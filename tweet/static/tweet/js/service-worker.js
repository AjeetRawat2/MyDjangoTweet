const CACHE_NAME = 'chai-chatter-static-v2';
const APP_ASSETS = [
  '/static/tweet/css/app.css',
  '/static/tweet/css/redesign.css',
  '/static/tweet/css/chai.css',
  '/static/tweet/js/app.js',
  '/static/tweet/manifest.webmanifest',
  '/static/tweet/images/chai-icon-192.png',
  '/static/tweet/images/chai-icon-512.png',
  '/static/tweet/offline.html'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key.startsWith('chai-chatter-') && key !== CACHE_NAME)
        .map((key) => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request).then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      }))
    );
    return;
  }

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match('/static/tweet/offline.html'))
    );
  }
});
