<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { type Agenda, buildAgenda, Item } from '$lib/agenda';
  import AgendaItem from '$lib/components/AgendaItem.svelte';
  import AgendaItemModal from '$lib/components/modal/AgendaItemModal.svelte';
  import Modal from '$lib/components/modal/Modal.svelte';
  import ZonePreferences from '$lib/components/modal/ZonePreferences.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  type ModalInstance = {
    open: () => Promise<void>;
  };

  let agenda: Agenda | null = $state(null);
  let zonePreferencesModal: ModalInstance;
  let selectedAgendaItem: Item | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }

    agenda = await buildAgenda();
    console.log($state.snapshot(agenda));
  });

  const openZonePreferencesModal = () => {
    zonePreferencesModal.open();
  };

  const refreshAgenda = () => {
    buildAgenda().then((result) => {
      agenda = result;
    });
  };

  const openAgendaItemModal = (item: Item) => {
    selectedAgendaItem = item;
  };
</script>

<div class="agenda">
  <div class="agenda--title fr-mb-1w">
    <h1 class="fr-h2 fr-mb-0">Mon agenda</h1>
    <div class="agenda--title--icon">
      <button class="preferences" type="button" onclick={openZonePreferencesModal}>
        <span class="fr-icon-settings-5-line" aria-hidden="true"></span><span
          class="fr-sr-only"
          >Préférences</span
        >
      </button>
    </div>
  </div>

  {#if agenda && agenda.now.length}
    <div class="agenda--events fr-mb-3w" data-testid="events-now">
      <div class="agenda--events--header">
        <h2 class="fr-h6 fr-mb-3v am-text--smbold">Prochainement</h2>
      </div>
      <div class="agenda--events--container">
        {#each agenda.now as item, i}
          {#if i == 0 || i > 0 && item.date?.getMonth() !== agenda.now[i - 1].date?.getMonth()}
            <h3 class="fr-text--sm fr-mb-1w am-text--smbold agenda--events--month">
              {item.monthName}
            </h3>
          {/if}
          <AgendaItem item={item} onOpen={() => openAgendaItemModal(item)} />
        {/each}
      </div>
    </div>
  {/if}

  {#if agenda && agenda.next.length}
    <div class="agenda--events" data-testid="events-next">
      <div class="agenda--events--header">
        <h2 class="fr-h6 fr-mb-3v am-text--smbold">Les mois suivants</h2>
      </div>
      <div class="agenda--events--container">
        {#each agenda.next as item, i}
          {#if i > 0 && item.date?.getMonth() !== agenda.next[i - 1].date?.getMonth() || i == 0 && (agenda.now.length && item.date?.getMonth() !== agenda.now[agenda.now.length - 1].date?.getMonth() || !agenda.now.length)}
            <h3 class="fr-text--sm fr-mb-1w am-text--smbold agenda--events--month">
              {item.monthName}
            </h3>
          {/if}
          <AgendaItem item={item} onOpen={() => openAgendaItemModal(item)} />
        {/each}
      </div>
    </div>
  {/if}
</div>
<Navigation currentItem="agenda" />

<Modal
  bind:this={zonePreferencesModal}
  id="modal-zones-preferences"
  title="Zones scolaires"
  onCloseCustom={refreshAgenda}
  component={ZonePreferences}
/>

{#if selectedAgendaItem}
  <AgendaItemModal bind:item={selectedAgendaItem} bind:agenda={agenda} />
{/if}

<style>
  .agenda {
    padding: 1.5rem 1rem;
    margin-bottom: 4.25rem;
    .agenda--title {
      display: flex;
      h1 {
        flex-grow: 1;
      }
      .agenda--title--icon {
        padding-top: 0.25rem;
        color: var(--text-active-blue-france);
      }
    }
  }
</style>
