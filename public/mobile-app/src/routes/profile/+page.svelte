<script lang="ts">
  import { onMount } from 'svelte';
  import type { Address } from '$lib/address';
  import { AMIGoto } from '$lib/ami-navigation';
  import Card from '$lib/components/Card.svelte';
  import PersonalDataConsentModal from '$lib/components/modal/PersonalDataConsentModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import {
    buildPersonalDataConsent,
    type PersonalDataConsent,
  } from '$lib/personal-data-consent';
  import type { DataOrigin, UserIdentity } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let identity: UserIdentity = $state() as UserIdentity;
  let address: Address | undefined = $state();
  let address_origin: DataOrigin | undefined = $state();
  let email_origin: DataOrigin | undefined = $state();
  let displayPersonalDataConsentBlock: boolean = $state(false);
  let displayModal: boolean = $state(false);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    } else {
      identity = userStore.connected.identity;
      address = identity.address;
      address_origin = identity.dataDetails.address.origin;
      email_origin = identity.dataDetails.email.origin;

      const personalDataConsent: PersonalDataConsent = await buildPersonalDataConsent();
      if (!personalDataConsent.consent_datetime) {
        displayPersonalDataConsentBlock = true;
      }
    }
  });

  const goToEditPreferredUsername = async () => {
    AMIGoto('/#/edit-preferred-username');
  };

  const goToEditEmail = async () => {
    AMIGoto('/#/edit-email');
  };

  const goToEditAddress = async () => {
    AMIGoto('/#/edit-address');
  };

  const openPersonalDataConsentModal = () => {
    displayModal = true;
  };
</script>

<NavWithBackButton title="Mon profil" {backUrl} />

{#if identity}
  <div class="fr-container profile-content-container fr-pt-14w" data-testid="profile">
    <Card
      id="profile-identity"
      iconClassName="fr-icon-account-circle-line fr-mr-1w am-icon-20"
      title="Mon identité"
    >
      <p class="paragraph-wrapper fr-mb-2w">
        Vous êtes&nbsp;:
        <br>
        <b
          >{identity.given_name} {identity.preferred_username || identity.family_name},</b
        >
        <br>
        {#if identity.gender == "female"}
          née
        {:else}
          né
        {/if}
        {#if identity.preferred_username}
          <b>{identity.family_name}</b>
        {/if}
        le <b>{identity.birthdate}</b>
        {#if identity.birthplace}
          à <b>{identity.birthplace} {identity.birthcountry}</b>
          <br>
        {/if}
        <span class="fr-text--xs">Informations fournies par FranceConnect</span>
        <br>
      </p>

      <button
        type="button"
        class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary"
        onclick={goToEditPreferredUsername}
        data-testid="preferred-username-button"
        aria-label="Modifier mon identité"
      >
        Modifier
      </button>
    </Card>

    <Card
      id="profile-email"
      iconClassName="fr-icon-mail-line fr-mr-1w am-icon-20"
      title="Contact"
    >
      <p class="paragraph-wrapper fr-mb-2w">
        Pour vous contacter&nbsp;:
        <br>
        <b>{identity.email}</b>
        <br>
        {#if email_origin == 'france-connect'}
          <span class="fr-text--xs">Informations fournies par FranceConnect</span>
          <br>
        {/if}
      </p>

      <button
        type="button"
        class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary"
        onclick={goToEditEmail}
        data-testid="email-button"
        aria-label="Modifier les informations de contact"
      >
        Modifier
      </button>
    </Card>

    <Card
      id="profile-address"
      iconClassName="fr-icon-map-pin-user-line fr-mr-1w am-icon-20"
      title="Mon adresse"
    >
      {#if address}
        <p class="paragraph-wrapper fr-mb-2w">
          Votre résidence principale
          <br>
          <b>{address.name}</b>
          <br>
          <b>{address.postcode} {address.city}</b>
          <br>
          {#if address_origin == 'api-particulier'}
            <span class="fr-text--xs">Informations fournies par la Caf</span>
            <br>
          {/if}
        </p>
      {/if}
      <button
        type="button"
        class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary"
        onclick={goToEditAddress}
        data-testid="address-button"
        aria-label={address ? "Modifier mon adresse" : "Définir une adresse"}
      >
        {#if !address}
          Définir une adresse
        {:else}
          Modifier
        {/if}
      </button>
    </Card>

    {#if displayPersonalDataConsentBlock}
      <div>
        Personnaliser votre profil
        <button type="button" onclick={openPersonalDataConsentModal}>
          Je veux utiliser mes données
        </button>
      </div>
    {/if}
  </div>
{/if}

{#if displayModal}
  <PersonalDataConsentModal
    bind:displayPersonalDataConsentBlock={displayPersonalDataConsentBlock}
    bind:displayModal={displayModal}
  />
{/if}
