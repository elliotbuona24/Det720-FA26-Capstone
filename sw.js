// Service worker: lets the board open with a weak or no signal.
// The page itself is network-first (always the newest version when online, the saved copy when not).
// Intel images, the Firebase SDK and fonts are kept after the first load.
// Bump CACHE (v2, v3...) only to force every phone to drop its saved copies.
const CACHE = 'marala-board-v1';
const NET_WAIT = 4000;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.add(new Request('./', { cache:'reload' }))).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('marala-board-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

// Network first, falling back to the saved copy after NET_WAIT ms or when offline.
function pageFirst(req){
  return new Promise(resolve => {
    let done = false;
    const fromCache = () => caches.match(req, { ignoreSearch:true }).then(r => r || caches.match('./'));
    const timer = setTimeout(() => fromCache().then(r => { if (r && !done){ done = true; resolve(r); } }), NET_WAIT);
    fetch(req).then(r => {
      if (r && r.ok){ const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      if (!done){ done = true; clearTimeout(timer); resolve(r); }
    }).catch(() => fromCache().then(r => { if (!done){ done = true; clearTimeout(timer); resolve(r || Response.error()); } }));
  });
}

// Saved copy first, refreshed from the network in the background.
function keepCopy(req){
  return caches.open(CACHE).then(c => c.match(req).then(hit => {
    const net = fetch(req).then(r => { if (r && (r.ok || r.type === 'opaque')) c.put(req, r.clone()); return r; }).catch(() => hit);
    return hit || net;
  }));
}

// Which requests use which strategy. Everything else goes straight to the network.
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (req.mode === 'navigate' && u.origin === location.origin){ e.respondWith(pageFirst(req)); return; }
  if (u.origin === location.origin && /\/intel\/[^/]+\.(jpe?g|png|webp)$/i.test(u.pathname)){ e.respondWith(keepCopy(req)); return; }
  if (u.hostname === 'www.gstatic.com' && u.pathname.startsWith('/firebasejs/')){ e.respondWith(keepCopy(req)); return; }
  if (u.hostname === 'fonts.googleapis.com' || u.hostname === 'fonts.gstatic.com'){ e.respondWith(keepCopy(req)); return; }
});
