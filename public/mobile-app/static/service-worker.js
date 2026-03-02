// Register event listener for the 'push' event.
self.addEventListener('push', (event) => {
  if (!(self.Notification && self.Notification.permission === 'granted')) {
    console.log('no permission to display notification');
    return;
  }

  const json_data = event.data?.json();

  // Keep the service worker alive until the notification is created.
  event.waitUntil(
    self.registration.showNotification(json_data.title, {
      body: `From ${json_data.sender}: ${json_data.message}`,
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  // This looks to see if the current is already open and focuses if it is
  event.waitUntil(
    clients
      .matchAll({
        type: 'window',
      })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
  );
});

/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />
/// <reference types="@sveltejs/kit" />

import { build, files, version } from '$service-worker';

// SW global
const sw = /** @type {ServiceWorkerGlobalScope} */ (self);

const CACHE_NAME = `static-cache-${version}`;

// Assets générés par SvelteKit (JS/CSS/HTML) + /static
const ASSETS = [...build, ...files];

// Installation : pré‑cache des assets connus
sw.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      await cache.addAll(ASSETS);
      sw.skipWaiting();
    })()
  );
});

// Activation : nettoyage des anciens caches
sw.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
      sw.clients.claim();
    })()
  );
});

// Stratégie de fetch
sw.addEventListener('fetch', (event) => {
  const { request } = event;

  // On ne gère que GET
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // 1) Assets connus : cache‑first
  if (ASSETS.includes(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // 2) Routes app (adapter-static + fallback index.html) : network‑first avec fallback cache
  if (url.origin === sw.location.origin) {
    event.respondWith(networkFirst(request));
    return;
  }

  // 3) Autres origines (APIs externes) : network‑first simple ou autre stratégie selon besoin
});

// Helpers
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  if (response.ok) {
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    if (cached) return cached;

    // Optionnel : fallback vers index.html pour les routes d’app
    const fallback = await cache.match('/index.html');
    if (fallback) return fallback;

    // Laisse SvelteKit déclencher +error.svelte
    throw new Error('Network error and no cache');
  }
}
