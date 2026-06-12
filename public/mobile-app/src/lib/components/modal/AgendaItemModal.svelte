<script lang="ts">
  import { type Agenda, buildAgenda, Item } from '$lib/agenda';
  import ItemModal from '$lib/components/modal/ItemModal.svelte';
  import { toastStore } from '$lib/state/toast.svelte';

  interface Props {
    item: Item | null;
    agenda: Agenda | null;
  }
  let { item = $bindable(), agenda = $bindable() }: Props = $props();

  const closeModal = () => {
    item = null;
  };

  const refreshAgenda = () => {
    buildAgenda().then((result) => {
      agenda = result;
    });
  };

  const clickOnHideAgendaItem = (item: Item | null) => {
    if (item) {
      item.hide();
      if (agenda) {
        refreshAgenda();
      }
      closeModal();
      toastStore.addToast("L'élément a bien été supprimé", 'success', 3000, true);
    }
  };
</script>

<ItemModal onClose={closeModal}>
  {#snippet header()}
    <h2 class="agenda-item-modal-header" data-testid="agenda-item-modal-header">
      {item?.title}
    </h2>
  {/snippet}

  {#snippet footer()}
    <ul class="agenda-item-modal-footer">
      <li>
        <span class="fr-icon-delete-line"></span>
        <button
          onclick={() => clickOnHideAgendaItem(item)}
          title="Cacher l'élément de l'agenda"
          aria-label="Cacher l'élément de l'agenda"
          data-testid="hide-agenda-item-button"
          class="hide-agenda-item"
        >
          Supprimer
        </button>
      </li>
    </ul>
  {/snippet}
</ItemModal>

<style>
  h2.agenda-item-modal-header {
    font-size: 1.25rem;
  }
  ul.agenda-item-modal-footer {
    padding: 0;
    margin: 0;
    li {
      list-style: none;
    }
  }
</style>
