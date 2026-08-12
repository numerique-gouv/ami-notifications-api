<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import { type ConsentsItem, updateConsent } from '$lib/consents';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/';
  let consentItems: ConsentsItem[] | undefined = $state([]);

  const refreshConsents = () => {
    if (!userStore.connected) {
      return;
    }
    consentItems = userStore.connected?.getConsentsItems();
  };

  onMount(() => {
    if (!userStore.connected) {
      goto('/');
    } else {
      // consentItems = userStore.connected?.consents?.items;
      refreshConsents();
      console.log('onMount', consentItems);
      console.log('onMount getConsentsItems', userStore.connected?.getConsentsItems());
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

  const saveConsents = async (id: string, checked: boolean) => {
    if (!userStore.connected) {
      return;
    }
    console.log('id', id);
    console.log('checked', checked);
    await updateConsent(id, checked);
    console.log('onMount', consentItems);
  };
</script>

<NavWithBackButton title="Suivi des démarches" {backUrl} />

<div class="fr-container consents-content-container fr-pt-14w" data-testid="consents">
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
</div>
