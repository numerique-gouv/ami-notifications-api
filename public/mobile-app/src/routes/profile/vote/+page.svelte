<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import Card from '$lib/components/Card.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/profile';
  // const DEMARCHE_URL = 'https://www.service-public.gouv.fr/particuliers/vosdroits/R51788';
  const DEMARCHE_URL = 'https://situation.elections.interieur.gouv.fr/';
  let voteData = {
    nationalNumber: '1292992124',
    pollingStationNumber: '19',
    pollingStationName: 'Collège Lakanal',
    pollingStationAddress: '17 Rue Lakanal, 92700 Colombes',
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
  });

  const goToDemarche = () => {
    AMIGoto(DEMARCHE_URL);
  };
</script>

<svelte:head>
  <title>Mon profil</title>
</svelte:head>

<NavWithBackButton title="Ma situation électorale" {backUrl} />

<div class="fr-container profile-content-container fr-pt-14w" data-testid="vote-data">
  {#if !voteData}
    <div class="image-wrapper">
      <img src="/remixicons/city-hall.svg" alt="">
    </div>

    <p>
      Vérifier <strong>votre inscription électorale</strong> et
      <strong>votre bureau de vote</strong> pour voir s’afficher ici votre situation
      électorale.
    </p>

    <button
      type="button"
      class="fr-btn fr-btn--lg am-btn-w100"
      onclick={goToDemarche}
      data-testid="external-item-button"
    >
      Vérifier mon inscription
    </button>
  {:else}
    <Card id="profile-vote" title="Ma situation électorale">
      <p class="fr-mb-1w">
        <!-- TODO: électeur ou électrice selon le genre -->
        Votre numéro national d’électeur&nbsp;:
        {#if voteData.nationalNumber}
          {voteData.nationalNumber}
        {/if}
      </p>

      <p class="fr-mb-1w">
        Votre bureau de vote&nbsp;:
        {#if voteData.pollingStationNumber}
          Bureau n° {voteData.pollingStationNumber}
        {/if}
        {#if voteData.pollingStationName}
          {voteData.pollingStationName}
        {/if}
        {#if voteData.pollingStationAddress}
          {voteData.pollingStationAddress}
        {/if}
      </p>
    </Card>
  {/if}
</div>

<style>
  .image-wrapper {
    padding: 1rem 0 1rem 0;
    text-align: center;
  }
</style>
