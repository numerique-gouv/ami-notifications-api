<script lang="ts">
  import ItemModal from '$lib/components/modal/ItemModal.svelte';
  import {
    buildFollowup,
    type Followup,
    type RequestItem as RequestItemType,
  } from '$lib/followup';
  import { toastStore } from '$lib/state/toast.svelte';

  interface Props {
    item: RequestItemType | null;
    followup: Followup | null;
    isFollowupEmpty: boolean;
  }
  let {
    item = $bindable(),
    followup = $bindable(),
    isFollowupEmpty = $bindable(),
  }: Props = $props();

  const closeModal = () => {
    item = null;
  };

  const refreshFollowup = () => {
    buildFollowup().then((result) => {
      followup = result;
      isFollowupEmpty = !followup.items.length;
    });
  };

  const clickOnArchiveRequestItem = async (item: RequestItemType | null) => {
    if (item) {
      const result = await item.archive();
      if (result === true) {
        if (followup) {
          refreshFollowup();
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
