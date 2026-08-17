<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { initializeLocalStorage } from '$lib/initializeDataFromAPI';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    try {
      initializeLocalStorage(page.url.searchParams);
      await userStore.buildUser();
      if (!userStore.connected) {
        goto('/#/login');
      } else if (page.url.searchParams.get('user_first_login') === 'true') {
        goto('/#/welcome/zones');
      } else {
        goto('/');
      }
    } catch (error) {
      console.error(error);
      goto('/#/login');
    }
  });
</script>

<p>Redirection vers l’accueil</p>
