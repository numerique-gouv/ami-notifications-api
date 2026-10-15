<script lang="ts">
  import { PUBLIC_FEATURE_FLAG_SERVICES_ENABLED } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import Icon from '$lib/components/Icon.svelte';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
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
      url: '/#/help-center',
      label: 'Aide et contact',
      iconClassName: 'fr-icon-customer-service-line',
      id: 'help-center',
    },
    {
      isEnabled: true,
      url: '/#/page/donnees-personnelles',
      label: 'Données personnelles et sécurité',
      iconClassName: 'fr-icon-lock-line',
      id: 'privacy',
    },
    {
      isEnabled: true,
      url: '/#/page/accessibilite',
      label: 'Accessibilité',
      iconClassName: 'fr-icon-accessibility-line',
      id: 'a11y',
    },
  ];

  const logoutUser = async () => {
    await userStore.logout(true);
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
              onclick={()=>AMIGoto(menuItem.url)}
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

<BottomModal modalId="modal-main-nav-plus-6655">
  {#snippet modalContent()}
    <h2 id="modal-main-nav-plus-6655-title" class="fr-modal__title fr-sr-only">
      La suite de la navigation
    </h2>
    <nav class="fr-sidemenu am-nav-plus">
      <div class="fr-sidemenu__inner">
        <ul class="fr-sidemenu__list">
          {#each menuPlus as menuPlusItem}
            {#if menuPlusItem.isEnabled}
              <li class="fr-sidemenu__item">
                <button
                  type="button"
                  class="fr-sidemenu__btn fr-text--regular"
                  onclick={() => AMIGoto(menuPlusItem.url)}
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
              data-fr-opened="false"
              aria-controls="logout-modal"
              id="logout-button"
              type="button"
              class="fr-sidemenu__btn fr-text--regular fr-connect-logout"
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
  {/snippet}
</BottomModal>

<CenteredModal modalId="logout-modal">
  {#snippet modalContent()}
    <h2 id="logout-modal-title" class="fr-h4">Suppression de vos données</h2>
    <p>
      En vous déconnectant, toutes les données enregistrées localement sur cet appareil
      (informations saisies, modifications et paramètres de personnalisation) seront
      supprimées.
    </p>
    <ul class="fr-btns-group fr-pb-3v logout-modal-action-buttons">
      <li>
        <button
          aria-controls="logout-modal"
          type="button"
          class="fr-btn fr-btn--secondary cancel-button"
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
  .fr-sidemenu.am-nav-plus {
    box-shadow: none;
    .fr-sidemenu__item:before {
      display: none;
    }
  }
  .logout-modal-action-buttons {
    gap: 1rem;
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
