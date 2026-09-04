<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';

  onMount(() => {
    AMIGoto('/#/welcome/notifications', false, {
      replaceState: true,
    });
  });
</script>
