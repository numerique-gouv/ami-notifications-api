<script lang="ts">
  import { type Agenda, buildAgenda, Item } from '$lib/agenda';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import { ariaHideDecorativeEmoji } from '$lib/emoji';
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
      class="agenda-item-modal-header"
      data-testid="agenda-item-modal-header"
    >
      {@html ariaHideDecorativeEmoji(item.title)}
    </h2>
    <ul class="agenda-item-modal-footer">
      <li>
        <button
          onclick={() => clickOnHideAgendaItem(item)}
          aria-controls="agenda-item-{item.key}-modal"
          title="Cacher l’élément de l’agenda {item.title}"
          aria-label="Cacher l’élément de l’agenda {item.title}"
          data-testid="agenda-item-{item.key}-hide-button"
          class="hide-agenda-item"
        >
          Masquer
        </button>
      </li>
    </ul>
  {/snippet}
</BottomModal>

<style>
  h2.agenda-item-modal-header {
    font-size: 1.25rem;
  }
  ul.agenda-item-modal-footer {
    padding: 0 0 1rem 0;
    margin: 0;
    li {
      list-style: none;
    }
  }
</style>
