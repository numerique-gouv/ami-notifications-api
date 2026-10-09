<script lang="ts">
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import {
    buildFollowup,
    type Followup,
    type FollowupItem as FollowupItemType,
  } from '$lib/followup';
  import { toastStore } from '$lib/state/toast.svelte';

  interface Props {
    item: FollowupItemType | null;
    followup: Followup | null;
    isFollowupEmpty: boolean;
  }
  let {
    item = $bindable(),
    followup = $bindable(),
    isFollowupEmpty = $bindable(),
  }: Props = $props();

  const refreshFollowup = () => {
    buildFollowup().then((result) => {
      followup = result;
      isFollowupEmpty = followup.isEmpty();
    });
  };

  const clickOnArchiveFollowupItem = async (item: FollowupItemType | null) => {
    if (item) {
      const result = await item.archive();
      if (result === true) {
        if (followup) {
          refreshFollowup();
        }
        toastStore.addToast('L’élément a bien été archivé', 'success', 3000, true);
      } else {
        toastStore.addToast("L’élément n'a pas pu être archivé", 'error', 3000, true);
      }
    }
  };
</script>

<BottomModal modalId="followup-item-{item?.id}-modal">
  {#snippet modalContent()}
    <h2 class="followup-item-modal-header" data-testid="followup-item-modal-header">
      {item?.title}
    </h2>
    <ul class="followup-item-modal-footer">
      <li>
        <span class="fr-icon-inbox-archive-line"></span>
        <button
          onclick={() => clickOnArchiveFollowupItem(item)}
          title="Archiver l'élément {item?.title}"
          aria-label="Archiver l'élément {item?.title}"
          data-testid="archive-followup-item-button-{item?.id}"
          class="archive-followup-item"
        >
          Archiver
        </button>
      </li>
    </ul>
  {/snippet}
</BottomModal>

<style>
  h2.followup-item-modal-header {
    font-size: 1.25rem;
  }
  ul.followup-item-modal-footer {
    padding: 0 0 1rem 0;
    margin: 0;
    li {
      list-style: none;
    }
  }
</style>
