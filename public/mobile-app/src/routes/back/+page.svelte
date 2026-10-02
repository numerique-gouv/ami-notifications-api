<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIBackToLastKnownURL } from '$lib/ami-navigation';

  onMount(async () => {
    AMIBackToLastKnownURL();
  });
</script>
