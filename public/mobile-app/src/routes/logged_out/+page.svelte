<script lang="ts">
import { globalState } from '$lib/state.svelte.ts'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'

onMount(async () => {
  // We've been redirected to this page by FC after being logged out.
  globalState.isLoggedOut = true
  goto('/')
})
</script>
