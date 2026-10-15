<script lang="ts">
  import { type Agenda, buildAgenda, Item } from '$lib/agenda';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import { ariaHideDecorativeEmoji, removeDecorativeEmoji } from '$lib/emoji';
  import { toastStore } from '$lib/state/toast.svelte';

  interface Props {
    item: Item;
    agenda: Agenda | null;
  }
  let { item, agenda = $bindable() }: Props = $props();

  const refreshAgenda = () => {
    buildAgenda().then((result) => {
      agenda = result;
    });
  };

  const clickOnHideAgendaItem = (item: Item) => {
    item.hide();
    if (agenda) {
      refreshAgenda();
    }
    toastStore.addToast('L’élément a bien été supprimé', 'success', 3000, true);
  };
</script>

<BottomModal modalId="agenda-item-{item.key}-modal">
  {#snippet modalContent()}
    <h2
      id="agenda-item-{item.key}-modal-title"
      class="fr-h5 fr-mb-3v agenda-item-modal-header"
      data-testid="agenda-item-modal-header"
    >
      {@html ariaHideDecorativeEmoji(item.title)}
    </h2>
    <ul class="fr-raw-list agenda-item-modal-footer">
      <li>
        <button
          onclick={() => clickOnHideAgendaItem(item)}
          aria-controls="agenda-item-{item.key}-modal"
          aria-label="Masquer l’élément de l’agenda { removeDecorativeEmoji(item.title)}"
          data-testid="agenda-item-{item.key}-hide-button"
          class="fr-btn fr-btn--lg fr-p-0 fr-btn--tertiary-no-outline fr-icon-eye-off-line fr-btn--icon-left fr-text--md fr-text-title--grey hide-agenda-item"
        >
          Masquer
        </button>
      </li>
    </ul>
  {/snippet}
</BottomModal>
