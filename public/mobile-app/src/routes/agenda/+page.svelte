<script lang="ts">
  import { onMount } from 'svelte';
  import { type Agenda, buildAgenda, Item } from '$lib/agenda';
  import { AMIGoto } from '$lib/ami-navigation';
  import AgendaItem from '$lib/components/AgendaItem.svelte';
  import AgendaItemModal from '$lib/components/modal/AgendaItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let agenda: Agenda | null = $state(null);

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }

    agenda = await buildAgenda();
    console.log($state.snapshot(agenda));
  });
</script>

<Navigation currentItem="agenda" />
<div class="agenda">
  <div class="agenda--title fr-mb-0">
    <h1 class="fr-h2 fr-mb-0">Mon agenda</h1>
    <div class="agenda--title--icon">
      <button
        class="fr-btn fr-icon-information-line fr-btn--tertiary-no-outline"
        type="button"
        onclick={() => AMIGoto('/#/agenda/themes')}
      >
        Information
      </button>
      <button
        class="fr-btn fr-icon-settings-5-line fr-btn--tertiary-no-outline"
        type="button"
        onclick={()=>AMIGoto("/#/preferences/zones")}
      >
        Préférences
      </button>
    </div>
  </div>

  {#if agenda && agenda.now.length}
    <div class="agenda--events fr-mb-3w" data-testid="events-now">
      <div class="agenda--events--header">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold">Prochainement</h2>
      </div>
      <div class="agenda--events--container">
        {#each agenda.now as item, i}
          {@const displayMonth = (i == 0 || i > 0 && item.date?.getMonth() !== agenda.now[i - 1].date?.getMonth())}
          {@const displayDay = (i == 0 || i > 0 && item.date?.toDateString() !== agenda.now[i - 1].date?.toDateString())}
          {#if displayMonth}
            <p
              class="fr-text--sm fr-mb-0 fr-text-title--grey am-text--smbold agenda--events--month"
            >
              {item.monthName}
            </p>
          {/if}
          <AgendaItem
            item={item}
            displayDay={displayDay}
            hasModal={true}
            index="agenda-now-{i}"
          />
          <AgendaItemModal item={item} bind:agenda={agenda} index="agenda-now-{i}" />
        {/each}
      </div>
    </div>
  {/if}

  {#if agenda && agenda.next.length}
    <div class="agenda--events" data-testid="events-next">
      <div class="agenda--events--header">
        <h2 class="fr-h6 fr-mb-0 am-text--smbold">Les mois suivants</h2>
      </div>
      <div class="agenda--events--container">
        {#each agenda.next as item, i}
          {@const displayMonth = (i > 0 && item.date?.getMonth() !== agenda.next[i - 1].date?.getMonth() || i == 0 && (agenda.now.length && item.date?.getMonth() !== agenda.now[agenda.now.length - 1].date?.getMonth() || !agenda.now.length))}
          {@const displayDay = (i == 0 || i > 0 && item.date?.toDateString() !== agenda.next[i - 1].date?.toDateString())}
          {#if displayMonth}
            <p
              class="fr-text--sm fr-mb-0 fr-text-title--grey am-text--smbold agenda--events--month"
            >
              {item.monthName}
            </p>
          {/if}
          <AgendaItem
            item={item}
            displayDay={displayDay}
            hasModal={true}
            index="agenda-next-{i}"
          />
          <AgendaItemModal item={item} bind:agenda={agenda} index="agenda-next-{i}" />
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .agenda {
    padding: 1.5rem 1rem;
    margin-bottom: 4.25rem;
    .agenda--title {
      display: flex;
      h1 {
        flex-grow: 1;
      }
    }
    /* titles stikcy */
    .agenda--events--month,
    .agenda--events--header {
      position: sticky;
      top: 0;
      padding: 0.5rem 1rem 0.25rem;
      margin: 0 -1rem;
      background-color: var(--background-default-grey);
      z-index: 10;
    }

    .agenda--events--month {
      top: 2.25rem;
      padding-bottom: 0.5rem;
    }
  }
</style>
