<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import RequestItemModal from '$lib/components/modal/RequestItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import RequestItem from '$lib/components/RequestItem.svelte';
  import type { FollowUp, RequestItem as RequestItemType } from '$lib/follow-up';
  import { buildFollowUp } from '$lib/follow-up';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let followUp: FollowUp | null = $state(null);
  let selectedRequestItem: RequestItemType | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }

    followUp = await buildFollowUp();
    console.log($state.snapshot(followUp));
  });

  const refreshFollowUp = () => {
    buildFollowUp().then((result) => {
      followUp = result;
    });
  };

  const openRequestItemModal = (item: RequestItemType) => {
    selectedRequestItem = item;
  };
  const closeRequestItemModal = () => {
    selectedRequestItem = null;
  };
  const clickOnArchiveRequestItem = async (item: RequestItemType | null) => {
    if (item) {
      const result = await item.archive();
      if (result === true) {
        if (followUp) {
          refreshFollowUp();
        }
        closeRequestItemModal();
        toastStore.addToast("L'élément a bien été archivé", 'success', 3000, true);
      } else {
        closeRequestItemModal();
        toastStore.addToast("L'élément n'a pas pu être archivé", 'error', 3000, true);
      }
    }
  };
</script>

<div class="requests">
  <div class="requests--title">
    <h2>Mes démarches</h2>
  </div>

  <div class="requests--container" data-testid="requests">
    {#if followUp && followUp.items.length}
      {#each followUp.items as item}
        <RequestItem item={item} onOpen={() => openRequestItemModal(item)} />
      {/each}
    {:else}
      <div class="no-requests">
        <div class="no-requests--icon">
          <img
            class="requests-icon"
            src="/remixicons/tracking.svg"
            alt="Icône de suivi"
          >
        </div>
        <div class="no-requests--title">
          Après avoir effectué vos démarches, vous pouvez les suivre en temps réel
          depuis l’application.
        </div>
      </div>
    {/if}
  </div>
</div>
<Navigation currentItem="requests" />

{#if selectedRequestItem}
  <RequestItemModal onClose={closeRequestItemModal}>
    {#snippet header()}
      <h2 class="request-item-modal-header">{selectedRequestItem?.title}</h2>
    {/snippet}
    {#snippet footer()}
      <ul class="request-item-modal-footer">
        <li>
          <span class="fr-icon-inbox-archive-line"></span>
          <button
            onclick={() => clickOnArchiveRequestItem(selectedRequestItem)}
            title="Archiver l'élément"
            aria-label="Archiver l'élément"
            data-testid="archive-request-item-button"
            class="archive-request-item"
          >
            Archiver
          </button>
        </li>
      </ul>
    {/snippet}
  </RequestItemModal>
{/if}

<style>
  .requests {
    padding: 1.5rem 1rem;
    margin-bottom: 68px;
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
  h2.request-item-modal-header {
    font-size: 1.25rem;
  }
  ul.request-item-modal-footer {
    padding: 0;
    margin: 0;
    li {
      list-style: none;
    }
  }
</style>
