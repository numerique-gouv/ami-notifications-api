<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import FollowupItem from '$lib/components/followup/FollowupItem.svelte';
  import FollowupNoConsent from '$lib/components/followup/FollowupNoConsent.svelte';
  import FollowupItemModal from '$lib/components/modal/FollowupItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { hasAnyConsents as hasAnyConsentsFunc } from '$lib/consents';
  import type { Followup, FollowupItem as FollowupItemType } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import { buildPartners, type Partners } from '$lib/partners';

  interface Props {
    archived?: boolean;
    followupProp: Followup;
    isFollowupEmptyProp: boolean;
    hasAnyConsentsProp: boolean;
    partnersProp: Partners;
  }
  let {
    archived = false,
    followupProp,
    isFollowupEmptyProp,
    hasAnyConsentsProp,
    partnersProp,
  }: Props = $props();

  const backUrl = '/#/followup';
  let isFollowupEmpty: boolean = $state(isFollowupEmptyProp);
  let followup: Followup | null = $state(followupProp);
  let selectedFollowupItem: FollowupItemType | null = $state(null);
  let menuOpened: boolean = $state(false);
  let hasAnyConsents: boolean = $state(hasAnyConsentsProp);
  let isExpanded: boolean = $state(isFollowupEmptyProp);
  let partners: Partners | null = $state(partnersProp);

  onMount(async () => {
    followup = await buildFollowup();
    console.log($state.snapshot(followup));
    hasAnyConsents = await hasAnyConsentsFunc();
    isExpanded = expandAccordion();
    partners = await buildPartners();
  });

  const expandAccordion = (): boolean => {
    if (followup && !archived) {
      return followup.items?.length === 0;
    } else if (followup && archived) {
      return followup.archived_items?.length === 0;
    }
    return false;
  };

  const openFollowupItemModal = (item: FollowupItemType) => {
    selectedFollowupItem = item;
  };

  const toggleMoreMenu = () => {
    menuOpened = !menuOpened;
  };

  const gotoArchivedFollowup = () => {
    goto('/#/followup/archived');
  };

  const gotoConsents = () => {
    goto('/#/preferences/consents');
  };
</script>

{#if archived}
  <NavWithBackButton title="Démarches archivées" {backUrl} />
{/if}

<div class="followup {archived ? 'archived': ''}">
  {#if !archived}
    <div class="followup--title">
      <h1 class="fr-h2">Mes démarches</h1>
      {#if hasAnyConsents}
        <div class="followup--title--icon">
          <button
            class="more"
            type="button"
            data-testid="more-button"
            onclick={toggleMoreMenu}
          >
            <span class="fr-icon-more-2-fill" aria-hidden="true"></span><span
              class="fr-sr-only"
              >Sous-menu</span
            >
          </button>
        </div>
      {/if}
      {#if menuOpened}
        <ul id="more-menu" data-testid="more-menu">
          <li>
            <span class="fr-icon-inbox-archive-line" aria-hidden="true"></span>
            <button
              type="button"
              onclick={gotoArchivedFollowup}
              data-testid="archived-followup-button"
            >
              Démarches archivées
            </button>
          </li>
        </ul>
      {/if}
    </div>
  {/if}

  <div class="followup--container" data-testid="followup">
    {#if hasAnyConsents}
      {#if archived && followup && followup.archived_items.length}
        {#each followup.archived_items as item}
          <FollowupItem item={item} onOpen={() => openFollowupItemModal(item)} />
        {/each}
      {:else if !archived && followup && followup.items.length}
        {#each followup.items as item}
          <FollowupItem item={item} onOpen={() => openFollowupItemModal(item)} />
        {/each}
      {/if}
      <div class="no-followup">
        <section class="fr-accordion fr-mt-4v">
          <h3 class="fr-accordion__title">
            <button
              type="button"
              class="fr-accordion__btn"
              aria-expanded="{isExpanded}"
              aria-controls="accordion-1"
              data-testid="accordion-button"
            >
              <span class="fr-pr-2v">
                <span class="fr-icon-information-line" aria-hidden="true"> </span>
              </span>
              Votre démarche n’apparaît pas&nbsp;?
            </button>
          </h3>
          <div id="accordion-1" class="fr-collapse fr-p-0">
            <div class="fr-m-4v">
              <p>Consultez votre compte</p>
              <ul class="fr-p-0">
                {#if partners && partners.items.length}
                  {#each partners.items as item}
                    <li class="account fr-pb-4v">
                      <button
                        type="button"
                        class="fr-btn fr-btn--secondary am-btn-target am-btn-w100"
                        onclick={()=> window.location.href = item.link}
                      >
                        {item.name}
                      </button>
                    </li>
                  {/each}
                {/if}
              </ul>
              <p>Vérifiez que vous suivez bien toutes vos démarches</p>
              <div class="consent-action-button">
                <button
                  class="fr-btn fr-btn--lg"
                  type="button"
                  onclick={gotoConsents}
                  data-testid="consent-button"
                >
                  Je veux suivre mes démarches
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    {:else}
      <FollowupNoConsent />
    {/if}
  </div>
</div>

{#if selectedFollowupItem}
  <FollowupItemModal
    bind:item={selectedFollowupItem}
    bind:followup={followup}
    bind:isFollowupEmpty={isFollowupEmpty}
  />
{/if}

<style>
  .followup {
    padding: 1.5rem 1rem;
    margin-bottom: 4.25rem;
    &.archived {
      padding-top: 7rem;
      margin-bottom: 0;
    }
    .followup--title {
      display: flex;
      position: relative;
      h1 {
        flex-grow: 1;
      }
      .followup--title--icon {
        padding-top: 0.25rem;
        color: var(--text-active-blue-france);
      }
      #more-menu {
        position: absolute;
        margin: 0;
        padding: 0.5rem 0;
        top: 2.5rem;
        right: 0.25rem;
        border: 1px solid var(--grey-950-100);
        border-radius: 0.25rem;
        z-index: 500;
        background-color: var(--background-default-grey);
        box-shadow: 0px 1px 2px 0px #0000004d;
        li {
          list-style: none;
          padding: 0.5rem 1rem;
          background-color: var(--background-default-grey);
          font-size: 14px;
          line-height: 24px;
          span {
            color: var(--text-active-blue-france);
            &::before {
              --icon-size: 1.25rem;
            }
          }
        }
      }
    }
    .followup--container {
      display: flex;
      flex-direction: column;
      .no-followup {
        .fr-accordion {
          .fr-accordion__btn {
            font-size: 14px;
            font-weight: 700;
          }
          .account {
            list-style: none;
          }
          &:before {
            border: solid 1px var(--border-default-blue-france);
            box-shadow: none;
          }
          .consent-action-button {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            button {
              display: flex;
              justify-content: center;
              width: 100%;
            }
          }
        }
      }
    }
  }
</style>
