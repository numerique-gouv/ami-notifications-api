import { goto } from '$app/navigation';
import {
  PUBLIC_API_URL,
  PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED,
} from '$env/static/public';

export const AMIUrl = (url: string, silentLogin: boolean = false): string => {
  if (PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED === 'true' && silentLogin && url) {
    return `${PUBLIC_API_URL}/silent-login-ami-fi?redirect_url=${encodeURIComponent(url)}`;
  }
  return url;
};

export const AMIGoto = async (
  url: string,
  silentLogin: boolean = false,
  opts?: {
    replaceState?: boolean | undefined;
  }
) => {
  const newUrl = AMIUrl(url, silentLogin);
  if (newUrl.startsWith('/')) {
    goto(url, opts);
  } else {
    window.location.href = newUrl;
  }
};
