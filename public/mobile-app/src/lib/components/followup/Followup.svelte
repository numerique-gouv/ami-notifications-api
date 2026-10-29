<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_SKELETON_DEBUG_DELAY } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupItem from '$lib/components/followup/FollowupItem.svelte';
  import FollowupNoConsent from '$lib/components/followup/FollowupNoConsent.svelte';
  import FollowupItemModal from '$lib/components/modal/FollowupItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { buildConsents, type Consents } from '$lib/consents';
  import type {
    FollowupItem as FollowupItemType,
    Followup as FollowupType,
  } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';
  import { buildPartners, type Partners } from '$lib/partners';

  interface Props {
    archived?: boolean;
  }
  let { archived = false }: Props = $props();

  const backUrl = '/#/followup';
  let menuOpened: boolean = $state(false);
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
    if (PUBLIC_SKELETON_DEBUG_DELAY) {
      await new Promise((resolve) => {
        setTimeout(() => resolve(0), parseFloat(PUBLIC_SKELETON_DEBUG_DELAY));
      });
    }
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

  const toggleMoreMenu = () => {
    menuOpened = !menuOpened;
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
  <div class="skeleton followup">
    {#if !archived}
      <div class="followup--title">
        <h1 class="fr-h2">Mes démarches</h1>
      </div>
    {:else}
      <div class="followup-archived-space"></div>
    {/if}
    <div>
      {#each Array(10).keys() as i}
        <div class="fr-card followup-item">
          <div class="tag"></div>
          <div class="date"></div>
          <div class="line"></div>
          <div class="line"></div>
          <div class="line short"></div>
        </div>
      {/each}
    </div>
  </div>
{:then pageDataLoaded}
  <div class="followup {archived ? 'archived': ''}">
    {#if !archived}
      <div class="followup--title">
        <h1 class="fr-h2">Mes démarches</h1>
        {#if consents.hasAnyConsents()}
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
                onclick={goToArchivedFollowup}
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
    .followup-archived-space {
      height: 5.5rem;
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
  .skeleton {
    .followup {
      padding: 1.5rem 1rem;
    }
    .followup-archived-space {
      padding-top: 5rem;
    }
    .followup-item {
      position: relative;
      padding: 0.875rem 1rem;
      margin-bottom: 1.5rem;
      border-bottom: 0.25rem solid var(--border-active-blue-france);
      .tag {
        background: #ececfe;
        height: 1.2rem;
        width: 50%;
      }
      .date {
        background: #f5f5fe;
        height: 0.8rem;
        width: 30%;
        position: absolute;
        top: 0.875rem;
        right: 1rem;
      }
      .line {
        background: #f5f5fe;
        margin-top: 0.5rem;
        height: 1.2rem;
        &.short {
          width: 70%;
        }
      }
    }
  }
</style>
