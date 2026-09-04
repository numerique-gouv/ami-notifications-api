<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { AMIGoto } from '$lib/ami-navigation';

  onMount(async () => {
    const searchParams = page.url.searchParams;
    if (
      localStorage.getItem('id_token') === null &&
      searchParams.get('id_token') !== ''
    ) {
      localStorage.setItem('id_token', searchParams.get('id_token') || '');
    }
    if (searchParams.has('redirect_url')) {
      AMIGoto(searchParams.get('redirect_url') || '');
    } else {
      AMIGoto('/');
    }
  });
</script>
