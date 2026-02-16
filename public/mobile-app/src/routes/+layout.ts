import { userStore } from '$lib/state/User.svelte';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async () => {
  // Initialize user state from localStorage before anything else
  await userStore.checkLoggedIn();
};
