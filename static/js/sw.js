const CACHE = 'anik-tech-v1';
const ASSETS = ['/','/programs','/about','/admissions','/contact','/gallery',
  '/student/login','/static/css/style.css','/static/css/admin.css','/static/css/portal.css',
  '/static/icons/icon-192x192.png','/static/icons/icon-512x512.png','/manifest.json'];

self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || e.request.url.includes('/admin')) return;
  e.respondWith(
    fetch(e.request).then(r => { const c=r.clone(); caches.open(CACHE).then(ch=>ch.put(e.request,c)); return r; })
    .catch(() => caches.match(e.request).then(r => r || new Response('<h1>Offline</h1><p>No internet connection.</p>',{headers:{'Content-Type':'text/html'}})))
  );
});
