<script lang="ts">
  import { PUBLIC_FEATURE_FLAG_SERVICES_ENABLED } from '$env/static/public';
  import AMILink from '$lib/components/AMILink.svelte';

  const { currentItem } = $props();
  const current = $derived({
    home: currentItem === 'home',
    agenda: currentItem === 'agenda',
    services: currentItem === 'services',
    followup: currentItem === 'followup',
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
      iconClass: current.followup ? 'fr-icon-vector-fill' : 'fr-icon-vector-line',
      isSelected: current.followup,
      isEnabled: true,
    },
  ]);
</script>

<nav id="menu-footer" class="menu-footer" aria-label="Menu principal">
  <ul class="menu__list fr-raw-list">
    {#each menuItems as menuItem}
      {#if menuItem.isEnabled}
        <li class="menu__item">
          <AMILink
            url={menuItem.url}
            variant={menuItem.isSelected ? 'menu-item-highlight': 'menu-item'}
            class="menu__link {menuItem.isSelected ? 'fr-text--bold' : ''}"
            aria-current={menuItem.isSelected ? 'page' : null}
          >
            <span
              aria-hidden="true"
              class="fr-icon { menuItem.iconClass } fr-mb-1w"
            ></span>
            <span class="menu__label fr-text--xs fr-mb-0">{menuItem.label}</span>
          </AMILink>
        </li>
      {/if}
    {/each}
  </ul>
</nav>

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
    }
  }
</style>
