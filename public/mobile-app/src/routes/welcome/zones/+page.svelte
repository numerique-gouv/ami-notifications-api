<script lang="ts">
  import { page } from '$app/state';
  import ZonePreferences from '$lib/components/ZonePreferences.svelte';
  import { toastStore } from '$lib/state/toast.svelte';

  if (page.url.searchParams.has('passkey_toast')) {
    toastStore.addToast('La clé a bien été ajoutée', 'success', 3000, false);
  }
</script>

<svelte:head>
  <title>Bienvenue - zones scolaires</title>
</svelte:head>

<ZonePreferences fromPage="welcome" />
