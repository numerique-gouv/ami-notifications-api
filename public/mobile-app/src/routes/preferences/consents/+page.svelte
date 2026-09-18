<script lang="ts">
  import { onMount } from 'svelte';
  import { SvelteMap } from 'svelte/reactivity';
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
  let displayWarningBlocks: SvelteMap<string, boolean> = new SvelteMap();

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    } else {
      partners = await buildPartners();
      partnerIds = partners.items.map((item: PartnersItem) => item.slug);
      const consents: Consents = await buildConsents(partnerIds);
      consentItems = consents.items;
      followup = await buildFollowup();

      consentItems.forEach((consentItem: ConsentsItem) => {
        displayWarningBlocks.set(consentItem.partner_id, false);
      });
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
    const consents: Consents = await buildConsents(partnerIds);
    consentItems = consents.items;

    const consentsItem: ConsentsItem[] | undefined = consentItems?.filter(
      (item) => item.partner_id === partnerId
    );

    if (consentsItem && consentsItem[0].hasFollowupItem(followup)) {
      displayWarningBlocks.set(consentsItem[0].partner_id, !checked);
    }
  };

  const hideWarningBlock = (partnerId: string) => {
    displayWarningBlocks.set(partnerId, false);
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
        <div
          class="fr-notice fr-p-2w toast-wrapper warning"
          data-testid="warning-{item.slug}"
        >
          <div class="toast-body">
            <div class="toast-body-left-wrapper">
              <div class="fr-mb-1v toast-title-container">
                <span
                  class="fr-icon-warning-fill fr-mr-1w warning"
                  aria-hidden="true"
                ></span>
                <p class="fr-text--bold">Attention</p>
              </div>
              <p class="fr-text--sm">
                Si vous avez des démarches {item.name} en cours ou à venir, vous ne
                pourrez plus les suivre dans l’application. L’historique de vos
                démarches est conservé.
              </p>
            </div>
            <div class="toast-body-right-wrapper">
              <button
                onclick={() => hideWarningBlock(item.slug)}
                aria-label="Fermer le toast"
                data-testid="close-button"
              >
                <span class="fr-icon-close-line" aria-hidden="true"></span>
              </button>
            </div>
          </div>
        </div>
      {/if}
    {/each}
  {/if}
  <FollowupInformation />
</div>

<style>
  .toast-wrapper {
    border-radius: 0.25rem;
    color: var(--grey-50-1000);
    &.warning {
      background-color: var(--yellow-moutarde-950-100);
    }
    .toast-body {
      display: flex;
      justify-content: space-between;
      .toast-body-left-wrapper {
        .toast-title-container {
          display: flex;
          span {
            &.warning::before {
              background-color: var(--warning-425-625);
            }
          }
        }
      }
      button {
        font-size: 14px;
        color: var(--blue-france-sun-113-625);
      }
    }
  }
</style>
