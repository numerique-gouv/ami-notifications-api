<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { zones } from '$lib/address';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import { Preferences } from '$lib/state/preferences';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/preferences';
  let userZones: string[] = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    } else {
      userZones = userStore.connected!.identity.preferences.zones;
    }
  });

  const navigateToPreviousPage = async () => {
    goto(backUrl);
  };

  const saveSettings = async (id: string, checked: boolean) => {
    const preferences = userStore.connected!.identity.preferences;
    if (checked) {
      preferences.addZone(id);
    } else {
      preferences.removeZone(id);
    }
    userStore.connected!.setPreferences(preferences);
  };
</script>

<div class="preferences-page">
  <NavWithBackButton title="Zones scolaires" {backUrl} />

  <div class="preferences-content-container">
    {#each zones as zone}
      <Toggle
        id={zone.label}
        label={zone.label}
        isChecked={userZones.includes(zone.label)}
        onChangeAction={saveSettings}
      />
    {/each}
  </div>

  <div class="preferences-button-container">
    <button
      class="fr-btn fr-btn--secondary fr-btn--lg save-preferences-button"
      type="button"
      onclick={navigateToPreviousPage}
      title="Retour à la page précédente"
      aria-label="Retour à la page précédente"
      data-testid="close-button"
    >
      Fermer
    </button>
  </div>
</div>

<style>
  .preferences-page {
    .preferences-content-container {
      margin-bottom: 68px;
    }
    .preferences-button-container {
      display: flex;
      background: var(--background-default-grey);
      width: 100%;
      position: fixed;
      bottom: 0;
      justify-content: center;
      padding: 1rem 0;
      .save-preferences-button {
        display: block;
        width: 328px;
      }
    }
  }
</style>
