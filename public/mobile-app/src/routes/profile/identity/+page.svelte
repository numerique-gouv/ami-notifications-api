<script lang="ts">
  import { onMount } from 'svelte';
  import type { Address } from '$lib/address';
  import { AMIGoto } from '$lib/ami-navigation';
  import Card from '$lib/components/Card.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import type { DataOrigin, UserIdentity } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/profile';
  let identity: UserIdentity = $state() as UserIdentity;
  let fullName: string = $state('');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
    identity = userStore.connected.identity;
    fullName = userStore.connected.getFullName();
  });

  const goToEditPreferredUsername = async () => {
    AMIGoto('/#/profile/identity/edit-preferred-username');
  };
</script>

<NavWithBackButton title="Mon identité" {backUrl} />

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
        <b>{fullName},</b>
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
  </div>
{/if}
