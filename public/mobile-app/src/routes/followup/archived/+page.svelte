<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-goto';
  import Followup from '$lib/components/Followup.svelte';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/');
      return;
    }
  });
</script>

<Followup archived={true} />
