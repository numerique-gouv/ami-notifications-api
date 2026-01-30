import { userStore } from '$lib/state/User.svelte'
import type { LayoutLoad } from './$types'

export const load: LayoutLoad = async () => {
  // Initialize user state from localStorage before anything else
  // TODO CLO : utile de faire ça si c'est déjà fait dans src/routes/+page.svelte ?
  await userStore.checkLoggedIn()
}
