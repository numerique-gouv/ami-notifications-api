<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Followup from '$lib/components/Followup.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }
  });
</script>

<Followup />
<Navigation currentItem="followup" />
