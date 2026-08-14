<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  if (!userStore.connected) {
    goto('/#/login');
  }
</script>

{#if userStore.connected}
  <Navigation currentItem="home" />
  <ConnectedHomepage />
{/if}
