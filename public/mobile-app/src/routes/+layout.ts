import { page } from '$app/state';
import { PUBLIC_PROMPT_FOR_ACCESS_KEY } from '$env/static/public';
import { initializeData } from '$lib/initializeDataFromAPI';
import { userStore } from '$lib/state/User.svelte';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async () => {
  if (!window.NativeBridge && PUBLIC_PROMPT_FOR_ACCESS_KEY) {
    let access_key: string = '';
    const access_key_cookie = await window.cookieStore.get('access_key');
    if (!access_key_cookie) {
      const day = 24 * 60 * 60 * 1000;
      access_key = prompt(PUBLIC_PROMPT_FOR_ACCESS_KEY) || '';
      await window.cookieStore.set({
        name: 'access_key',
        value: access_key,
        expires: Date.now() + 7 * day,
      });
    } else {
      access_key = access_key_cookie.value || '';
    }
    const response = await fetch('/api/v1/access-key', {
      method: 'POST',
      body: new URLSearchParams({ key: access_key }),
    });
    if (response.status !== 200) {
      await cookieStore.delete('access_key');
      (window as Window).location = '/';
    }
  }
  // Initialize user state from localStorage before anything else
  if (localStorage.getItem('is_logged_in')) {
    await initializeData(page.url.searchParams, userStore);
  }
};
