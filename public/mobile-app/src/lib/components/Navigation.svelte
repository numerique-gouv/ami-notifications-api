<script lang="ts">
  import { PUBLIC_FEATUREFLAG_REQUESTS_ENABLED } from '$env/static/public'

  const { currentItem } = $props()
  const current = $derived({
    home: currentItem === 'home',
    agenda: currentItem === 'agenda',
    requests: currentItem === 'requests',
  })
  const requests_enabled = PUBLIC_FEATUREFLAG_REQUESTS_ENABLED === 'true'
</script>

<nav class="menu-footer" aria-label="Menu principal">
  <ul class="menu-list">
    <li class="menu__item">
      <a
        class="menu__link {current.home ? 'highlight': ''}"
        href="/"
        aria-current="{current.home ? 'true': null}"
      >
        <img src="/remixicons/home-4-fill.svg" alt="Icône d'accueil">
        <span>Accueil</span>
      </a>
    </li>
    <li class="menu__item">
      <a
        class="menu__link {current.agenda ? 'highlight': ''}"
        href="/#/agenda"
        aria-current="{current.agenda ? 'true': null}"
      >
        <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier">
        <span>Agenda</span>
      </a>
    </li>
    {#if requests_enabled}
      <li class="menu__item">
        <a
          class="menu__link {current.requests ? 'highlight': ''}"
          href="/#/requests"
          aria-current="{current.requests ? 'true': null}"
        >
          <img src="/remixicons/vector.svg" alt="Icône de suivi">
          <span>Suivi</span>
        </a>
      </li>
    {/if}
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

    .menu-list {
      display: flex;
      list-style-type: none;
      padding-inline-start: 0;
      margin-block-start: 0;
      margin-block-end: 0;
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

        img {
          margin-bottom: 0.5rem;
          height: 1.5rem;
          width: 1.5rem;
        }

        span {
          display: block;
          width: 100%;
          color: var(--grey-200-850);
          text-align: center;
          font-size: 0.75rem;
          font-weight: 400;
          line-height: 1.25rem;
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
