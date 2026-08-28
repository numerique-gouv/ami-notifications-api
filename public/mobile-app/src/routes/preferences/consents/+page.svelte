<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import FollowupInformation from '$lib/components/FollowupInformation.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import {
    buildConsents,
    Consents,
    type ConsentsItem,
    updateConsent,
  } from '$lib/consents';
  import { userStore } from '$lib/state/User.svelte.js';

  let backUrl: string = '/';
  let consentItems: ConsentsItem[] | undefined = $state([]);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    } else {
      const consents: Consents = await buildConsents();
      consentItems = consents.items;
    }
  });

  const hasConsentedFor = (id: string): boolean => {
    if (consentItems) {
      const consentItem: ConsentsItem = consentItems.filter(
        (item) => item.partner_id === id
      )[0];
      if (consentItem) {
        return consentItem.consent_datetime !== null;
      }
    }
    return false;
  };

  const saveConsents = async (partnerId: string, checked: boolean) => {
    await updateConsent(partnerId, checked);
    await buildConsents();
  };
</script>

<NavWithBackButton title="Suivi des démarches" {backUrl} />

<div class="fr-container consents-content-container fr-pt-14w">
  <Toggle
    id="psl"
    label="Suivre mes démarches <strong>Service Public</strong> sur mon appareil mobile"
    isChecked={hasConsentedFor('psl')}
    onChangeAction={saveConsents}
  />
  <Toggle
    id="dinum-dn"
    label="Suivre mes démarches <strong>Démarches Numériques</strong> sur mon appareil mobile"
    isChecked={hasConsentedFor('dinum-dn')}
    onChangeAction={saveConsents}
  />
  <Toggle
    id="dinum-ami"
    label="Suivre mes démarches <strong>AMI</strong> sur mon appareil mobile"
    isChecked={hasConsentedFor('dinum-ami')}
    onChangeAction={saveConsents}
  />
  <Toggle
    id="dinum-rdvsp"
    label="Suivre mes démarches <strong>Rendez-vous SP</strong> sur mon appareil mobile"
    isChecked={hasConsentedFor('dinum-rdvsp')}
    onChangeAction={saveConsents}
  />
  <FollowupInformation />
</div>
