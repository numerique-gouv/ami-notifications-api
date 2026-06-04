<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';

  onMount(async () => {
    const searchParams = page.url.searchParams;
    if (searchParams.has('is_logged_in')) {
      if (
        localStorage.getItem('id_token') === null &&
        searchParams.get('id_token') !== ''
      ) {
        localStorage.setItem('id_token', searchParams.get('id_token') || '');
      }
    }
    if (searchParams.has('redirect_url')) {
      window.location.href = searchParams.get('redirect_url') || '';
    } else {
      goto('/');
    }
  });
</script>
