<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AMIGoto } from '$lib/ami-goto';
  import ServicesItemModal from '$lib/components/modal/ServicesItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import type { Followup } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import type { Services, ServicesItem } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let services: Services | null = $state(null);
  let selectedServicesItem: ServicesItem | null = $state(null);
  let followup: Followup | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
      return;
    }

    followup = await buildFollowup();
    services = await buildServices();
    console.log($state.snapshot(services));
  });

  const getServiceUrl = async (service: ServicesItem) => {
    return await service.getServiceUrl();
  };

  const gotoService = async (service: ServicesItem) => {
    const url = await service.getServiceUrl();
    AMIGoto(url, service.with_silent_login);
  };

  const clickOnService = (service: ServicesItem) => {
    const hasNonArchivedItems =
      followup?.hasNonArchivedItems(service.partner_id, service.item_type) || false;
    if (hasNonArchivedItems) {
      selectedServicesItem = service;
    } else {
      gotoService(service);
    }
  };

  // SOS

  const sosTags = [
    {
      isEnabled: true,
      url: '/#/',
      label: 'Dialoguer avec une policière ou un policier',
      iconClassName: 'fr-icon-question-answer-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/procedure-17cyber',
      label: 'Je suis victime de cybermalveillance',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'On m’a volé mon vélo',
    },
  ];

  const cfsiTabs = [
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je pars vivre à l’étranger',
      iconClassName: 'fr-icon-earth-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je crée une association',
      iconClassName: 'fr-icon-team-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je rentre en France après avoir vécu à l’étranger',
      iconClassName: 'fr-icon-flight-land-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je déménage en France',
      iconClassName: 'fr-icon-france-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je pars de chez mes parents',
      iconClassName: 'fr-icon-suitcase-2-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je deviens parent',
      iconClassName: 'fr-icon-parent-line fr-tag--icon-left',
    },
    {
      isEnabled: true,
      url: '/#/',
      label: 'Je suis muté à l’étranger',
      iconClassName: 'fr-icon-global-line fr-tag--icon-left',
    },
  ];
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
    >
      <h2 class="fr-h5 fr-mb-2w fr-pt-1w">SOS, j’ai un problème !</h2>
      {#if sosTags.length}
        {#each sosTags as sosTag}
          {#if sosTag.isEnabled}
            <button
              type="button"
              class="fr-tag fr-mb-2w fr-mr-1w {sosTag.iconClassName}"
              onclick={()=> goto(sosTag.url)}
            >
              {sosTag.label}
            </button>
          {/if}
        {/each}
      {/if}
      <p class="fr-mb-4w">
        <button
          type="button"
          class="fr-link fr-icon-arrow-right-line fr-link--icon-right am-link-bordered"
          onclick={()=> goto("/#/")}
        >
          J’ai besoin d’aide sur un autre sujet
        </button>
      </p>

      <h2 class="fr-h5 fr-mb-1w">Comment faire si ... ?</h2>

      <nav class="fr-sidemenu cfsi-sidemenu fr-mb-3w fr-mx-0">
        <div class="fr-sidemenu__inner">
          <ul class="fr-sidemenu__list">
            {#each cfsiTabs as cfsi}
              {#if cfsi.isEnabled}
                <li class="fr-sidemenu__item">
                  <button
                    class="fr-sidemenu__btn fr-pr-4w am-text--smbold {cfsi.iconClassName}"
                    type="button"
                    onclick={() => goto(cfsi.url)}
                  >
                    {cfsi.label}
                    <span
                      aria-hidden="true"
                      class="icon fr-icon-arrow-right-s-line am-color-blue    "
                    ></span>
                  </button>
                </li>
              {/if}
            {/each}
          </ul>
        </div>
      </nav>

      <h2 class="fr-h5">Je recherche un service public, une administration </h2>

      <button
        type="button"
        class="fr-btn fr-btn--secondary am-btn-target am-btn-w100"
        onclick={()=> window.location.href = "https://lannuaire.service-public.gouv.fr/"}
      >
        Accéder à l’annuaire
      </button>
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
                    {#each services.items as item}
                      <li class="fr-sidemenu__item">
                        <button
                          type="button"
                          class="fr-sidemenu__link"
                          onclick={() => clickOnService(item)}
                          data-testid="service-{item.id}"
                        >
                          <span class="services--item-details">
                            <span class="services--item-label">{item.title}</span>
                            <span class="services--item-description"
                              >{item.short_description}</span
                            >
                          </span>
                          <span
                            aria-hidden="true"
                            class="icon fr-icon-arrow-right-s-line"
                          ></span>
                        </button>
                      </li>
                    {/each}
                  {/if}
                </ul>
              </div>
            </div>
          </nav>
          <button
            type="button"
            class="fr-btn fr-btn--secondary am-btn-target am-btn-w100"
            onclick={()=> window.location.href = "https://www.service-public.gouv.fr/particuliers/recherche?rubricFilter=serviceEnLigne"}
          >
            Voir toutes les démarches
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

{#if selectedServicesItem}
  <ServicesItemModal bind:item={selectedServicesItem} />
{/if}

<style>
  .services {
    margin-bottom: 68px;
    .fr-sidemenu.services-sidemenu {
      box-shadow: none;
      margin: 0 0 2rem;
      .fr-sidemenu__item {
        button.fr-sidemenu__link {
          background: none;
          border: none;
          width: 100%;
          text-align: left;
          font: inherit;
          cursor: pointer;
          padding: 1.5rem 0;
          color: #000;
          --hover-tint: none;
          --active-tint: none;
          justify-content: space-between;
          span.services--item-details {
            display: flex;
            flex-direction: column;
            span.services--item-label {
              font-weight: 700;
              font-size: 16px;
            }
            span.services--item-description {
              font-weight: 400;
              font-size: 14px;
              line-height: 20px;
              color: var(--text-mention-grey);
            }
          }
          span.icon {
            color: var(--text-active-blue-france);
          }
        }
        &:last-child::before {
          box-shadow:
            0 -1px 0 0 var(--border-default-grey),
            inset 0 -1px 0 0 var(--border-default-grey);
        }
      }
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
