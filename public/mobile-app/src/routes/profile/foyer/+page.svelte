<script lang="ts">
  import { onMount } from 'svelte';
  import { monthName } from '$lib/agenda';
  import { AMIGoto } from '$lib/ami-navigation';
  import Card from '$lib/components/Card.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import type { FoyerData as FoyerDataType } from '$lib/user-data';
  import { formatShortDate } from '$lib/utils';

  let backUrl: string = '/#/profile';
  let foyerData: FoyerDataType | null | undefined = $state();

  const monthNameFromNumber = (number: number) => {
    const date = new Date();
    date.setMonth(number - 1);
    return monthName(date).toLowerCase();
  };

  const getNormalizedFournisseur = (fournisseur: string) => {
    if (fournisseur === 'CNAF') {
      return 'CAF';
    } else {
      return fournisseur;
    }
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
    foyerData = userStore.connected.getFoyer();
    if (foyerData === undefined) {
      window.location.href = `/silent-login-ami-fi?data-mode=foyer`;
      return;
    }
  });
</script>

<NavWithBackButton title="Mon foyer" {backUrl} allowHistoryBack={false} />

<div class="fr-container profile-content-container fr-pt-14w" data-testid="profile">
  {#if typeof(foyerData) === 'undefined'}
  <!-- nothing -->
  {:else if !foyerData}
    <div class="fr-container fr-pt-8w" data-testid="foyer">
      <h1 class="fr-h2 fr-mb-2w">Mon foyer</h1>

      <p>ICÔNE</p>

      <p>
        Les informations concernant votre foyer <strong>connues de la CAF</strong>
        (enfant, quotient familial) devraient remonter ici.
      </p>
    </div>
  {:else}
    {#if foyerData.enfants}
      <Card
        id="profil-foyer"
        iconClassName="fr-icon-parent-line fr-mr-1w am-icon-20"
        title="Mon foyer"
      >
        <p class="fr-mb-1w">
          Enfants :
          {#if foyerData.enfants.length === 0}
            pas d’enfants
          {/if}
        </p>
        {#if foyerData.enfants}
          <ul class="fr-raw-list">
            {#each foyerData.enfants as item}
              <li class="fr-mb-1w">
                <strong>{item.prenoms} {item.nom_usage || item.nom_naissance}</strong>
                <br>
                {#if item.sexe == 'M'}
                  né
                {:else}
                  née
                {/if}
                le <strong>{formatShortDate(item.date_naissance)}</strong>
              </li>
            {/each}
          </ul>
        {/if}

        <p class="fr-mb-0 am-text-mention-grey">
          Informations fournies par la CAF, mises à jour le XX.
        </p>
      </Card>
    {/if}

    {#if foyerData.quotient_familial}
      <Card
        id="profil-qf"
        iconClassName="fr-icon-calculator-line fr-mr-1w am-icon-20"
        title="Quotient familial"
      >
        <ul class="fr-raw-list">
          <li>Organisme : <strong
            >{#if foyerData.quotient_familial.fournisseur == "CNAF"}
              CAF
            {:else}
              {foyerData.quotient_familial.fournisseur}
            {/if}</strong
          ></li>
          <li>
            Montant du QF : <strong>{foyerData.quotient_familial.valeur} €</strong>
          </li>
          <li>Mois concerné : <strong
            >{monthNameFromNumber(foyerData.quotient_familial.mois)}
            {foyerData.quotient_familial.annee}</strong
          ></li>
          <li>Mois de calcul : <strong
            >{monthNameFromNumber(foyerData.quotient_familial.mois_calcul)}
            {foyerData.quotient_familial.annee_calcul}</strong
          ></li>
        </ul>
        <p class="fr-mt-2w fr-mb-0 am-text-mention-grey">
          Informations fournies par la
          {getNormalizedFournisseur(foyerData.quotient_familial.fournisseur)}, mises à
          jour le XX.
        </p>
      </Card>
    {/if}
  {/if}
  <p class="fr-mt-2w"><a href="/silent-login-ami-fi?data-mode=foyer">refresh</a> </p>
</div>
