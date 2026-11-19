<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import ServicesItemModal from '$lib/components/modal/ServicesItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import ServicesItem from '$lib/components/ServicesItem.svelte';
  import ServicesSearchSkeleton from '$lib/components/skeletons/ServicesSearchSkeleton.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import type {
    ServicesItem as Item,
    Services,
    ServicesItemSearchResult,
  } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { skeletonDebugDelay } from '$lib/skeleton';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/services');

  let services: Services | null = $state(null);
  let followup: Followup | null = $state(null);

  let timer: ReturnType<typeof setTimeout>;
  let inputValue: string = $state('');
  let searchResult: ServicesItemSearchResult | null = $state(null);

  const waitForPageData = async () => {
    await skeletonDebugDelay();
    [followup, services] = await Promise.all([buildFollowup(), buildServices()]);
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }

    document.getElementById('search-input')?.focus();
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
  <NavWithBackButton
    className="not-sticky small-header"
    title="Rechercher un service"
    {backUrl}
  />

  <div class="services-search-container">
    {#await waitForPageData()}
      <ServicesSearchSkeleton />
    {:then pageDataLoaded}
      <form class="search-form">
        <div class="fr-fieldset__element fr-p-0">
          <div class="fr-input-group autocomplete">
            <label class="fr-label fr-sr-only" for="search-input">
              Saisissez un mot-clé pour rechercher une démarche, un service ou une
              situation de vie.
            </label>
            <div class="fr-input-wrap fr-icon-search-line fr-mt-0 fr-mb-1w">
              <input
                class="fr-input"
                id="search-input"
                type="text"
                autocomplete="off"
                bind:value={inputValue}
                data-testid="search-input"
                oninput={searchInputHandler}
              >
            </div>
            <div>
              <p aria-atomic="true" aria-live="polite" class="fr-sr-only">
                {searchResult === null ? '0': searchResult.services.length} résultat(s)
                trouvés
              </p>

              {#if searchResult === null}
                <div class="search-input-empty fr-py-2w">
                  <div class="no-services--icon">
                    <img
                      class="search-input-empty--icon"
                      src="/icons/search.svg"
                      alt=""
                    >
                  </div>
                  <p class="search-input-empty--title">
                    Recherchez une démarche, un service, une situation de vie par
                    mots-clés
                  </p>
                </div>
              {:else}
                {#if searchResult.services.length > 0}
                  <nav class="fr-sidemenu cfsi-sidemenu fr-mb-3w fr-mx-0">
                    <div class="fr-sidemenu__inner">
                      <ul class="fr-sidemenu__list" data-testid="search-result">
                        {#each searchResult.services as service, index}
                          {#if service.kind == 'catalog'}
                            <ServicesItem
                              item={service}
                              hasNonArchivedItems={followup?.hasNonArchivedItems(service.partner_id, service.item_type) || false}
                              goToService={(service) => goToService(service)}
                              index="services-items-{index}"
                            />
                          {:else}
                            <li class="fr-sidemenu__item">
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
                            </li>
                          {/if}
                        {/each}
                      </ul>
                    </div>
                  </nav>

                  {#each searchResult.services as service, index}
                    {#if service.kind == 'catalog'}
                      <ServicesItemModal
                        item={service}
                        index="services-items-{index}"
                      />
                    {/if}
                  {/each}
                {:else}
                  <div class="search-input-no-result fr-py-2w" data-testid="no-result">
                    <div class="no-result--icon">
                      <img
                        class="search-input-no-result--icon"
                        src="/icons/search-error.svg"
                        alt=""
                      >
                    </div>
                    <p class="search-input-no-result--title">
                      Aucun résultat pour « {searchResult.terms} »
                    </p>
                  </div>
                {/if}
              {/if}
            </div>
          </div>
        </div>
      </form>
    {/await}
  </div>
</div>

<style>
  .services-search-page {
    .services-search-container {
      .search-input-empty,
      .search-input-no-result {
        text-align: center;
        img {
          height: 5rem;
          width: 5rem;
        }
      }
    }

    .search-form {
      .fr-input {
        min-height: 3rem;
        box-shadow: inset 0 -3px 0 0 var(--border-action-high-blue-france);
      }
    }

    .fr-sidemenu {
      box-shadow:
        inset 0 -1px 0 0 var(--border-default-grey),
        inset 0 0 0 0 var(--border-default-grey);
      .fr-sidemenu__btn {
        min-height: 4.5rem;

        &:before {
          margin-right: 0.5rem;
        }
      }

      .icon {
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);
      }
    }
  }
</style>
