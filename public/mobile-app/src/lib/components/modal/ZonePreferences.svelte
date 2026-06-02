<script lang="ts">
  import { mount, onMount, unmount } from 'svelte';
  import { slide } from 'svelte/transition';
  import { goto } from '$app/navigation';
  import { Address } from '$lib/address';
  import {
    callGeoAPI,
    cityToBAN,
    type ResponseFromGeoAPI,
  } from '$lib/citiesFromGeoAPIAndBAN';
  import Toggle from '$lib/components/Toggle.svelte';
  import { Preferences, type ZoneInfo } from '$lib/state/preferences';
  import { userStore } from '$lib/state/User.svelte';
  import NavWithBackButton from './NavWithBackButton.svelte';
  import ZonePreferencesFooter from './ZonePreferencesFooter.svelte';

  let backUrl: string = '/#/preferences';
  let zoneInfos: ZoneInfo[] = $state([]);
  let userHasAddresses: boolean = $state(false);
  let timer: ReturnType<typeof setTimeout>;
  let inputValue: string = $state('');
  let filteredCities: ResponseFromGeoAPI[] = $state([]);
  let cityApiHasError: boolean = $state(false);
  let zonesVisible: boolean = $state(true);

  interface Props {
    footerTarget?: HTMLElement | null;
    getFooterTarget?: (() => HTMLElement | null) | null;
    onClose?: (() => void) | null;
    toggleModalElements?: ((visible: boolean) => void) | null;
  }

  let {
    footerTarget = null,
    getFooterTarget = null,
    onClose = null,
    toggleModalElements = null,
  }: Props = $props();

  let footerInstance: Record<string, unknown> | null = null;

  const mountFooter = () => {
    const target = getFooterTarget?.() ?? footerTarget;
    if (!target) {
      return;
    }
    if (footerInstance) {
      unmount(footerInstance);
      footerInstance = null;
    }
    footerInstance = mount(ZonePreferencesFooter, {
      target,
      props: { onClose },
    });
  };

  const refreshPreferences = () => {
    if (!userStore.connected) {
      return;
    }
    zoneInfos = userStore.connected.getZoneInfosFromPreferences();
    userHasAddresses = userStore.connected.identity.preferences.addresses.length > 0;
  };

  onMount(() => {
    if (!userStore.connected) {
      goto('/');
    } else {
      refreshPreferences();
    }

    mountFooter();

    return () => {
      if (footerInstance) {
        unmount(footerInstance);
        footerInstance = null;
      }
    };
  });

  const hideZones = async () => {
    zonesVisible = false;
    await toggleModalElements?.(false);
  };

  const showZones = async () => {
    zonesVisible = true;
    await toggleModalElements?.(true);
    mountFooter();
  };

  const cityInputHandler = (event: Event) => {
    if (!event.target) {
      return;
    }
    cityApiHasError = false;
    const { value } = event.target as HTMLInputElement;
    debounce(value);
  };

  const debounce = (value: string) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      inputValue = value;
      filterCities();
    }, 750);
  };

  const filterCities = async () => {
    filteredCities = [];
    if (inputValue) {
      try {
        const response = await callGeoAPI(inputValue);
        cityApiHasError = response.errorCode === 'geo-api-unavailable';
        if (cityApiHasError) {
          return;
        }
        if (!response.results) {
          return;
        }
        filteredCities = response.results;
      } catch (error) {
        console.error(error);
      }
    }
  };

  const setInputVal = async (city: ResponseFromGeoAPI) => {
    filteredCities = [];
    inputValue = '';
    try {
      const response = await cityToBAN(city);
      cityApiHasError = response.errorCode === 'ban-unavailable';
      if (cityApiHasError) {
        return;
      }
      if (!response.address) {
        return;
      }
      if (!userStore.connected) {
        return;
      }
      const preferences = userStore.connected.identity.preferences;
      preferences.addAddress(response.address);
      userStore.connected.setPreferences(preferences);
      refreshPreferences();
      showZones();
    } catch (error) {
      console.error(error);
    }
  };

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
  };

  const removeAddress = async (id: string) => {
    if (!userStore.connected) {
      return;
    }
    const preferences = userStore.connected.identity.preferences;
    const matchingAddresses = preferences.addresses.filter(
      (address) => address.idBAN.toString() === id
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
</script>

{#if !zonesVisible}
  <NavWithBackButton title="Commune" onClick={showZones} />
{/if}

<div class="preferences-city-search-container">
  {#if zonesVisible}
    <p transition:slide>
      Quelles zones scolaires et communes associées voulez-vous voir affichées dans
      votre agenda&nbsp;?
    </p>
  {/if}
  <form class="city-form">
    <fieldset class="fr-fieldset">
      <div class="fr-fieldset__element preferences-city-input-wrapper">
        <div class="fr-input-group autocomplete">
          <div class="fr-input-wrap fr-icon-search-line">
            <input
              class="fr-input"
              id="city-input"
              type="text"
              bind:value={inputValue}
              data-testid="city-input"
              oninput={cityInputHandler}
              onfocus={hideZones}
            >
          </div>
          {#if !zonesVisible}
            <div transition:slide>
              {#if !inputValue}
                <div class="city-input-empty">
                  <div class="no-agenda--icon">
                    <img
                      class="city-input-empty--icon"
                      src="/icons/city-search.svg"
                      alt="Icône de recherche"
                    >
                  </div>
                  <div class="city-input-empty--title">
                    Recherchez une commune pour afficher une zone
                  </div>
                </div>
              {/if}
              {#if filteredCities.length > 0}
                <ul id="autocomplete-items-list">
                  {#each filteredCities as city, index}
                    <li
                      class="autocomplete-item"
                      data-testid="autocomplete-item-{index}"
                    >
                      <button
                        type="button"
                        onclick={() => setInputVal(city)}
                        data-testid="autocomplete-item-button-{index}"
                      >
                        <p>{city.nom} ({city.departement.code})</p>
                      </button>
                    </li>
                  {/each}
                </ul>
              {/if}
              {#if cityApiHasError}
                <div class="fr-alert fr-alert--warning" data-testid="city-warning">
                  <h3 class="fr-alert__title">
                    Récupération de la commune indisponible
                  </h3>
                  <p>
                    Nous rencontrons des difficultés à trouver votre commune dans notre
                    répertoire. Merci de réessayer plus tard.
                  </p>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      </div>
      {#if zonesVisible && userHasAddresses}
        <div class="preferences-city-clear">
          <button
            type="button"
            class="fr-btn fr-btn--sm fr-btn--tertiary"
            onclick={clearAddresses}
            data-testid="clear-addresses"
          >
            Effacer tout
          </button>
        </div>
      {/if}
    </fieldset>
  </form>
</div>

{#if zonesVisible}
  <div class="preferences-content-container" transition:slide>
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
{/if}

<style>
  .preferences-city-search-container {
    p {
      margin-bottom: 0.5rem;
    }
    .city-input-empty {
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      text-align: center;
      font-size: 16px;
      line-height: 24px;
      color: var(--grey-0-1000);
      img {
        height: 5rem;
        width: 5rem;
      }
    }
    ul#autocomplete-items-list {
      position: relative;
      margin: 0;
      padding: 0;
      top: 0;
      border: 1px solid var(--grey-950-100);
      background-color: var(--grey-975-75);
      li.autocomplete-item {
        list-style: none;
        padding: 0;
        background-color: var(--background-default-grey);
        button {
          padding: 0.75rem;
          width: 100%;
          text-align: left;
          --hover-tint: var(--text-action-high-blue-france);
          --active-tint: var(--text-action-high-blue-france);
          p {
            margin: 0;
          }
        }
      }
      li.autocomplete-item:hover {
        background-color: var(--text-action-high-blue-france);
        color: var(--text-inverted-blue-france);
      }
    }
    .preferences-city-input-wrapper:has(+ .preferences-city-clear) {
      margin-bottom: 0.5rem;
    }
    .preferences-city-clear {
      display: flex;
      justify-content: flex-end;
      flex-direction: row;
      width: 100%;
      padding: 0 0.5rem;
    }
  }
</style>
