<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { initializeData } from '$lib/initializeDataFromAPI';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    // User state already initialized in +layout.svelte

    try {
      if (page.url.searchParams.has('is_logged_in')) {
        await initializeData(page.url.searchParams, userStore);
        if (page.url.searchParams.get('user_first_login') === 'true') {
          goto('/#/welcome/zones');
        } else {
          goto('/');
        }
      }
      if (page.url.searchParams.has('is_logged_out')) {
        goto('/?is_logged_out#/login');
      }
    } catch (error) {
      console.error(error);
    }
  });

  if (!userStore.connected) {
    goto('/#/login');
  }
</script>

{#if userStore.connected}
  <Navigation currentItem="home" />
  <ConnectedHomepage />
{/if}
