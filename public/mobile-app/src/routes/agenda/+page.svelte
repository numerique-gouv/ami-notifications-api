<script lang="ts">
import Navigation from '$lib/Navigation.svelte'
import { onMount } from 'svelte'

let isFranceConnected: boolean = $state(false)

onMount(async () => {
  isFranceConnected = !!localStorage.getItem('access_token')
  if (!isFranceConnected) {
    goto('/')
  }
})
</script>

<div class="agenda">
  <div class="agenda--title">
    <h2>Mon agenda</h2>
    <div class="agenda--title--icon">
      <span class="fr-icon-search-line" aria-hidden="true"></span>
    </div>
  </div>

  <div class="agenda--events">
    <div class="agenda--events--header">
      <span class="title">Ce mois-ci</span>
    </div>
    <div class="agenda--events--container">
      <div class="agenda--event">
        <div class="agenda--event--date">
          <span class="day-name">sam</span> 
          <span class="day-num">20</span> 
        </div>
        <div class="agenda--event--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
          <div class="fr-tile__body">
            <div class="fr-tile__content">
              <h3 class="fr-tile__title">
                <a href="/#/agenda/">Vacances de Noël 🎄</a>
              </h3>
              <div class="fr-tile__start">
                <p class="fr-badge">
                  <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                  Vacances et jours fériés
                </p>
                <p class="fr-tag">
                  Du 20 décembre au 5 janvier
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="agenda--events">
    <div class="agenda--events--header">
      <span class="title">Prochainement</span>
    </div>
    <div class="agenda--events--container">
      <div class="agenda--event">
        <div class="agenda--event--date">
          <span class="day-name">sam</span> 
          <span class="day-num">7</span> 
        </div>
        <div class="agenda--event--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
          <div class="fr-tile__body">
            <div class="fr-tile__content">
              <h3 class="fr-tile__title">
                <a href="/#/agenda/">Vacances d’hiver Zone A ❄️</a>
              </h3>
              <div class="fr-tile__start">
                <p class="fr-badge">
                  <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                  Vacances et jours fériés
                </p>
                <p class="fr-tag">
                  Du 7 au 23 février 2026
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="agenda--event">
        <div class="agenda--event--date">
          <span class="day-name">sam</span> 
          <span class="day-num">14</span> 
        </div>
        <div class="agenda--event--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link">
          <div class="fr-tile__body">
            <div class="fr-tile__content">
              <h3 class="fr-tile__title">
                <a href="/#/agenda/">Vacances d’hiver Zone B ❄️</a>
              </h3>
              <div class="fr-tile__start">
                <p class="fr-badge">
                  <img src="/remixicons/calendar-event-line.svg" alt="Icône de calendrier" />
                  Vacances et jours fériés
                </p>
                <p class="fr-tag">
                  Du 14 février au 2 mars 2026
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
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
        margin-bottom: 1.5rem;
        .title {
          font-weight: 500;
          color: #000;
        }
      }
      .agenda--events--container {
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
            margin-bottom: 1.5rem;
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
