<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import AgendaItem from '$lib/AgendaItem.svelte'
  import type { Agenda } from '$lib/agenda'
  import { buildAgenda } from '$lib/agenda'
  import Navigation from '$lib/Navigation.svelte'
  import { userStore } from '$lib/state/User.svelte'

  let agenda: Agenda | null = $state(null)

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
    }

    agenda = await buildAgenda()
    console.log($state.snapshot(agenda))
  })
</script>

<div class="agenda">
  <div class="agenda--title">
    <h2>Mon agenda</h2>
    <div class="agenda--title--icon">
      <span class="fr-icon-search-line" aria-hidden="true"></span>
    </div>
  </div>

  {#if agenda && agenda.now.length}
    <div class="agenda--events" data-testid="events-now">
      <div class="agenda--events--header"><span class="title">Prochainement</span></div>
      <div class="agenda--events--container">
        {#each agenda.now as item, i}
          {#if i == 0 || i > 0 && item.date?.getMonth() !== agenda.now[i - 1].date?.getMonth()}
            <div class="agenda--events--month">{item.monthName}</div>
          {/if}
          <AgendaItem item={item} />
        {/each}
      </div>
    </div>
  {/if}

  {#if agenda && agenda.next.length}
    <div class="agenda--events" data-testid="events-next">
      <div class="agenda--events--header">
        <span class="title">Les mois suivants</span>
      </div>
      <div class="agenda--events--container">
        {#each agenda.next as item, i}
          {#if i > 0 && item.date?.getMonth() !== agenda.next[i - 1].date?.getMonth() || i == 0 && (agenda.now.length && item.date?.getMonth() !== agenda.now[agenda.now.length - 1].date?.getMonth() || !agenda.now.length)}
            <div class="agenda--events--month">{item.monthName}</div>
          {/if}
          <AgendaItem item={item} />
        {/each}
      </div>
    </div>
  {/if}
</div>
<Navigation currentItem="agenda" />

<style>
  .agenda {
    padding: 1.5rem 1rem;
    margin-bottom: 68px;
    .agenda--title {
      display: flex;
      h2 {
        flex-grow: 1;
        margin-bottom: 0.5rem;
      }
      .agenda--title--icon {
        padding-top: 0.25rem;
        color: var(--text-active-blue-france);
      }
    }
    .agenda--events {
      .agenda--events--header {
        margin-bottom: 0.75rem;
        .title {
          font-weight: 500;
          color: #000;
        }
      }
      .agenda--events--container {
        .agenda--events--month {
          font-weight: 500;
          color: #000;
          font-size: 14px;
          margin-bottom: 0.5rem;
        }
      }
    }
  }
</style>
