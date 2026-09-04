import { goto } from '$app/navigation';
import { PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED } from '$env/static/public';
import * as self from './ami-navigation';

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
  } else if (link.startsWith('/') && !link.startsWith('//')) {
    if (opts !== undefined) {
      goto(link, opts);
    } else {
      goto(link);
    }
  } else {
    try {
      const url = new URL(link, window.location.origin);
      const allowedProtocols = ['http:', 'https:'];
      if (!allowedProtocols.includes(url.protocol)) {
        console.warn('Protocol not allowed', url.protocol);
        return;
      }
      window.location.href = url.href;
    } catch (e) {
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
