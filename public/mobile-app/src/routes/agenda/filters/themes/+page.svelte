<script lang="ts">
  import { onMount } from 'svelte';
  import { Item, THEMES } from '$lib/agenda';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/agenda/filters');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<svelte:head>
  <title>Thèmes</title>
</svelte:head>

<NavWithBackButton title="" {backUrl} />

<div class="themes-container fr-pt-8w fr-px-2w">
  <h1 class="fr-h2 fr-mb-4w">Thèmes</h1>
  <ul class="fr-raw-list">
    {#each THEMES as theme}
      <li class="fr-mb-3w">
        <div aria-hidden="true">
          <p
            class="fr-badge fr-badge--sm fr-badge--icon-left {theme.icon} {theme.badgeClassName}"
          ></p>
        </div>
        {theme.label}
      </li>
    {/each}
  </ul>
</div>

<style>
  .themes-container {
    ul {
      li {
        align-items: center;
        display: flex;
        gap: 1rem;
      }
      .fr-badge {
        min-height: 1.5rem;
        &::before {
          margin: 0;
        }
      }
    }
  }
</style>
