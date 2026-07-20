import { goto } from '$app/navigation';
import {
  PUBLIC_API_URL,
  PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED,
} from '$env/static/public';

const AMIFILogin = async (url: string) => {
  window.location.href = `${PUBLIC_API_URL}/silent-login-ami-fi?redirect_url=${encodeURIComponent(url)}`;
};

export const AMIGoto = async (url: string, silentLogin: boolean = false) => {
  if (PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED === 'true' && silentLogin) {
    AMIFILogin(url);
  } else if (url.startsWith('/')) {
    goto(url);
  } else {
    window.location.href = url;
  }
};
