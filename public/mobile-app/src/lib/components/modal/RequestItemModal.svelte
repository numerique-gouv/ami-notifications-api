<script lang="ts">
  import ItemModal from '$lib/components/modal/ItemModal.svelte';
  import {
    buildFollowUp,
    type FollowUp,
    type RequestItem as RequestItemType,
  } from '$lib/follow-up';
  import { toastStore } from '$lib/state/toast.svelte';

  interface Props {
    item: RequestItemType | null;
    followUp: FollowUp | null;
    isFollowUpEmpty: boolean;
  }
  let {
    item = $bindable(),
    followUp = $bindable(),
    isFollowUpEmpty = $bindable(),
  }: Props = $props();

  const closeModal = () => {
    item = null;
  };

  const refreshFollowUp = () => {
    buildFollowUp().then((result) => {
      followUp = result;
      isFollowUpEmpty = !followUp.items.length;
    });
  };

  const clickOnArchiveRequestItem = async (item: RequestItemType | null) => {
    if (item) {
      const result = await item.archive();
      if (result === true) {
        if (followUp) {
          refreshFollowUp();
        }
        closeModal();
        toastStore.addToast("L'élément a bien été archivé", 'success', 3000, true);
      } else {
        closeModal();
        toastStore.addToast("L'élément n'a pas pu être archivé", 'error', 3000, true);
      }
    }
  };
</script>

<ItemModal onClose={closeModal}>
  {#snippet header()}
    <h2 class="request-item-modal-header" data-testid="request-item-modal-header">
      {item?.title}
    </h2>
  {/snippet}
  {#snippet footer()}
    <ul class="request-item-modal-footer">
      <li>
        <span class="fr-icon-inbox-archive-line"></span>
        <button
          onclick={() => clickOnArchiveRequestItem(item)}
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
</ItemModal>

<style>
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
