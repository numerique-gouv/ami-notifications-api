import { browser } from '$app/environment';
import { page } from '$app/state';
import { initializeData } from '$lib/initializeDataFromAPI';
import { userStore } from '$lib/state/User.svelte';
import type { LayoutLoad } from './$types';

export const prerender = true;
export const trailingSlash = 'always';

export const load: LayoutLoad = async () => {
  // Initialize user state from localStorage before anything else
  if (browser && localStorage.getItem('is_logged_in')) {
    await initializeData(page.url.searchParams, userStore);
  }
};
