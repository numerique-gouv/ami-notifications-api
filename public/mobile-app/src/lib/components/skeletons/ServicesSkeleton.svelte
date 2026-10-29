<div class="skeleton">
  <div class="fr-tabs fr-tabs--viewport-width am-tabs">
    <ul
      class="fr-tabs__list"
      role="tablist"
      aria-label="Navigation par onglets des services"
    >
      <li role="presentation">
        <button
          type="button"
          id="skeleton-tab-6496"
          class="fr-tabs__tab fr-m-0 fr-text--sm fr-text--regular"
          tabindex="0"
          role="tab"
          aria-selected="true"
          aria-controls="skeleton-tab-6496-panel"
        >
          Trouver de l’aide
        </button>
      </li>
      <li role="presentation">
        <button
          type="button"
          id="skeleton-tab-6497"
          class="fr-tabs__tab fr-m-0 fr-text--sm fr-text--regular"
          tabindex="-1"
          role="tab"
          aria-selected="false"
          aria-controls="skeleton-tab-6497-panel"
        >
          Démarches et outils
        </button>
      </li>
    </ul>
    <div
      id="skeleton-tab-6496-panel"
      class="fr-tabs__panel fr-tabs__panel--selected"
      role="tabpanel"
      aria-labelledby="skeleton-tab-6496"
      tabindex="0"
    >
      {#each Array(10).keys() as i}
        <div class="service-line">
          <div class="line1"></div>
          <div class="line2"></div>
          <div class="line3"></div>
        </div>
      {/each}
    </div>
    <div
      id="skeleton-tab-6497-panel"
      class="fr-tabs__panel"
      role="tabpanel"
      aria-labelledby="skeleton-tab-6497"
      tabindex="0"
    ></div>
  </div>
</div>
<style>
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

  .skeleton {
    .fr-tabs__list {
      pointer-events: none;
    }
    .service-line {
      padding: 0.75rem 0 0 0;
      border-bottom: 1px solid #dddddd;
    }
    .line1 {
      background: #ececfe;
      width: 100%;
      height: 1rem;
      margin-bottom: 0.875rem;
    }
    .line2 {
      background: #ececfe;
      width: 65%;
      height: 1rem;
      margin-bottom: 0.875rem;
    }
    .line3 {
      background: #f5f5fe;
      width: 80%;
      height: 1rem;
      margin-bottom: 0.875rem;
    }
  }
</style>
