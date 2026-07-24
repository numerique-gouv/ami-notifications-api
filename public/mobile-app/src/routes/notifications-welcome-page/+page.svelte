<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-goto';

  onMount(() => {
    AMIGoto('/#/welcome/notifications', false, {
      replaceState: true,
    });
  });
</script>
