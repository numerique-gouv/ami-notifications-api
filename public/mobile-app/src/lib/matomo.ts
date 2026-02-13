import {
  PUBLIC_MATOMO_CDN_URL,
  PUBLIC_MATOMO_ENABLED,
  PUBLIC_MATOMO_SITE_ID,
  PUBLIC_MATOMO_URL,
} from '$env/static/public';
import { userStore } from '$lib/state/User.svelte';

const MATOMO_ENABLED = PUBLIC_MATOMO_ENABLED === 'true';

export function initMatomo() {
  if (!MATOMO_ENABLED || typeof window === 'undefined') {
    return;
  }

  window._paq = window._paq || [];
  window._paq.push(['setTrackerUrl', `${PUBLIC_MATOMO_URL}matomo.php`]);
  window._paq.push(['setSiteId', PUBLIC_MATOMO_SITE_ID]);
  window._paq.push(['enableLinkTracking']);

  const script = document.createElement('script');
  script.src = `${PUBLIC_MATOMO_CDN_URL}matomo.js`;
  script.async = true;
  document.head.appendChild(script);
}

export function trackPageView(title?: string) {
  if (typeof window === 'undefined') {
    return;
  }

  window._paq = window._paq || [];
  let path = window.location.hash ? window.location.hash.substr(1) : '/';
  if (!userStore.connected && path === '/') {
    path = '/login';
  }
  window._paq.push(['setCustomUrl', path]);
  if (title) {
    window._paq.push(['setDocumentTitle', title]);
  }
  window._paq.push(['trackPageView']);
}
