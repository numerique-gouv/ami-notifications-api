<script lang="ts">
  import { onMount } from 'svelte';
  import { SvelteMap } from 'svelte/reactivity';
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupInformation from '$lib/components/followup/FollowupInformation.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import ConsentsSkeleton from '$lib/components/skeletons/ConsentsSkeleton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import {
    buildConsents,
    Consents,
    type ConsentsItem,
    updateAllConsents,
  } from '$lib/consents';
  import { buildFollowup, type Followup } from '$lib/followup';
  import { buildPartners, type Partners } from '$lib/partners';
  import { skeletonDebugDelay } from '$lib/skeleton';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let backUrl: string = '/';
  let consents: Consents = $state() as Consents;
  let consentItems: ConsentsItem[] = $state() as ConsentsItem[];
  let partners: Partners = $state() as Partners;
  let followup: Followup = $state() as Followup;
  let displayWarningBlocks: SvelteMap<string, boolean> = new SvelteMap();

  const buildConsentsAndPartners = async () => {
    partners = await buildPartners(); // expected side-effect
    return await buildConsents(partners);
  };

  const waitForPageData = async () => {
    await skeletonDebugDelay();
    [followup, consents] = await Promise.all([
      buildFollowup(),
      buildConsentsAndPartners(),
    ]);
    consentItems = consents.items;
    consentItems.forEach((consentItem: ConsentsItem) => {
      displayWarningBlocks.set(consentItem.partner_id, false);
    });
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
      return;
    }
  });

  const selectAll = async () => {
    await updateAllConsents(true);
    consentItems.forEach((consentItem: ConsentsItem) => {
      displayWarningBlocks.set(consentItem.partner_id, false);
    });
  };

  const saveConsents = async (partnerId: string, checked: boolean) => {
    const consentsItems: ConsentsItem[] | undefined = consentItems?.filter(
      (item) => item.partner_id === partnerId
    );

    if (consentsItems) {
      const consentsItem: ConsentsItem = consentsItems[0];
      await consentsItem.updateConsent(checked);
      const consents: Consents = await buildConsents(partners);
      consentItems = consents.items;

      if (consentsItem.hasFollowupItem(followup)) {
        displayWarningBlocks.set(consentsItem.partner_id, !checked);
      }
    }
  };

  const hideWarningBlock = (partnerId: string) => {
    displayWarningBlocks.set(partnerId, false);
  };
</script>

<NavWithBackButton title="Suivi des démarches" {backUrl} />

{#if userStore.connected}
  {#await waitForPageData()}
    <ConsentsSkeleton />
  {:then pageDataLoaded}
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

      {#if consentItems && consentItems.length}
        <div class="am-toggle-container">
          {#each consentItems as item}
            <Toggle
              id="{item.partner_id}"
              label="Suivre mes démarches <strong>{item.partner_name}</strong> sur mon appareil mobile"
              isChecked={item.consent_datetime !== null}
              onChangeAction={saveConsents}
            />
            {#if displayWarningBlocks.get(item.partner_id)}
              <div
                class="fr-notice fr-p-2w toast-wrapper warning"
                data-testid="warning-{item.partner_id}"
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
                      Si vous avez des démarches {item.partner_name} en cours ou à
                      venir, vous ne pourrez plus les suivre dans l’application.
                      L’historique de vos démarches est conservé.
                    </p>
                  </div>
                  <div class="toast-body-right-wrapper">
                    <button
                      onclick={() => hideWarningBlock(item.partner_id)}
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
        </div>
      {/if}
      <FollowupInformation />
    </div>
  {/await}
{/if}

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
