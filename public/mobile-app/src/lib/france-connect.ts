import { AMIGoto } from '$lib/ami-navigation';
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

export const franceConnectLogout = async (id_token_hint: string) => {
  AMIGoto(`/logout-france-connect?id_token_hint=${id_token_hint}`);
};
