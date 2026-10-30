<script lang="ts">
  import { onMount } from 'svelte';
  import { PUBLIC_SKELETON_DEBUG_DELAY } from '$env/static/public';
  import { type Agenda, buildAgenda, Item, monthName } from '$lib/agenda';
  import { AMIGoto } from '$lib/ami-navigation';
  import AgendaItem from '$lib/components/AgendaItem.svelte';
  import AgendaItemModal from '$lib/components/modal/AgendaItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let agenda: Agenda | null = $state(null);

  let currentDate = new Date();
  let skeletonCurrentMonths: string[] = [];
  let skeletonFutureMonths: string[] = [];
  skeletonCurrentMonths.push(monthName(currentDate));
  let futureDate = new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000);
  if (futureDate.getMonth() !== currentDate.getMonth()) {
    skeletonCurrentMonths.push(monthName(futureDate));
  }
  futureDate.setDate(1);
  [...Array(6)].forEach(() => {
    futureDate.setMonth((futureDate.getMonth() + 1) % 12);
    skeletonFutureMonths.push(monthName(futureDate));
  });

  const waitForPageData = async () => {
    if (PUBLIC_SKELETON_DEBUG_DELAY) {
      await new Promise((resolve) => {
        setTimeout(() => resolve(0), parseFloat(PUBLIC_SKELETON_DEBUG_DELAY));
      });
    }
    agenda = await buildAgenda();
  };

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
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

  {#await waitForPageData()}
    <div class="skeleton">
      <div class="agenda--events fr-mb-3w">
        <div class="agenda--events--header">
          <h2 class="fr-h6 fr-mb-0 am-text--smbold">Prochainement</h2>
        </div>
        <div class="agenda--events--container current">
          {#each skeletonCurrentMonths as skeletonMonth}
            <p
              class="fr-text--sm fr-mb-0 fr-text-title--grey am-text--smbold agenda--events--month"
            >
              {skeletonMonth}
            </p>
            <div class="agenda--events--container">
              <div class="agenda--item">
                <div class="agenda--item--date">
                  <div class="line"></div>
                  <div class="line"></div>
                </div>
                <div class="agenda--item--container fr-card fr-card--sm">
                  <div class="tag"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
      <div class="agenda--events">
        <div class="agenda--events--header">
          <h2 class="fr-h6 fr-mb-0 am-text--smbold">Les mois suivants</h2>
        </div>
        <div class="agenda--events--container future">
          {#each skeletonFutureMonths as skeletonMonth}
            <p
              class="fr-text--sm fr-mb-0 fr-text-title--grey am-text--smbold agenda--events--month"
            >
              {skeletonMonth}
            </p>
            <div class="agenda--events--container">
              <div class="agenda--item">
                <div class="agenda--item--date">
                  <div class="line"></div>
                  <div class="line"></div>
                </div>
                <div class="agenda--item--container fr-card fr-card--sm">
                  <div class="tag"></div>
                  <div class="line"></div>
                  <div class="line"></div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {:then pageDataLoaded}
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
  {/await}
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

  .skeleton {
    --border-default-grey: #e5e5e5;
    .agenda--item {
      display: flex;
      position: relative;
      padding: 0.5rem 0;
      .agenda--item--date {
        display: flex;
        flex-direction: column;
        width: 2rem;
        margin-right: 1rem;
      }
      .agenda--item--container {
        flex: 1;
        padding: 0.875rem 2rem 0.875rem 1rem;
      }

      .tag {
        background: #ececfe;
        height: 1.2rem;
        width: 70%;
        margin-bottom: 0.5rem;
      }
      .line {
        background: #f5f5fe;
        margin-bottom: 0.5rem;
        height: 1.2rem;
        &.short {
          width: 70%;
        }
      }
    }
  }
</style>
