<script>
import '@gouvfr/dsfr/dist/dsfr.min.css'
import '@gouvfr/dsfr/dist/utility/utility.min.css'
import { onMount } from 'svelte'
import { userStore } from '$lib/state/User.svelte'

let { children } = $props()

onMount(async () => {
  // Initialize user state from localStorage before anything else
  await userStore.checkLoggedIn()

  // @ts-ignore
  await import('@gouvfr/dsfr/dist/dsfr.module.min.js')
})
</script>

{@render children()}
