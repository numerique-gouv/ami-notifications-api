<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }
  });
</script>

<div class="requests">
  <div class="requests--title">
    <h2>Mes démarches</h2>
    <div class="requests--title--icon">
      <span class="fr-icon-search-line" aria-hidden="true"></span>
    </div>
  </div>

  <div class="fr-tabs requests--container">
    <ul
      class="fr-tabs__list requests--container--tabs"
      role="tablist"
      aria-label="Suivi des démarches"
    >
      <li role="presentation">
        <button
          type="button"
          id="requests-tab-current"
          class="fr-tabs__tab"
          tabindex="0"
          role="tab"
          aria-selected="true"
          aria-controls="requests-tab-current-panel"
        >
          En cours
        </button>
      </li>
      <li role="presentation">
        <button
          type="button"
          id="requests-tab-past"
          class="fr-tabs__tab"
          tabindex="-1"
          role="tab"
          aria-selected="false"
          aria-controls="requests-tab-past-panel"
        >
          Passées
        </button>
      </li>
    </ul>

    <div
      id="requests-tab-current-panel"
      class="fr-tabs__panel fr-tabs__panel--selected requests--container--panel"
      role="tabpanel"
      aria-labelledby="requests-tab-current"
      tabindex="0"
    >
      <div class="requests--container--panel--content">
        <div class="no-requests">
          <div class="no-requests--icon">
            <img
              class="requests-icon"
              src="/remixicons/tracking.svg"
              alt="Icône de suivi"
            >
          </div>
          <div class="no-requests--title">
            Après avoir effectué vos démarches, vous pouvez les suivre en temps réel
            depuis l’application.
          </div>
        </div>
      </div>
    </div>
    <div
      id="requests-tab-past-panel"
      class="fr-tabs__panel requests--container--panel"
      role="tabpanel"
      aria-labelledby="requests-tab-past"
      tabindex="0"
    >
      <div class="requests--container--panel--content">
        <div class="no-requests">
          <div class="no-requests--icon">
            <img
              class="requests-icon"
              src="/remixicons/tracking.svg"
              alt="Icône de suivi"
            >
          </div>
          <div class="no-requests--title">
            Après avoir effectué vos démarches, vous pouvez les suivre en temps réel
            depuis l’application.
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<Navigation currentItem="requests" />

<style>
  .requests {
    padding: 1.5rem 1rem;
    margin-bottom: 68px;
    .requests--title {
      display: flex;
      h2 {
        flex-grow: 1;
        margin-bottom: 0.5rem;
      }
      .requests--title--icon {
        padding-top: 0.25rem;
        color: var(--text-active-blue-france);
      }
    }
    .requests--container {
      box-shadow: none;
      &::before {
        box-shadow: none;
      }
      .requests--container--tabs {
        padding: 0;
        li {
          flex: 1;
          text-align: center;
          line-height: 3.5rem;
          button {
            width: 100%;
            margin: 0;
            display: flex;
            justify-content: center;
            background: none;
            font-weight: 400;
            font-size: 14px;
            line-height: 1.5rem;
            border-bottom: solid 2px transparent;
            &[aria-selected="true"] {
              border-bottom: solid 2px var(--text-active-blue-france);
            }
          }
        }
      }
      .requests--container--panel {
        padding: 0;
        .requests--container--panel--content {
          display: flex;
          flex-direction: column;
          margin-top: 1.5rem;
          &:has(div.no-requests) {
            align-items: center;
            justify-content: center;
            height: calc(100vh - 15rem);
            min-height: 10rem;
          }
          .no-requests {
            flex-direction: column;
            text-align: center;
            padding: 1rem;
            display: flex;
            font-size: 16px;
            line-height: 24px;
            color: var(--grey-0-1000);
            img {
              height: 5rem;
              width: 5rem;
            }
            .no-requests--title {
              text-align: left;
            }
          }
        }
      }
    }
  }
</style>
