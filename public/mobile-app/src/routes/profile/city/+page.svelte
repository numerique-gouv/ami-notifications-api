<script lang="ts">
  import { onMount } from 'svelte';
  import type { Address } from '$lib/address';
  import { AMIGoto } from '$lib/ami-navigation';
  import { type APIMairie, retrieveMairie } from '$lib/api-annuaire-sp';
  import Card from '$lib/components/Card.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/profile';
  let address: Address | undefined = $state();
  let mairie: APIMairie | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
    address = userStore.connected.identity.address;
    if (address) {
      mairie = await retrieveMairie(address.citycode);
    }
  });

  const goToEditAddress = async () => {
    AMIGoto('/#/profile/addresses/edit-address');
  };
</script>

<svelte:head>
  <title>Mon profil - Ma commune</title>
</svelte:head>

<NavWithBackButton className="small-header" title="Ma commune" {backUrl} />

<div class="fr-container profile-content-container fr-pt-10w" data-testid="ma-commune">
  {#if mairie}
    <p class="fr-mb-2w">Votre mairie&nbsp;:</p>

    <Card id="profile-city" title={mairie.nom}>
      <button
        class="fr-btn"
        type="button"
        onclick={(e) => {if (mairie) { AMIGoto(mairie?.url_service_public) } else {e.preventDefault();} }}
        data-testid="mairie-button"
      >
        Aller sur le site de la mairie
      </button>
    </Card>
  {:else}
    <button
      type="button"
      class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary am-btn-w100"
      onclick={goToEditAddress}
      data-testid="address-button"
      aria-label="Renseigner votre adresse"
    >
      Renseigner votre adresse
    </button>
  {/if}
</div>
