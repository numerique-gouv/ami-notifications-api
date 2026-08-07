<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  if (!userStore.connected) {
    goto('/#/login');
  }

  if (page.url.searchParams.has('passkey_toast')) {
    toastStore.addToast('La clé a bien été ajoutée', 'success', 3000, false);
  }
</script>

{#if userStore.connected}
  <Navigation currentItem="home" />
  <ConnectedHomepage />
{/if}
