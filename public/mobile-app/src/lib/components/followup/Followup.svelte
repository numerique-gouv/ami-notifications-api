<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupItem from '$lib/components/followup/FollowupItem.svelte';
  import FollowupNoConsent from '$lib/components/followup/FollowupNoConsent.svelte';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import FollowupItemModal from '$lib/components/modal/FollowupItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import FollowupSkeleton from '$lib/components/skeletons/FollowupSkeleton.svelte';
  import { buildConsents, type Consents } from '$lib/consents';
  import type {
    FollowupItem as FollowupItemType,
    Followup as FollowupType,
  } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import { buildPartners, type Partners } from '$lib/partners';
  import { skeletonDebugDelay } from '$lib/skeleton';

  interface Props {
    archived?: boolean;
  }
  let { archived = false }: Props = $props();

  const backUrl = '/#/followup';
  let isExpanded: boolean = $state(false);

  let followup: FollowupType = $state() as FollowupType;
  let consents: Consents = $state() as Consents;
  let partners: Partners = $state() as Partners;
  let isFollowupEmpty: boolean = $state(false);

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
    isFollowupEmpty = followup.isEmpty();
    isExpanded = expandAccordion();
  };

  const expandAccordion = (): boolean => {
    if (followup && !archived) {
      return followup.items?.length === 0;
    } else if (followup && archived) {
      return followup.archived_items?.length === 0;
    }
    return false;
  };

  const goToArchivedFollowup = () => {
    AMIGoto('/#/followup/archived');
  };

  const goToConsents = () => {
    AMIGoto('/#/preferences/consents');
  };
</script>

{#if archived}
  <NavWithBackButton title="Démarches archivées" {backUrl} />
{/if}

{#await waitForPageData()}
  <FollowupSkeleton archived={archived} />
{:then pageDataLoaded}
  <div class="followup {archived ? 'archived': ''}">
    {#if !archived}
      <div class="followup--title">
        <h1 class="fr-h2">Mes démarches</h1>
        {#if consents.hasAnyConsents()}
          <div>
            <button
              id="followup-page-options-button"
              aria-controls="followup-page-options-modal"
              aria-expanded="false"
              type="button"
              data-fr-opened="false"
              class="fr-btn fr-icon-more-2-fill fr-btn--tertiary-no-outline am-followup-page-options"
              data-testid="followup-page-options-open-modal-button"
            >
              Sous menu de mes démarches
            </button>

            <BottomModal modalId="followup-page-options-modal">
              {#snippet modalContent()}
                <h2
                  id="followup-page-options-modal-title"
                  class="fr-h5 fr-mb-3v fr-sr-only"
                >
                  Sous menu de mes démarches
                </h2>
                <ul class="fr-raw-list followup-item-modal-footer">
                  <li>
                    <button
                      onclick={goToArchivedFollowup}
                      data-testid="archived-followup-button"
                      class="fr-btn fr-btn--lg fr-p-0 fr-btn--tertiary-no-outline fr-icon-inbox-archive-line fr-btn--icon-left fr-text--md fr-text-title--grey archive-followup-item"
                    >
                      Démarches archivées
                    </button>
                  </li>
                </ul>
              {/snippet}
            </BottomModal>
          </div>
        {/if}
      </div>
    {/if}

    <div class="followup--container" data-testid="followup">
      {#if consents.hasAnyConsents()}
        {#if archived && followup && followup.archived_items.length}
          {#each followup.archived_items as item, i}
            <FollowupItem item={item} hasModal={false} />
          {/each}
        {:else if !archived && followup && followup.items.length}
          {#each followup.items as item, i}
            <FollowupItem item={item} hasModal={true} index="followup-items-{i}" />
            <FollowupItemModal
              item={item}
              followup={followup}
              isFollowupEmpty={isFollowupEmpty}
              index="followup-items-{i}"
            />
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
                  <span class="fr-icon-information-line" aria-hidden="true"></span>
                  <span class="fr-sr-only">Information</span>
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
                          class="fr-btn fr-btn--secondary am-btn-w100"
                          onclick={()=> AMIGoto(item.link)}
                        >
                          {item.name}
                        </button>
                      </li>
                    {/each}
                  {/if}
                </ul>
                {#if !consents.hasAllConsents()}
                  <p>Vérifiez que vous suivez bien toutes vos démarches</p>
                  <div class="consent-action-button">
                    <button
                      class="fr-btn fr-btn--lg"
                      type="button"
                      onclick={goToConsents}
                      data-testid="consent-button"
                    >
                      Je veux suivre mes démarches
                    </button>
                  </div>
                {/if}
              </div>
            </div>
          </section>
        </div>
      {:else}
        <FollowupNoConsent />
      {/if}
    </div>
  </div>
{/await}

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

    .am-followup-page-options {
      &.fr-btn:before {
        --icon-size: 1.25rem;
        margin-left: 0.125rem;
        margin-right: 0.625rem;
      }
    }
  }
</style>
