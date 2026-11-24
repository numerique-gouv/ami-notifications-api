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
  <NavWithBackButton
    className="small-header"
    title="Rechercher une commune"
    {backUrl}
  />

  <div class="preferences-city-search-container fr-pt-8w">
    <form class="city-form">
      <fieldset class="fr-fieldset">
        <div class="fr-fieldset__element preferences-city-input-wrapper">
          <div class="fr-input-group autocomplete">
            <label class="fr-label fr-sr-only fr-h3" for="city-input">
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
                  <img class="city-input-empty--icon" src="/icons/search.svg" alt="">
                </div>
                <div class="city-input-empty--title">
                  Recherchez une commune pour afficher une zone
                </div>
              </div>
            {/if}
            <div>
              <p aria-atomic="true" aria-live="polite" class="fr-sr-only">
                {#if filteredCities.length > 0}
                  {filteredCities.length} résultat(s) trouvés
                {/if}
              </p>
              {#if filteredCities.length > 0}
                <ul class="fr-raw-list" id="autocomplete-items-list">
                  {#each filteredCities as city, index}
                    <li
                      class="autocomplete-item"
                      data-testid="autocomplete-item-{index}"
                    >
                      <button
                        type="button"
                        class="fr-btn fr-btn--tertiary-no-outline fr-p-3v"
                        onclick={() => setInputVal(city)}
                        data-testid="autocomplete-item-button-{index}"
                      >
                        <p>{city.nom} ({city.departement.code})</p>
                      </button>
                    </li>
                  {/each}
                </ul>
              {/if}
            </div>
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
        li.autocomplete-item {
          border-bottom: 1px solid var(--grey-950-100);
          button {
            display: block;
            width: 100%;
            text-align: left;
            font-weight: 400;
            color: var(--text-default-grey);
            p {
              margin: 0;
            }
          }
        }
      }
    }
  }
</style>
