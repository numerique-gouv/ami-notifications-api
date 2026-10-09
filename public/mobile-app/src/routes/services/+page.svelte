<script lang="ts">
  import { onMount } from 'svelte';
  import {
    PUBLIC_SP_ANNUAIRE_URL,
    PUBLIC_SP_ORIENTEUR_URL,
    PUBLIC_SP_SEARCH_URL,
  } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import ServicesItemModal from '$lib/components/modal/ServicesItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import ServicesItem from '$lib/components/ServicesItem.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import type { ServicesItem as Item, Services } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let services: Services | null = $state(null);
  let followup: Followup | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }

    followup = await buildFollowup();
    services = await buildServices();
    console.log($state.snapshot(services));
  });

  const goToService = async (service: Item) => {
    const url = await service.getServiceUrl();
    AMIGoto(url, service.with_silent_login);
  };
</script>

<Navigation currentItem="services" />

<div class="services">
  <div class="fr-pt-3w fr-px-2w services--title">
    <h2>Services</h2>
  </div>

  <div class="fr-tabs fr-tabs--viewport-width am-tabs">
    <ul
      class="fr-tabs__list"
      role="tablist"
      aria-label="Navigation par onglets des services"
    >
      <li role="presentation">
        <button
          type="button"
          id="tab-6496"
          class="fr-tabs__tab fr-m-0 fr-text--sm fr-text--regular"
          tabindex="0"
          role="tab"
          aria-selected="true"
          aria-controls="tab-6496-panel"
        >
          Trouver de l’aide
        </button>
      </li>
      <li role="presentation">
        <button
          type="button"
          id="tab-6497"
          class="fr-tabs__tab fr-m-0 fr-text--sm fr-text--regular"
          tabindex="-1"
          role="tab"
          aria-selected="false"
          aria-controls="tab-6497-panel"
        >
          Démarches et outils
        </button>
      </li>
    </ul>
    <div
      id="tab-6496-panel"
      class="fr-tabs__panel fr-tabs__panel--selected"
      role="tabpanel"
      aria-labelledby="tab-6496"
      tabindex="0"
      data-testid="sos"
    >
      <h2 class="fr-h5 fr-mb-2w fr-pt-1w">SOS, j’ai un problème !</h2>
      {#if services && services.sos.length}
        {#each services.sos as sos}
          <button
            type="button"
            class="fr-tag fr-mb-2w fr-mr-1w {sos.icon} {sos.icon ? 'fr-tag--icon-left': ''}"
            data-testid="service-sos-{sos.id}"
            onclick={()=> goToService(sos)}
          >
            {sos.title}
          </button>
        {/each}
      {/if}
      {#if PUBLIC_SP_ORIENTEUR_URL}
        <p class="fr-mb-4w">
          <button
            type="button"
            class="fr-link fr-icon-arrow-right-line fr-link--icon-right am-link-bordered"
            onclick={()=> AMIGoto(PUBLIC_SP_ORIENTEUR_URL)}
          >
            J’ai besoin d’aide sur un autre sujet
          </button>
        </p>
      {/if}

      <h2 class="fr-h5 fr-mb-1w">Comment faire si ... ?</h2>

      <!--
      {#if services && services.steps.length }
        <SideMenu sideMenus={services.steps} />
      {/if}
      -->

      <nav class="fr-sidemenu cfsi-sidemenu fr-mb-3w fr-mx-0">
        <div class="fr-sidemenu__inner">
          <ul class="fr-sidemenu__list" data-testid="steps">
            {#if services && services.steps.length}
              {#each services.steps as steps}
                <li class="fr-sidemenu__item">
                  <button
                    class="fr-sidemenu__btn fr-pl-0 fr-pr-4w am-text--smbold  {steps.icon} {steps.icon ? 'fr-tag--icon-left': ''}"
                    type="button"
                    data-testid="service-steps-{steps.id}"
                    onclick={() => goToService(steps)}
                  >
                    {steps.title}
                    <span
                      aria-hidden="true"
                      class="icon fr-icon-arrow-right-s-line am-color-blue    "
                    ></span>
                  </button>
                </li>
              {/each}
            {/if}
          </ul>
        </div>
      </nav>

      {#if PUBLIC_SP_ANNUAIRE_URL}
        <h2 class="fr-h5">Je recherche un service public, une administration </h2>

        <button
          type="button"
          class="fr-btn fr-btn--secondary am-btn-w100"
          onclick={() => AMIGoto(PUBLIC_SP_ANNUAIRE_URL)}
        >
          Accéder à l’annuaire
        </button>
      {/if}
    </div>
    <div
      id="tab-6497-panel"
      class="fr-tabs__panel"
      role="tabpanel"
      aria-labelledby="tab-6497"
      tabindex="0"
    >
      <div class="services--container" data-testid="services">
        <div class="preferences-content-container">
          <nav
            class="fr-sidemenu services-sidemenu"
            aria-labelledby="fr-sidemenu-title"
          >
            <div class="fr-sidemenu__inner">
              <div id="fr-sidemenu-wrapper">
                <ul class="fr-sidemenu__list">
                  {#if services && services.items.length}
                    {#each services.items as item, i}
                      <ServicesItem
                        item={item}
                        hasNonArchivedItems={followup?.hasNonArchivedItems(item.partner_id, item.item_type) || false}
                        goToService={(item) => goToService(item)}
                      />
                      <ServicesItemModal bind:item={services.items[i]} />
                    {/each}
                  {/if}
                </ul>
              </div>
            </div>
          </nav>
          {#if PUBLIC_SP_SEARCH_URL}
            <button
              type="button"
              class="fr-btn fr-btn--secondary am-btn-w100"
              onclick={()=> AMIGoto(PUBLIC_SP_SEARCH_URL)}
            >
              Voir toutes les démarches
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .services {
    margin-bottom: 68px;
    .fr-sidemenu.services-sidemenu {
      box-shadow: none;
      margin: 0 0 2rem;
    }

    .am-tabs {
      &.fr-tabs {
        box-shadow: none;
        &:before {
          box-shadow: none;
        }

        li {
          width: 100%;
        }
        .fr-tabs__tab {
          width: 100%;
          padding: 1rem 0.5rem;
          justify-content: center;

          &[aria-selected="true"]:not(:disabled) {
            background-image: linear-gradient(
              0deg,
              var(--border-active-blue-france),
              var(--border-active-blue-france)
            );
            background-position: 0 100%;
            background-repeat: no-repeat, no-repeat;
            transition: background-size 0s;
            background-size:
              100% 2px,
              0 0,
              0 0,
              0 0;
          }

          &:not([aria-selected="true"]) {
            background: var(--background-default-grey);
          }
        }
      }
      .fr-tabs__panel {
        transition: none;
      }
    }

    .cfsi-sidemenu {
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
