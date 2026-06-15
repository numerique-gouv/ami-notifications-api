import {
  PUBLIC_APP_URL,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_LOGOUT_ENDPOINT,
  PUBLIC_FC_PROXY_BASE_URL,
} from '$env/static/public';
import type { UserInfo } from '$lib/state/User.svelte';

export function parseJwt(token: string): UserInfo {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    window
      .atob(base64)
      .split('')
      .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
      .join('')
  );

  return JSON.parse(jsonPayload);
}

export const franceConnectLogout = async (
  id_token_hint: string,
  redirect_url: string | null = null
) => {
  const redirect_uri = encodeURIComponent(
    redirect_url || `${PUBLIC_APP_URL}/?is_logged_out`
  );
  let post_logout_redirect_uri = redirect_uri;
  if (PUBLIC_FC_PROXY_BASE_URL) {
    post_logout_redirect_uri = `${PUBLIC_FC_PROXY_BASE_URL}/`;
  }
  const params = new URLSearchParams({
    id_token_hint,
    state: redirect_uri,
    post_logout_redirect_uri: post_logout_redirect_uri,
  });
  const url = new URL(`${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}`);
  url.search = params.toString();

  // Now logout from FC.
  window.location.href = url.toString();
};
