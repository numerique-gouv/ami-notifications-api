<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-goto';
  import FollowupItem from '$lib/components/FollowupItem.svelte';
  import FollowupItemModal from '$lib/components/modal/FollowupItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import type { Followup, FollowupItem as FollowupItemType } from '$lib/followup';
  import { buildFollowup } from '$lib/followup';

  interface Props {
    archived?: boolean;
  }
  let { archived = false }: Props = $props();

  const backUrl = '/#/followup';
  let isFollowupEmpty: boolean = $state(true);
  let followup: Followup | null = $state(null);
  let selectedFollowupItem: FollowupItemType | null = $state(null);
  let menuOpened: boolean = $state(false);

  onMount(async () => {
    followup = await buildFollowup();
    console.log($state.snapshot(followup));
  });

  const openFollowupItemModal = (item: FollowupItemType) => {
    selectedFollowupItem = item;
  };

  const toggleMoreMenu = () => {
    menuOpened = !menuOpened;
  };

  const goToArchivedFollowup = () => {
    AMIGoto('/#/followup/archived');
  };
</script>

{#if archived}
  <NavWithBackButton title="Démarches archivées" {backUrl} />
{/if}

<div class="followup {archived ? 'archived': ''}">
  {#if !archived}
    <div class="followup--title">
      <h1 class="fr-h2">Mes démarches</h1>
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
    {#if archived && followup && followup.archived_items.length}
      {#each followup.archived_items as item}
        <FollowupItem item={item} onOpen={() => openFollowupItemModal(item)} />
      {/each}
    {:else if !archived && followup && followup.items.length}
      {#each followup.items as item}
        <FollowupItem item={item} onOpen={() => openFollowupItemModal(item)} />
      {/each}
    {:else}
      <div class="no-followup">
        <div class="no-followup--icon">
          <img class="followup-icon" src="/remixicons/tracking.svg" alt="">
        </div>
        <div class="no-followup--title">
          Après avoir effectué vos démarches, vous pouvez les suivre en temps réel
          depuis l’application.
        </div>
      </div>
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
    margin-bottom: 68px;
    &.archived {
      padding-top: 0;
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
      &:has(div.no-followup) {
        align-items: center;
        justify-content: center;
        height: calc(100vh - 15rem);
        min-height: 10rem;
      }
      .no-followup {
        flex-direction: column;
        text-align: center;
        padding: 1rem;
        display: flex;
        font-size: 16px;
        line-height: 24px;
        color: var(--grey-0-1000);
        img {
          height: 5rem;
          width: 5rem;
        }
        .no-followup--title {
          text-align: left;
        }
      }
    }
  }
</style>
