<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import ServicesItemModal from '$lib/components/modal/ServicesItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import ServicesItem from '$lib/components/ServicesItem.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import type {
    ServicesItem as Item,
    Services,
    ServicesItemSearchResult,
  } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/services');

  let services: Services | null = $state(null);
  let followup: Followup | null = $state(null);

  let timer: ReturnType<typeof setTimeout>;
  let inputValue: string = $state('');
  let searchResult: ServicesItemSearchResult | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }

    followup = await buildFollowup();
    services = await buildServices();
  });

  const searchInputHandler = (event: Event) => {
    if (!event.target) {
      return;
    }
    const { value } = event.target as HTMLInputElement;
    debounce(value);
  };

  const debounce = (value: string) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      inputValue = value;
      filterServices();
    }, 750);
  };

  const filterServices = async () => {
    if (inputValue && services) {
      searchResult = services.search(inputValue);
    } else {
      searchResult = null;
    }
  };

  const goToService = async (service: Item) => {
    const url = await service.getServiceUrl();
    AMIGoto(url, service.with_silent_login);
  };
</script>

<div class="services-search-page fr-px-2w">
  <NavWithBackButton title="" {backUrl} />

  <div class="services-search-container fr-pt-8w">
    <h1 class="fr-h3">Rechercher un service</h1>
    <form class="search-form">
      <div class="fr-fieldset__element">
        <div class="fr-input-group autocomplete">
          <div class="fr-input-wrap fr-icon-search-line">
            <input
              class="fr-input"
              id="search-input"
              type="text"
              bind:value={inputValue}
              data-testid="search-input"
              oninput={searchInputHandler}
            >
          </div>
          {#if searchResult === null}
            <div class="search-input-empty">
              <div class="no-services--icon">
                <img class="search-input-empty--icon" src="/icons/search.svg" alt="">
              </div>
              <div class="search-input-empty--title">
                Recherchez une démarche, un service, une situation de vie par mots-clés
              </div>
            </div>
          {:else}
            {#if searchResult.services.length > 0}
              <nav class="fr-sidemenu cfsi-sidemenu fr-mb-3w fr-mx-0">
                <div class="fr-sidemenu__inner">
                  <ul class="fr-sidemenu__list" data-testid="search-result">
                    {#each searchResult.services as service, index}
                      <li class="fr-sidemenu__item">
                        {#if service.kind == 'catalog'}
                          <ServicesItem
                            item={service}
                            hasNonArchivedItems={followup?.hasNonArchivedItems(service.partner_id, service.item_type) || false}
                            goToService={(service) => goToService(service)}
                            index="services-items-{index}"
                          />
                          <ServicesItemModal
                            item={service}
                            index="services-items-{index}"
                          />
                        {:else}
                          <button
                            class="fr-sidemenu__btn fr-pl-0 fr-pr-4w am-text--smbold  {service.icon} {service.icon ? 'fr-tag--icon-left': ''}"
                            type="button"
                            data-testid="service-{service.id}"
                            onclick={() => goToService(service)}
                          >
                            {service.title}
                            <span
                              aria-hidden="true"
                              class="icon fr-icon-arrow-right-s-line am-color-blue"
                            ></span>
                          </button>
                        {/if}
                      </li>
                    {/each}
                  </ul>
                </div>
              </nav>
            {:else}
              <div class="search-input-no-result" data-testid="no-result">
                <div class="no-result--icon">
                  <img
                    class="search-input-no-result--icon"
                    src="/icons/search-error.svg"
                    alt=""
                  >
                </div>
                <div class="search-input-no-result--title">
                  Aucun résultat pour « {searchResult.terms} »
                </div>
              </div>
            {/if}
          {/if}
        </div>
      </div>
    </form>
  </div>
</div>

<style>
  .services-search-page {
    .services-search-container {
      .search-input-empty,
      .search-input-no-result {
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
    }
  }
</style>
