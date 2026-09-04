<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { AMIGoto } from '$lib/ami-navigation';
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  if (page.url.searchParams.has('is_logged_out')) {
    AMIGoto('/?is_logged_out#/login');
  }

  if (!userStore.connected) {
    AMIGoto('/#/login');
  }

  if (page.url.searchParams.has('passkey_toast')) {
    toastStore.addToast('La clé a bien été ajoutée', 'success', 3000, false);
  }
  if (page.url.searchParams.has('user_does_not_match')) {
    toastStore.addToast(
      'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
      'warning',
      null,
      true
    );
    const hash = page.url.searchParams.get('redirect_to_hash') || '';
    if (hash !== '') {
      AMIGoto(`/#${hash}`);
    }
  }
</script>

{#if userStore.connected}
  <Navigation currentItem="home" />
  <ConnectedHomepage />
{/if}
