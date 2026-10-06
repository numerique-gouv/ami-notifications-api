<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { AMIBack, AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import { trackZoneCount } from '$lib/matomo';
  import { Preferences, type ZoneInfo } from '$lib/state/preferences';
  import { userStore } from '$lib/state/User.svelte';

  let zoneInfos: ZoneInfo[] = $state([]);
  let userHasAddresses: boolean = $state(false);
  let zonesVisible: boolean = $state(true);
  let zonesHasChanged: boolean = $state(false);

  interface Props {
    fromPage: 'preferences' | 'welcome';
  }

  let { fromPage }: Props = $props();

  let backUrl: string = $derived(
    fromPage === 'welcome' ? '/#/welcome/zones' : '/#/preferences'
  );

  const refreshPreferences = () => {
    if (!userStore.connected) {
      return;
    }
    zoneInfos = userStore.connected.getZoneInfosFromPreferences();
    userHasAddresses = userStore.connected.identity.preferences.addresses.length > 0;
  };

  onMount(() => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    } else {
      refreshPreferences();
    }
  });

  onDestroy(() => {
    if (zonesHasChanged) {
      if (!userStore.connected) {
        return;
      }
      const preferences = userStore.connected.identity.preferences;
      trackZoneCount(preferences.zones.length);
    }
  });

  const saveZones = async (id: string, checked: boolean) => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    if (checked) {
      preferences.addZone(id);
    } else {
      preferences.removeZone(id);
    }
    userStore.connected.setPreferences(preferences);
    refreshPreferences();
    zonesHasChanged = true;
  };

  const removeAddress = async (id: string) => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    const matchingAddresses = preferences.addresses.filter(
      (address) => address.idBAN.toString() === id.replace('city-', '')
    );
    if (matchingAddresses.length) {
      preferences.removeAddress(matchingAddresses[0]);
      userStore.connected.setPreferences(preferences);
      refreshPreferences();
    }
  };

  const clearAddresses = async () => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    preferences.clearAddresses();
    userStore.connected.setPreferences(preferences);
    refreshPreferences();
  };

  const goToNotificationsWelcomePage = () => {
    AMIGoto('/#/notifications-welcome-page');
    /* to be replaced by:
     * AMIGoto('/#/welcome/notifications')
     * when app mobile is ready to intercept this new url
     */
  };
</script>

<div class="zones fr-px-2w">
  {#if fromPage === 'preferences'}
    <NavWithBackButton title="Zones scolaires" {backUrl} />
  {:else}
    <h1 class="fr-h3 fr-pt-3w">Zones scolaires</h1>
  {/if}
  <div class="zones-content fr-pb-9w {fromPage === 'preferences' ? 'fr-pt-14w': ''}">
    <div class="preferences-city-search-container fr-mb-3w">
      <p class="fr-mb-1w">
        Quelles zones scolaires et communes associées voulez-vous voir affichées dans
        votre agenda&nbsp;?
      </p>
      <div class="preferences-city-add">
        <button
          type="button"
          class="fr-btn fr-btn--secondary am-btn-w100"
          onclick={() => AMIGoto('/#/preferences/zones/city')}
          data-testid="add-address"
        >
          Ajouter des communes
        </button>
      </div>
      {#if userHasAddresses}
        <div class="preferences-city-clear fr-pt-2w">
          <button
            type="button"
            class="fr-btn fr-btn--tertiary"
            onclick={clearAddresses}
            data-testid="clear-addresses"
            aria-label="Réinitialiser les communes"
          >
            Réinitialiser
          </button>
        </div>
      {/if}
    </div>

    <div class="preferences-content-container">
      <div class="fr-pb-3w am-toggle-container">
        {#each zoneInfos as zoneInfo}
          <Toggle
            id={zoneInfo.zone}
            label={zoneInfo.zone}
            isChecked={zoneInfo.selected}
            onChangeAction={saveZones}
            onRemoveAction={removeAddress}
            tags={zoneInfo.tags}
          />
        {/each}
      </div>
    </div>
  </div>
  <div class="fr-p-2w zones-footer">
    {#if fromPage === 'preferences'}
      <button
        class="fr-btn fr-btn--secondary cancel-button am-btn-w100"
        type="button"
        onclick={() => AMIBack(backUrl)}
        data-testid="close-button"
      >
        Fermer
      </button>
    {:else}
      <button
        type="button"
        class="fr-btn fr-btn--tertiary-no-outline fr-icon-arrow-right-line fr-btn--icon-right am-btn-w100"
        onclick={goToNotificationsWelcomePage}
        data-testid="skip-button"
      >
        Passer
      </button>
    {/if}
  </div>
</div>

<style>
  .zones {
    .zones-footer {
      z-index: 400;
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      background-color: var(--background-lifted-grey);
      border-top: 1px solid var(--border-default-grey);
      button.fr-btn--tertiary-no-outline {
        text-decoration: underline;
        text-underline-offset: 0.125rem;
      }
    }
  }
</style>
