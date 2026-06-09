<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Navigation from '$lib/components/Navigation.svelte';
  import Requests from '$lib/components/Requests.svelte';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }
  });
</script>

<Requests />
<Navigation currentItem="requests" />
