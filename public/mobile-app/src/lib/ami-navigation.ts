import { goto } from '$app/navigation';
import { PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED } from '$env/static/public';
import { isPromotedUrl } from '$lib/urlAliases';
import * as self from './ami-navigation';

export const EXCLUDED_URLS_FROM_HISTORY = [
  '/#/login',
  '/#/silent-login',
  '/#/relogin',
  '/#/login-callback',
  '/#/passkey-authentication',
  '/#/back',
];

const AMIFILogin = (url: string) => {
  window.location.href = `/silent-login-ami-fi?redirect_url=${encodeURIComponent(url)}&from_hash=${window.location.hash.substring(1)}`;
};

export const AMIGoto = (
  link: string,
  silentLogin: boolean = false,
  opts?: {
    replaceState?: boolean | undefined;
  }
) => {
  if (PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED === 'true' && silentLogin) {
    AMIFILogin(link);
    return;
  }

  const isInternal = link === '/' || link.startsWith('/#/');
  let isPromoted = false;
  if (isInternal) {
    isPromoted = isPromotedUrl(link);
  }

  if (isInternal && !EXCLUDED_URLS_FROM_HISTORY.includes(link)) {
    localStorage.setItem('last_visited_internal_url', link);
  }
  if (isInternal && !isPromoted) {
    if (opts !== undefined) {
      goto(link, opts);
    } else {
      goto(link);
    }
  } else if (link.startsWith('/') && !link.startsWith('//')) {
    window.location.href = link;
  } else {
    try {
      const url = new URL(link, window.location.origin);
      const allowedProtocols = ['http:', 'https:'];
      if (!allowedProtocols.includes(url.protocol)) {
        console.warn('Protocol not allowed', url.protocol);
        return;
      }
      localStorage.setItem(
        'webview_back_target',
        JSON.stringify({
          url: localStorage.getItem('last_visited_internal_url') || '/',
          historyLength: history.length,
        })
      );
      window.location.href = url.href;
    } catch {
      console.warn('Invalid URL', link);
    }
  }
};

export const AMIBack = (backUrl: string) => {
  if (history.length > 1) {
    history.back();
  } else {
    self.AMIGoto(backUrl);
  }
};

export const AMIBackToLastKnownURL = () => {
  const target = localStorage.getItem('webview_back_target');

  if (!target) {
    AMIGoto('/', false, { replaceState: true });
    return;
  }

  try {
    const { url, historyLength } = JSON.parse(target) as {
      url: string;
      historyLength: number;
    };

    const currentHistoryLength = history.length;

    const delta = currentHistoryLength - historyLength;

    if (delta > 0) {
      localStorage.removeItem('webview_back_target');
      history.go(-delta);

      return;
    }

    localStorage.removeItem('webview_back_target');
    AMIGoto(url, false, {
      replaceState: true,
    });
  } catch {
    console.warn('Invalid target', target);
    localStorage.removeItem('webview_back_target');
    AMIGoto('/', false, {
      replaceState: true,
    });
  }
};
