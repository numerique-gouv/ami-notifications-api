<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import type { Services } from '$lib/services';
  import { buildServices } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';

  let services: Services | null = $state(null);
  let backUrl: string = $state('/#/services');
  let inputValue: string = $state('');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }

    services = await buildServices();
  });
</script>

<div class="services-search-page fr-px-2w">
  <NavWithBackButton title="" {backUrl} />

  <div class="services-search-container fr-pt-8w">
    <h1 class="fr-h3">Rechercher un service</h1>
    <form class="search-form">
      <div class="fr-fieldset__element">
        <div class="fr-input-group autocomplete">
          <div class="fr-input-wrap fr-icon-search-line">
            <input
              class="fr-input"
              id="search-input"
              type="text"
              bind:value={inputValue}
              data-testid="search-input"
            >
          </div>
          {#if !inputValue}
            <div class="search-input-empty">
              <div class="no-services--icon">
                <img class="search-input-empty--icon" src="/icons/search.svg" alt="">
              </div>
              <div class="search-input-empty--title">
                Recherchez une démarche, un service, une situation de vie par mots-clés
              </div>
            </div>
          {/if}
        </div>
      </div>
    </form>
  </div>
</div>

<style>
  .services-search-page {
    .services-search-container {
      .search-input-empty {
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        text-align: center;
        font-size: 16px;
        line-height: 24px;
        color: var(--grey-0-1000);
        img {
          height: 5rem;
          width: 5rem;
        }
      }
    }
  }
</style>
