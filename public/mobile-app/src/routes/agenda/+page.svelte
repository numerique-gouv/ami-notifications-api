<script lang="ts">
import Navigation from '$lib/Navigation.svelte'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'
import { dayName, monthName, holidayPeriod, retrieveHolidays } from '$lib/api-holidays'
import type { Holiday } from '$lib/api-holidays'

let isFranceConnected: boolean = $state(false)
let holidays: Object = $state({ now: [] as Holiday[], next: [] as Holiday[] })

onMount(async () => {
  isFranceConnected = !!localStorage.getItem('access_token')
  if (!isFranceConnected) {
    goto('/')
  }

  holidays = await retrieveHolidays()
  console.log($state.snapshot(holidays))
})
</script>

<div class="agenda">
  <div class="agenda--title">
    <h2>Mon agenda</h2>
    <div class="agenda--title--icon">
      <span class="fr-icon-search-line" aria-hidden="true"></span>
    </div>
  </div>

  {#if holidays.now.length}
  <div class="agenda--events" data-testid="events-now">
    <div class="agenda--events--header">
      <span class="title">D'ici un mois</span>
    </div>
    <div class="agenda--events--container">
      {#each holidays.now as holiday, i}
        {#if i == 0 || i > 0 && holiday.start_date.getMonth() !== holidays.now[i - 1].start_date.getMonth()}
        <div class="agenda--events--month">
          {monthName(holiday.start_date)}
        </div>
        {/if}
        <div class="agenda--event">
          <div class="agenda--event--date">
            <span class="day-name">{dayName(holiday.start_date)}</span> 
            <span class="day-num">{holiday.start_date.getDate()}</span> 
          </div>
          <div class="agenda--event--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
            <div class="fr-tile__body">
              <div class="fr-tile__content">
                <h3 class="fr-tile__title">
                  <a href="/#/agenda/">{holiday.description} {holiday.zones} {holiday.emoji}</a>
                </h3>
                <div class="fr-tile__start">
                  <p class="fr-badge">
                    <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                    Vacances et jours fériés
                  </p>
                  <p class="fr-tag">
                    {holidayPeriod(holiday.start_date, holiday.end_date)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
  {/if}

  {#if holidays.next.length}
  <div class="agenda--events" data-testid="events-next">
    <div class="agenda--events--header">
      <span class="title">Prochainement</span>
    </div>
    <div class="agenda--events--container">
      {#each holidays.next as holiday, i}
        {#if i > 0 && holiday.start_date.getMonth() !== holidays.next[i - 1].start_date.getMonth() || i == 0 && (holidays.now.length && holiday.start_date.getMonth() !== holidays.now[holidays.now.length - 1].start_date.getMonth() || !holidays.now.length)}
        <div class="agenda--events--month">
          {monthName(holiday.start_date)}
        </div>
        {/if}
        <div class="agenda--event">
          <div class="agenda--event--date">
            <span class="day-name">{dayName(holiday.start_date)}</span> 
            <span class="day-num">{holiday.start_date.getDate()}</span> 
          </div>
          <div class="agenda--event--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
            <div class="fr-tile__body">
              <div class="fr-tile__content">
                <h3 class="fr-tile__title">
                  <a href="/#/agenda/">{holiday.description} {holiday.zones} {holiday.emoji}</a>
                </h3>
                <div class="fr-tile__start">
                  <p class="fr-badge">
                    <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                    Vacances et jours fériés
                  </p>
                  <p class="fr-tag">
                    {holidayPeriod(holiday.start_date, holiday.end_date)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
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
        .agenda--event {
          display: flex;
          .agenda--event--date {
            width: 2rem;
            color: #000;
            text-align: center;
            margin-right: 1rem;
            .day-name {
              font-size: 12px;
              line-height: 20px;
            }
            .day-num {
              font-size: 16px;
              font-weight: 700;
            }
          }
          .agenda--event--detail {
            margin-bottom: 0.75rem;
            padding: 1.5rem;
            padding-bottom: 1rem;
            width: 100%;
            .fr-tile__content {
              padding-bottom: 1.5rem;
              .fr-tile__title {
                font-size: 16px;
                a::after {
                  bottom: 1.25rem;
                  right: 1.25rem;
                  --icon-size: 1rem;
                }
              }
              .fr-badge {
                font-size: 12px;
                font-weight: 700;
                line-height: 20px;
                color: var(--text-active-blue-france);
                background-color: var(--background-action-low-blue-france);
                margin-bottom: 0.5rem;
                img {
                  width: 12px;
                  margin-right: 4px;
                }
              }
              .fr-tag {
                font-size: 12px;
                line-height: 20px;
                min-height: 0;
                display: block;
              }
            }
          }
        }
      }
    }
  }
</style>
