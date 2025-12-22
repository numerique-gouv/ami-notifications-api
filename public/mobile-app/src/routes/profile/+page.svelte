<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import type { Address } from '$lib/address'
  import Card from '$lib/components/Card.svelte'
  import type { UserIdentity } from '$lib/state/User.svelte'
  import { userStore } from '$lib/state/User.svelte'

  let identity: UserIdentity = $state() as UserIdentity
  let address: Address | undefined = $state()

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
      return
    } else {
      identity = userStore.connected.identity
      address = identity.address
    }
  })

  const goToEditPreferredUsername = async () => {
    goto('/#/edit-preferred-username')
  }

  const goToEditAddress = async () => {
    goto('/#/edit-address')
  }
</script>

<nav class="fr-pb-0 fr-px-4v fr-pt-6v">
  <div class="back-link fr-mb-2v">
    <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </a>
  </div>
  <div class="title">
    <h2 class="fr-mb-0">Mon profil</h2>
  </div>
</nav>

{#if identity}
<div class="fr-m-4v profile-content-container" data-testid="profile">
  <Card id="profile-identity" iconHref="/remixicons/account-circle-line.svg" title="Mon identité">
    <p>Vous êtes&nbsp;:<br />
    <b>{identity.given_name} {identity.preferred_username || identity.family_name},</b><br />
    né{#if identity.gender == "female"}e{/if} {#if identity.preferred_username}<b>{identity.family_name}</b>{/if}
    le <b>{identity.birthdate}</b>
    {#if identity.birthplace}à <b>{identity.birthplace} {identity.birthcountry}</b><br />{/if}
    <span class="fr-text--xs">Informations fournies par FranceConnect</span><br />
    </p>

    <button type="button"
            class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary"
            onclick={goToEditPreferredUsername}
            data-testid="preferred-username-button"
    >
      Modifier
    </button>
  </Card>

  <Card iconHref="/remixicons/mail-line.svg" title="Contact">
    <p>Pour vous contacter&nbsp;:<br />
    <b>{identity.email}</b><br />
    <span class="fr-text--xs">Informations fournies par FranceConnect</span><br />
    </p>

    <button type="button" class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary">Modifier</button>
  </Card>

  <Card iconHref="/remixicons/map-pin-user-line.svg" title="Mon adresse">
    {#if address}
      <p>
        Votre résidence principale :<br />
        <b>{address.name}</b><br />
        <b>{address.postcode} {address.city}</b><br />
      </p>
    {/if}
    <button type="button"
            class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary"
            onclick={goToEditAddress}
            data-testid="address-button"
    >
      {#if !address}
        Définir une adresse
      {:else}
        Modifier
      {/if}
    </button>
  </Card>
</div>
{/if}

<style>
  nav {
    .back-link {
      color: var(--text-active-blue-france);
      a {
        text-decoration: none;
        --underline-img: none;
      }
    }
    .title {
      display: flex;
      h2 {
        flex-grow: 1;
      }
    }
  }
</style>
