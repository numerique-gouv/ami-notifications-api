<script lang="ts">
  import { goto } from '$app/navigation';
  import { PUBLIC_FEATURE_FLAG_SERVICES_ENABLED } from '$env/static/public';
  import Icon from '$lib/components/Icon.svelte';
  import CenteredModal from '$lib/components/modal/CenteredModal.svelte';
  import { userStore } from '$lib/state/User.svelte';

  const { currentItem } = $props();
  const current = $derived({
    home: currentItem === 'home',
    agenda: currentItem === 'agenda',
    services: currentItem === 'services',
    followup: currentItem === 'followup',
    more: currentItem === 'more',
  });
  const services_enabled = PUBLIC_FEATURE_FLAG_SERVICES_ENABLED === 'true';

  const menuItems = $derived([
    {
      url: '/',
      label: 'Accueil',
      iconClass: current.home ? 'fr-icon-home-4-fill' : 'fr-icon-home-4-line',
      isSelected: current.home,
      isEnabled: true,
    },
    {
      url: '/#/agenda',
      label: 'Agenda',
      iconClass: current.agenda
        ? 'fr-icon-calendar-event-fill'
        : 'fr-icon-calendar-event-line',
      isSelected: current.agenda,
      isEnabled: true,
    },
    {
      url: '/#/services',
      label: 'Services',
      iconClass: current.services
        ? 'fr-icon-layout-grid-fill'
        : 'fr-icon-layout-grid-line',
      isSelected: current.services,
      isEnabled: services_enabled,
    },
    {
      url: '/#/followup',
      label: 'Suivi',
      iconClass: current.followup
        ? 'fr-icon-search-eye-fill'
        : 'fr-icon-search-eye-line',
      isSelected: current.followup,
      isEnabled: true,
    },
    {
      url: '',
      label: 'Plus',
      iconClass: current.more ? 'fr-icon-more-fill' : 'fr-icon-more-line',
      isSelected: current.more,
      isEnabled: true,
    },
  ]);

  // Menu Plus

  const menuPlus = [
    {
      isEnabled: true,
      url: '/#/profile',
      label: 'Mon profil',
      iconClassName: 'fr-icon-user-line',
      id: 'profile',
    },
    {
      isEnabled: true,
      url: '/#/preferences',
      label: 'Préférences',
      iconClassName: 'fr-icon-settings-3-line',
      id: 'preferences',
    },
    {
      isEnabled: true,
      url: '/#/contact',
      label: 'Contact',
      iconClassName: 'fr-icon-question-answer-line',
      id: 'contact',
    },
  ];

  let logoutModal = $state(false);

  const openLogoutModal = () => {
    logoutModal = true;
  };

  const closeLogoutModal = () => {
    logoutModal = false;
  };

  const logoutUser = async () => {
    await userStore.logout();
  };
</script>

<nav id="menu-footer" class="menu-footer" aria-label="Menu principal">
  <ul class="menu__list fr-raw-list">
    {#each menuItems as menuItem}
      {#if menuItem.isEnabled}
        <li class="menu__item">
          {#if menuItem.label === "Plus"}
            <button
              type="button"
              data-fr-opened="false"
              aria-controls="modal-main-nav-plus-6655"
              id="button-modal-main-nav-plus-6655"
              data-testid="button-modal-main-nav-plus-6655"
              class="menu__link {menuItem.isSelected ? 'highlight fr-text--bold' : ''}"
            >
              <span
                aria-hidden="true"
                class="fr-icon { menuItem.iconClass } fr-mb-1w"
              ></span>
              <span class="menu__label fr-text--xs fr-mb-0">{menuItem.label}</span>
            </button>
          {:else}
            <button
              type="button"
              onclick={()=>goto(menuItem.url)}
              class="menu__link {menuItem.isSelected ? 'highlight fr-text--bold' : ''}"
              aria-current={menuItem.isSelected ? 'page' : null}
            >
              <span
                aria-hidden="true"
                class="fr-icon { menuItem.iconClass } fr-mb-1w"
              ></span>
              <span class="menu__label fr-text--xs fr-mb-0">{menuItem.label}</span>
            </button>
          {/if}
        </li>
      {/if}
    {/each}
  </ul>
</nav>

<dialog
  id="modal-main-nav-plus-6655"
  class="fr-modal am-modal-nav-plus"
  aria-labelledby="modal-main-nav-plus-6655-title"
>
  <div class="fr-container fr-container--fluid fr-container-md">
    <div class="fr-modal__body">
      <div class="fr-modal__header fr-py-1v">
        <button
          type="button"
          aria-label="Fermer"
          aria-controls="modal-main-nav-plus-6655"
          id="button-6045"
          class="fr-btn--close fr-btn fr-icon-close-line fr-btn--tertiary-no-outline"
        ></button>
      </div>
      <div class="fr-modal__content">
        <h2 id="modal-main-nav-plus-6655-title" class="fr-modal__title fr-sr-only">
          La suite de la navigation
        </h2>

        <nav class="fr-sidemenu">
          <div class="fr-sidemenu__inner">
            <ul class="fr-sidemenu__list">
              {#each menuPlus as menuPlusItem}
                {#if menuPlusItem.isEnabled}
                  <li class="fr-sidemenu__item">
                    <button
                      type="button"
                      class="fr-sidemenu__btn fr-text--regular"
                      onclick={() => goto(menuPlusItem.url)}
                      data-testid="{menuPlusItem.id}-button"
                    >
                      <Icon
                        className="{menuPlusItem.iconClassName} am-color-blue am-icon-20 fr-mr-1w"
                      />
                      {menuPlusItem.label}
                    </button>
                  </li>
                {/if}
              {/each}
              <li class="fr-sidemenu__item">
                <button
                  type="button"
                  class="fr-sidemenu__btn fr-text--regular fr-connect-logout"
                  onclick={openLogoutModal}
                  data-testid="logout-button"
                >
                  <Icon
                    className="fr-icon-shut-down-line am-color-blue am-icon-20 fr-mr-1w"
                  />
                  Me déconnecter
                </button>
              </li>
            </ul>
          </div>
        </nav>
      </div>
    </div>
  </div>
</dialog>

{#if logoutModal}
  <CenteredModal onClose={closeLogoutModal}>
    {#snippet header()}
      <h2 class="fr-h4">Suppression de vos données</h2>
      <p>
        En vous déconnectant, toutes les données enregistrées localement sur cet
        appareil (informations saisies, modifications et paramètres de personnalisation)
        seront supprimées.
      </p>
    {/snippet}
    {#snippet footer()}
      <ul class="fr-btns-group logout-modal-action-buttons">
        <li>
          <button
            type="button"
            class="fr-btn fr-btn--secondary cancel-button"
            onclick={closeLogoutModal}
            data-testid="logout-cancel-button"
          >
            Annuler
          </button>
        </li>
        <li>
          <button
            type="button"
            class="fr-btn submit-button"
            onclick={logoutUser}
            data-testid="logout-submit-button"
          >
            Confirmer
          </button>
        </li>
      </ul>
    {/snippet}
  </CenteredModal>
{/if}

<style>
  nav.menu-footer {
    position: fixed;
    z-index: 300;
    bottom: 0;
    background: var(--background-default-grey);
    border-top: solid 1px var(--background-alt-grey-active);
    width: 100%;
    .menu__list {
      display: flex;
    }
    .menu__item {
      padding-bottom: 0;
      width: 100%;
      .menu__link {
        position: relative;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        background: none;
        padding: 0.75rem 0 0.375rem;
        height: 4.25rem;
        width: 100%;
        outline-offset: -2px;
        .fr-icon {
          height: 1.5rem;
          width: 1.5rem;
          color: var(--text-action-high-blue-france);
        }
        .menu__label {
          display: block;
          width: 100%;
          text-align: center;
        }
        &.highlight {
          &:before {
            z-index: -1;
            content: "";
            position: absolute;
            top: 0.5rem;
            background: var(--background-contrast-blue-france);
            border-radius: 1rem;
            width: 3.5rem;
            height: 2rem;
          }
        }
      }
    }
  }

  .am-modal-nav-plus {
    .fr-btn--close {
      min-width: 2.5rem;
      min-height: 2.5rem;
      &:after {
        --icon-size: 1.5rem;
        margin-left: 0;
      }
    }

    > .fr-container {
      border-radius: 1.75rem 1.75rem 0 0;
    }

    .fr-sidemenu__item:before {
      display: none;
    }

    .fr-sidemenu {
      box-shadow: none;
    }
  }

  .logout-modal-action-buttons {
    background-color: var(--background-default-grey);
    display: flex;
    gap: 1rem;
    margin: 0;
    li {
      flex: 1;
      button {
        display: block;
        width: 100%;
        margin: 0;
      }
    }
  }
</style>
