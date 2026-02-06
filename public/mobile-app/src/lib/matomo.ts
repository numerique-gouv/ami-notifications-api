import {
  PUBLIC_MATOMO_CDN_URL,
  PUBLIC_MATOMO_ENABLED,
  PUBLIC_MATOMO_SITE_ID,
  PUBLIC_MATOMO_URL,
} from '$env/static/public'

const MATOMO_ENABLED = PUBLIC_MATOMO_ENABLED === 'true'

export function initMatomo() {
  if (!MATOMO_ENABLED || typeof window === 'undefined') return

  window._paq = window._paq || []
  window._paq.push(['setTrackerUrl', `${PUBLIC_MATOMO_URL}matomo.php`])
  window._paq.push(['setSiteId', PUBLIC_MATOMO_SITE_ID])
  window._paq.push(['enableLinkTracking'])

  const script = document.createElement('script')
  script.src = `${PUBLIC_MATOMO_CDN_URL}matomo.js`
  script.async = true
  document.head.appendChild(script)
}

function getPath() {
  if (typeof window === 'undefined') {
    return '/'
  }

  const hash = window.location.hash || '#/'
  return hash ? `/${hash}` : '/'
}

export function trackPageView(title?: string) {
  if (!MATOMO_ENABLED || !window._paq) {
    return
  }

  const path = getPath()
  window._paq.push(['setCustomUrl', path])
  if (title) {
    window._paq.push(['setDocumentTitle', title])
  }
  window._paq.push(['trackPageView'])
}
