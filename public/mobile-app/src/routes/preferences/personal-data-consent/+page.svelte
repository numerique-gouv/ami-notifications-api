<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import {
    buildPersonalDataConsent,
    type PersonalDataConsent,
  } from '$lib/personal-data-consent';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/preferences';
  let personalDataConsent: PersonalDataConsent | undefined = $state();
  let isPersonalDataConsentChecked: boolean = $state(false);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    } else {
      personalDataConsent = await buildPersonalDataConsent();
      if (personalDataConsent.consent_datetime) {
        isPersonalDataConsentChecked = true;
      }
    }
  });

  const savePersonalDataConsent = async (_id: string, checked: boolean) => {
    if (personalDataConsent) {
      await personalDataConsent.updateConsent(checked);
      personalDataConsent = await buildPersonalDataConsent();
    }
  };
</script>

<NavWithBackButton title="Consentement données personnelles" {backUrl} />

<div class="fr-container consents-content-container fr-pt-14w">
  <Toggle
    id="personal-data-consent-toggle"
    label="J’accepte que AMI <strong>utilise mes données administratives</strong> pour préremplir mes demandes et personnaliser mon profil"
    isChecked={isPersonalDataConsentChecked}
    onChangeAction={savePersonalDataConsent}
  />
</div>
