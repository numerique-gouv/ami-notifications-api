<script lang="ts">
  import { onMount } from 'svelte';
  import { Item } from '$lib/agenda';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = $state('/#/agenda');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<NavWithBackButton title="" {backUrl} />

<div class="themes-container fr-pt-8w fr-px-2w">
  <h1 class="fr-h2 fr-mb-4w">Thèmes</h1>
  <ul class="fr-raw-list">
    <li class="fr-mb-3w">
      <p
        class="fr-badge fr-badge--sm fr-badge--icon-left fr-mr-1w {Item.KindInfo['personal'].icon} {Item.KindInfo['personal'].badgeClassName}"
      ></p>
      Échéance personnelle (rendez-vous, date de renouvellement etc.)
    </li>
    <li class="fr-mb-3w">
      <p
        class="fr-badge fr-badge--sm fr-badge--icon-left fr-mr-1w {Item.KindInfo['holiday'].icon} {Item.KindInfo['holiday'].badgeClassName}"
      ></p>
      Vacances et jours fériés
    </li>
  </ul>
</div>

<style>
  .themes-container {
    ul {
      .fr-badge {
        min-height: 1.5rem;
        &::before {
          margin: 0;
        }
      }
    }
  }
</style>
