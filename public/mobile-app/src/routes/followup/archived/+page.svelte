<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import Followup from '$lib/components/followup/Followup.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  const backUrl = '/#/followup';

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<NavWithBackButton title="Démarches archivées" {backUrl} />
{#if userStore.connected}
  <Followup archived={true} />
{/if}
