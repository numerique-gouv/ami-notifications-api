<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import Followup from '$lib/components/followup/Followup.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<svelte:head>
  <title>Mes démarches</title>
</svelte:head>

<Navigation currentItem="followup" />

{#if userStore.connected}
  <Followup />
{/if}
