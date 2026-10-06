<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIBack, AMIGoto } from '$lib/ami-navigation';
  import {
    callGeoAPI,
    cityToBAN,
    type ResponseFromGeoAPI,
  } from '$lib/citiesFromGeoAPIAndBAN';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/preferences/zones';
  let timer: ReturnType<typeof setTimeout>;
  let inputValue: string = $state('');
  let filteredCities: ResponseFromGeoAPI[] = $state([]);
  let cityApiHasError: boolean = $state(false);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
  });

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
      AMIBack(backUrl);
    } catch (error) {
      console.error(error);
    }
  };
</script>

<div class="preferences-city-page fr-px-2w">
  <NavWithBackButton title="" {backUrl} />

  <div class="preferences-city-search-container fr-pt-8w">
    <h1 class="fr-h3 fr-sr-only">Rechercher une commune</h1>
    <form class="city-form">
      <fieldset class="fr-fieldset">
        <div class="fr-fieldset__element preferences-city-input-wrapper">
          <div class="fr-input-group autocomplete">
            <label class="fr-label fr-h3" for="city-input">
              Commune
              <span class="fr-hint-text fr-sr-only"
                >Recherchez une commune pour afficher une zone</span
              >
            </label>
            <div class="fr-input-wrap fr-icon-search-line">
              <input
                class="fr-input"
                id="city-input"
                type="text"
                bind:value={inputValue}
                data-testid="city-input"
                oninput={cityInputHandler}
              >
            </div>
            {#if !inputValue}
              <div class="city-input-empty">
                <div class="no-agenda--icon">
                  <img
                    class="city-input-empty--icon"
                    src="/icons/city-search.svg"
                    alt=""
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
                  <li class="autocomplete-item" data-testid="autocomplete-item-{index}">
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
                <h3 class="fr-alert__title">Récupération de la commune indisponible</h3>
                <p>
                  Nous rencontrons des difficultés à trouver votre commune dans notre
                  répertoire. Merci de réessayer plus tard.
                </p>
              </div>
            {/if}
          </div>
        </div>
      </fieldset>
    </form>
  </div>
</div>

<style>
  .preferences-city-page {
    .preferences-city-search-container {
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
    }
  }
</style>
