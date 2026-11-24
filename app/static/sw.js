/* Python Academy service worker — offline app shell + cached learning materials. */
const VERSION = 'python-academy-v1';
const SHELL_CACHE = `${VERSION}-shell`;
const RUNTIME_CACHE = `${VERSION}-runtime`;
const LEARNING_CACHE = `${VERSION}-learning`;

const SHELL_ASSETS = [
  '/',
  '/offline',
  '/manifest.webmanifest',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/js/dashboard.js',
  '/static/js/pathway.js',
  '/static/js/workspace.js',
  '/static/js/library.js',
  '/static/js/topic.js',
  '/static/js/challenges.js',
  '/static/js/playground.js',
  '/static/js/ide.js',
  '/static/js/snippets.js',
  '/static/js/stats.js',
  '/static/js/profile.js',
  '/static/vendor/codemirror/lib_codemirror.min.css',
  '/static/vendor/codemirror/theme_material.min.css',
  '/static/vendor/codemirror/addon_hint_show-hint.min.css',
  '/static/vendor/codemirror/lib_codemirror.min.js',
  '/static/vendor/codemirror/mode_python_python.min.js',
  '/static/vendor/codemirror/addon_edit_matchbrackets.min.js',
  '/static/vendor/codemirror/addon_edit_closebrackets.min.js',
  '/static/vendor/codemirror/addon_comment_comment.min.js',
  '/static/vendor/codemirror/addon_hint_show-hint.min.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then(cache => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => !key.startsWith(VERSION)).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

function isLearningApi(url) {
  return url.pathname === '/api/library' || /^\/api\/library\/[^/]+$/.test(url.pathname);
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request, { ignoreSearch: false });
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok && response.type === 'basic') cache.put(request, response.clone());
  return response;
}

async function navigationHandler(request) {
  try {
    const response = await fetch(request);
    if (response.ok && response.type === 'basic') {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = (await caches.match(request)) || (await caches.match('/offline'));
    return cached || new Response('Offline', { status: 503, headers: { 'Content-Type': 'text/plain' } });
  }
}

const PERSONAL_FIELDS = new Set([
  'bookmarked', 'achievements_unlocked', 'status', 'score', 'last_code', 'updated_at'
]);

function stripPersonalState(value) {
  if (Array.isArray(value)) return value.map(stripPersonalState);
  if (value && typeof value === 'object') {
    const result = {};
    for (const [key, item] of Object.entries(value)) {
      if (!PERSONAL_FIELDS.has(key)) result[key] = stripPersonalState(item);
    }
    return result;
  }
  return value;
}

async function cacheLearningResponse(cache, request, response) {
  if (!response.ok || response.type !== 'basic') return;
  try {
    const data = await response.clone().json();
    const safe = new Response(JSON.stringify(stripPersonalState(data)), {
      status: response.status,
      headers: { 'Content-Type': 'application/json' }
    });
    await cache.put(request, safe);
  } catch (_) {
    // Never cache a malformed or non-JSON response.
  }
}

async function learningApiHandler(request) {
  const cache = await caches.open(LEARNING_CACHE);
  const cached = await cache.match(request);
  const network = fetch(request)
    .then(async response => {
      await cacheLearningResponse(cache, request, response);
      return response;
    })
    .catch(() => null);
  const response = await Promise.race([network, new Promise(resolve => setTimeout(() => resolve(null), 350))]);
  return response || cached || new Response(JSON.stringify({ error: { code: 503, message: 'Offline and no cached copy available.' } }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/api/')) {
    if (isLearningApi(url)) event.respondWith(learningApiHandler(request));
    return; // all other API data stays live (progress, user data, execution)
  }
  if (request.mode === 'navigate') {
    event.respondWith(navigationHandler(request));
    return;
  }
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/sw.js')) {
    event.respondWith(cacheFirst(request, SHELL_CACHE));
    return;
  }
  event.respondWith(cacheFirst(request, RUNTIME_CACHE));
});

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
