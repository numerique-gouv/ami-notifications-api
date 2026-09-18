<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupInformation from '$lib/components/followup/FollowupInformation.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import {
    buildConsents,
    Consents,
    type ConsentsItem,
    updateAllConsents,
    updateConsent,
  } from '$lib/consents';
  import { buildFollowup, type Followup, FollowupItem } from '$lib/followup';
  import { buildPartners, type Partners, PartnersItem } from '$lib/partners';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();

  let backUrl: string = '/';
  let consentItems: ConsentsItem[] | undefined = $state(data.consentItems);
  let partners: Partners | null = $state(data.partners);
  let partnerIds: string[];
  let followup: Followup | null = $state(data.followup);
  let displayWarningBlocks: Map<string, boolean> = $state(data.displayWarningBlocks);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    } else {
      partners = await buildPartners();
      partnerIds = partners.items.map((item: PartnersItem) => item.slug);
      const consents: Consents = await buildConsents(partnerIds);
      consentItems = consents.items;
      followup = await buildFollowup();
    }
  });

  const selectAll = async () => {
    await updateAllConsents(true);
    const consents: Consents = await buildConsents(partnerIds);
    consentItems = consents.items;

    partners?.items.forEach((partner) => {
      const toggleElement: HTMLElement | null = document.getElementById(partner.slug);
      if (toggleElement) {
        const toggleInput: HTMLInputElement = toggleElement as HTMLInputElement;
        toggleInput.checked = true;
      }
    });
  };

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
    await buildConsents(partnerIds);

    // s'affiche quand au moins 1 démarche en cours pour ce partenaire et qu'on le désactive
    const consentsItem: ConsentsItem[] | undefined = consentItems?.filter(
      (item) => item.partner_id === partnerId
    );
    if (consentsItem?.[0].hasFollowupItem(followup)) {
      displayWarningBlocks.set(consentsItem[0].partner_id, !checked);
      console.log(displayWarningBlocks.get(consentsItem[0].partner_id));
    }
    console.log(displayWarningBlocks);
  };
</script>

<NavWithBackButton title="Suivi des démarches" {backUrl} />

<div class="fr-container consents-content-container fr-pt-14w">
  <button
    id="select-all-button"
    class="fr-btn fr-btn--secondary fr-mb-2v"
    type="button"
    onclick={selectAll}
    data-testid="select-all-button"
  >
    Tout suivre
  </button>

  {#if partners && partners.items.length}
    {#each partners.items as item}
      <Toggle
        id="{item.slug}"
        label="Suivre mes démarches <strong>{item.name}</strong> sur mon appareil mobile"
        isChecked={hasConsentedFor(item.slug)}
        onChangeAction={saveConsents}
      />
      {#if displayWarningBlocks.get(item.slug)}
        <!--s'affiche quand au moins 1 démarche en cours pour ce partenaire et qu'on le désactive-->
        <div>orange</div>
      {/if}
    {/each}
  {/if}
  <FollowupInformation />
</div>
