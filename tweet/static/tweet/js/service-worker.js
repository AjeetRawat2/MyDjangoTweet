const CACHE_NAME = 'chai-chatter-static-v3';
const MEDIA_CACHE_NAME = 'chai-chatter-media-v1';
const APP_ASSETS = [
  '/static/tweet/css/app.css',
  '/static/tweet/css/redesign.css',
  '/static/tweet/css/chai.css',
  '/static/tweet/css/pwa.css',
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
      keys.filter((key) =>
        key.startsWith('chai-chatter-') &&
        key !== CACHE_NAME &&
        key !== MEDIA_CACHE_NAME
      ).map((key) => caches.delete(key))
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
      caches.open(CACHE_NAME).then(async (cache) => {
        const cached = await cache.match(request);
        if (cached) return cached;
        const response = await fetch(request);
        if (response.ok) await cache.put(request, response.clone());
        return response;
      })
    );
    return;
  }

  if (url.pathname.startsWith('/media/')) {
    event.respondWith(
      fetch(request).then(async (response) => {
        if (response.ok && (response.headers.get('content-type') || '').startsWith('image/')) {
          const cache = await caches.open(MEDIA_CACHE_NAME);
          await cache.put(request, response.clone());
          const keys = await cache.keys();
          if (keys.length > 80) await cache.delete(keys[0]);
        }
        return response;
      }).catch(async () => {
        const cached = await caches.match(request);
        return cached || Response.error();
      })
    );
    return;
  }

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        return await fetch(request);
      } catch (_firstError) {
        if (self.navigator.onLine) {
          await new Promise((resolve) => setTimeout(resolve, 700));
          try {
            return await fetch(request);
          } catch (_retryError) {
            // Fall through to the offline page when both network attempts fail.
          }
        }
        const offlinePage = await caches.open(CACHE_NAME).then(
          (cache) => cache.match('/static/tweet/offline.html')
        );
        return offlinePage || new Response(
          'Chai & Chatter cannot connect right now. Please try again.',
          {status: 503, headers: {'Content-Type': 'text/plain; charset=utf-8'}}
        );
      }
    })());
  }
});
