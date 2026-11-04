// Service worker: makes the pages installable as phone apps and lets them open offline.
// API calls always go to the network, so payment data is never served from a cache.
const CACHE = 'guardrail-v1';
const SHELL = [
  '/senior.html', '/guardian.html', '/phone.html',
  '/icons/senior-192.png', '/icons/guardian-192.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
  // Network first so a redeploy shows up straight away; the cache is only the offline fallback.
  event.respondWith(fetch(event.request).then((res) => {
    if (res.ok) {
      const copy = res.clone();
      caches.open(CACHE).then((cache) => cache.put(event.request, copy));
    }
    return res;
  }).catch(() => caches.match(event.request, { ignoreSearch: true })));
});
