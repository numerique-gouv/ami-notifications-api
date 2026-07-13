<script lang="ts">
  const { currentItem } = $props();
  const current = $derived({
    home: currentItem === 'home',
    agenda: currentItem === 'agenda',
    followup: currentItem === 'followup',
  });

  const menuItems = $derived([
    {
      url: '/',
      label: 'Accueil',
      iconClass: current.home ? 'fr-icon-home-4-fill' : 'fr-icon-home-4-line',
      isSelected: current.home,
    },
    {
      url: '/#/agenda',
      label: 'Agenda',
      iconClass: current.agenda
        ? 'fr-icon-calendar-event-fill'
        : 'fr-icon-calendar-event-line',
      isSelected: current.agenda,
    },
    {
      url: '/#/followup',
      label: 'Suivi',
      iconClass: current.followup ? 'fr-icon-vector-fill' : 'fr-icon-vector-line',
      isSelected: current.followup,
    },
  ]);
</script>

<nav id="menu-footer" class="menu-footer" aria-label="Menu principal">
  <ul class="menu__list fr-raw-list">
    {#each menuItems as menuItem}
      <li class="menu__item">
        <a
          href={menuItem.url}
          class="menu__link {menuItem.isSelected ? 'highlight fr-text--bold' : ''}"
          aria-current={menuItem.isSelected ? 'page' : null}
        >
          <span
            aria-hidden="true"
            class="fr-icon { menuItem.iconClass } fr-mb-1w"
          ></span>
          <span class="menu__label fr-text--xs fr-mb-0">{menuItem.label}</span>
        </a>
      </li>
    {/each}
  </ul>
</nav>

<style>
  nav.menu-footer {
    position: fixed;
    z-index: 2;
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
</style>
