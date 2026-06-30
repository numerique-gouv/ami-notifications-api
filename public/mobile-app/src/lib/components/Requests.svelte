<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import RequestItemModal from '$lib/components/modal/RequestItemModal.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import RequestItem from '$lib/components/RequestItem.svelte';
  import type { FollowUp, RequestItem as RequestItemType } from '$lib/followup';
  import { buildFollowUp } from '$lib/followup';

  interface Props {
    archived?: boolean;
  }
  let { archived = false }: Props = $props();

  const backUrl = '/#/requests';
  let isFollowUpEmpty: boolean = $state(true);
  let followUp: FollowUp | null = $state(null);
  let selectedRequestItem: RequestItemType | null = $state(null);
  let menuOpened: boolean = $state(false);

  onMount(async () => {
    followUp = await buildFollowUp();
    console.log($state.snapshot(followUp));
  });

  const openRequestItemModal = (item: RequestItemType) => {
    selectedRequestItem = item;
  };

  const toggleMoreMenu = () => {
    menuOpened = !menuOpened;
  };

  const gotoArchivedRequests = () => {
    goto('/#/requests/archived');
  };
</script>

<div class="requests {archived ? 'archived': ''}">
  {#if archived}
    <NavWithBackButton title="Démarches archivées" {backUrl} />
  {:else}
    <div class="requests--title">
      <h2>Mes démarches</h2>
      <div class="requests--title--icon">
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
              onclick={gotoArchivedRequests}
              data-testid="archived-requests-button"
            >
              Démarches archivées
            </button>
          </li>
        </ul>
      {/if}
    </div>
  {/if}

  <div class="requests--container" data-testid="requests">
    {#if archived && followUp && followUp.archived_items.length}
      {#each followUp.archived_items as item}
        <RequestItem item={item} onOpen={() => openRequestItemModal(item)} />
      {/each}
    {:else if !archived && followUp && followUp.items.length}
      {#each followUp.items as item}
        <RequestItem item={item} onOpen={() => openRequestItemModal(item)} />
      {/each}
    {:else}
      <div class="no-requests">
        <div class="no-requests--icon">
          <img class="requests-icon" src="/remixicons/tracking.svg" alt="">
        </div>
        <div class="no-requests--title">
          Après avoir effectué vos démarches, vous pouvez les suivre en temps réel
          depuis l’application.
        </div>
      </div>
    {/if}
  </div>
</div>

{#if selectedRequestItem}
  <RequestItemModal
    bind:item={selectedRequestItem}
    bind:followUp={followUp}
    bind:isFollowUpEmpty={isFollowUpEmpty}
  />
{/if}

<style>
  .requests {
    padding: 1.5rem 1rem;
    margin-bottom: 68px;
    &.archived {
      padding-top: 0;
      margin-bottom: 0;
    }
    .requests--title {
      display: flex;
      position: relative;
      h2 {
        flex-grow: 1;
      }
      .requests--title--icon {
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
    .requests--container {
      display: flex;
      flex-direction: column;
      &:has(div.no-requests) {
        align-items: center;
        justify-content: center;
        height: calc(100vh - 15rem);
        min-height: 10rem;
      }
      .no-requests {
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
        .no-requests--title {
          text-align: left;
        }
      }
    }
  }
</style>
