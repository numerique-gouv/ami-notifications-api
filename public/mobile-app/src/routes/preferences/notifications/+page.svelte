<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIBack, AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/preferences';

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<div class="preferences-page">
  <NavWithBackButton title="Notifications" {backUrl} />

  <button
    class="fr-btn fr-btn--secondary fr-btn--lg save-preferences-button"
    type="button"
    onclick={() => AMIBack(backUrl)}
    title="Retour à la page précédente"
    aria-label="Retour à la page précédente"
    data-testid="close-button"
  >
    Fermer
  </button>
</div>

<style>
  .preferences-page {
    .preferences-content-container {
      padding: 0 1rem;
    }
    .save-preferences-button {
      position: fixed;
      bottom: 1rem;
      left: 50%;
      transform: translateX(-50%);

      display: block;
      width: 328px;
    }
  }
</style>
