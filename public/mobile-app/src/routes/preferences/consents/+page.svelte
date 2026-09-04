<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import FollowupInformation from '$lib/components/followup/FollowupInformation.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import {
    buildConsents,
    Consents,
    type ConsentsItem,
    updateConsent,
  } from '$lib/consents';
  import { buildPartners, type Partners } from '$lib/partners';
  import { userStore } from '$lib/state/User.svelte.js';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();

  let backUrl: string = '/';
  let consentItems: ConsentsItem[] | undefined = $state([]);
  let partners: Partners | null = $state(data.partners);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    } else {
      const consents: Consents = await buildConsents();
      consentItems = consents.items;
      partners = await buildPartners();
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
  {#if partners && partners.items.length}
    {#each partners.items as item}
      <Toggle
        id="{item.slug}"
        label="Suivre mes démarches <strong>{item.name}</strong> sur mon appareil mobile"
        isChecked={hasConsentedFor(item.slug)}
        onChangeAction={saveConsents}
      />
    {/each}
  {/if}
  <FollowupInformation />
</div>
