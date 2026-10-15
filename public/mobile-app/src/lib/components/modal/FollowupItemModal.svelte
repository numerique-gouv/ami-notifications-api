<script lang="ts">
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import { ariaHideDecorativeEmoji, removeDecorativeEmoji } from '$lib/emoji';
  import {
    buildFollowup,
    type Followup,
    type FollowupItem as FollowupItemType,
  } from '$lib/followup';
  import { toastStore } from '$lib/state/toast.svelte';

  interface Props {
    item: FollowupItemType;
    followup: Followup | null;
    isFollowupEmpty: boolean;
  }
  let { item, followup = $bindable(), isFollowupEmpty = $bindable() }: Props = $props();

  const refreshFollowup = () => {
    buildFollowup().then((result) => {
      followup = result;
      isFollowupEmpty = followup.isEmpty();
    });
  };

  const clickOnArchiveFollowupItem = async (item: FollowupItemType) => {
    const result = await item.archive();
    if (result === true) {
      if (followup) {
        refreshFollowup();
      }
      toastStore.addToast('L’élément a bien été archivé', 'success', 3000, true);
    } else {
      toastStore.addToast("L’élément n'a pas pu être archivé", 'error', 3000, true);
    }
  };
</script>

<BottomModal modalId="followup-item-{item.id}-modal">
  {#snippet modalContent()}
    <h2
      id="followup-item-{item.id}-modal-title"
      class="fr-h5 fr-mb-3v followup-item-modal-header"
      data-testid="followup-item-modal-header"
    >
      {@html ariaHideDecorativeEmoji(item.title)}
    </h2>
    <ul class="fr-raw-list followup-item-modal-footer">
      <li>
        <button
          onclick={() => clickOnArchiveFollowupItem(item)}
          aria-controls="followup-item-{item.id}-modal"
          aria-label="Archiver l'élément {removeDecorativeEmoji(item.title)}"
          data-testid="followup-item-{item.id}-archive-button"
          class="fr-btn fr-btn--lg fr-p-0 fr-btn--tertiary-no-outline fr-icon-inbox-archive-line fr-btn--icon-left fr-text--md fr-text-title--grey archive-followup-item"
        >
          Archiver
        </button>
      </li>
    </ul>
  {/snippet}
</BottomModal>
