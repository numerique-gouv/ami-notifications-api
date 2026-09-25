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

<NavWithBackButton title="Thèmes" {backUrl} />

<div class="themes">
  <div>
    <p
      class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w {Item.KindInfo['personal'].icon} {Item.KindInfo['personal'].badgeClassName}"
    ></p>
    Échéance personnelle (rendez-vous, date de renouvellement etc.)
  </div>
  <div>
    <p
      class="fr-badge fr-badge--sm fr-badge--icon-left fr-mb-1w {Item.KindInfo['holiday'].icon} {Item.KindInfo['holiday'].badgeClassName}"
    ></p>
    Vacances et jours fériés
  </div>
</div>

<style>
  .themes {
    padding: 1.5rem 1rem;
    margin-top: 8rem;
    margin-bottom: 4.25rem;
  }
</style>
