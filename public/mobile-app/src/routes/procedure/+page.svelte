<script lang="ts">
import { onMount } from 'svelte'
import { PUBLIC_OTV_URL } from '$env/static/public'

const otvUrl = PUBLIC_OTV_URL
let itemDate: string = $state('')

const isValidDate = (d: Date | number) => d instanceof Date && !isNaN(d.getTime())

onMount(async () => {
  const hash = window.location.hash
  const url = new URL(hash.substring(1), window.location.origin)
  const stringFromUrl = url.searchParams.get('date') || ''
  itemDate = ''

  if (stringFromUrl !== '') {
    const dateFromUrl: Date = new Date(stringFromUrl)
    if (isValidDate(dateFromUrl)) {
      const dayNumber: string = dateFromUrl ? dateFromUrl.getDate().toString() : ''
      const monthName: string = dateFromUrl
        ? dateFromUrl.toLocaleString('fr-FR', { month: 'long' })
        : ''
      itemDate = `${dayNumber} ${monthName}`
    }
  }
})
</script>

<div class="procedure">
  <nav class="fr-p-4v fr-pt-6v">
    <div class="back-link">
      <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
        <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
      </a>
    </div>
    <div class="partner-logo">
      <img src="/icons/otv-logo.svg" alt="Icône du logo du partenaire" />
    </div>
    <div class="title">
      <h2>Opération Tranquillité Vacances</h2>
    </div>
  </nav>

  <div class="procedure-content">
    <div class="procedure-content-block">
      <p class="title">Quand ?</p>
      <p data-testid="item-date">À partir du {itemDate}</p>
    </div>
    <div class="procedure-content-block">
      <p class="title">Comment ça fonctionne ?</p>
      <p>Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'<b>opération tranquillité vacances</b>.</p>
      <p><b>Les services de police ou de gendarmerie se chargent alors de surveiller votre logement.</b> Des patrouilles sont organisées pour passer aux abords de votre domicile.</p>
      <p><b>Vous serez prévenu</b> en cas d'anomalies.</p>
    </div>
  </div>

  <div class="procedure-action-buttons">
    <div class="procedure-start">
      <a href="{otvUrl}">
        Commencer la démarche
      </a>
    </div>
    <div class="procedure-add-agenda">
      <button>
        <span class="fr-icon-calendar-event-fill" aria-hidden="true"></span>
        Ajouter à mon agenda
      </button>
    </div>
  </div>
</div>

<style>
  .procedure {
    nav {
      padding: 1.5rem 1rem;
      background-color: var(--green-archipel-975-75);
      border-bottom: .25rem solid var(--green-archipel-sun-391-moon-716);

      .back-link {
        margin-bottom: .5rem;
        color: var(--text-active-blue-france);
        a {
          text-decoration: none;
          --underline-img: none;
        }
      }
      .partner-logo {
        display: flex;
        justify-content: center;
        margin-bottom: .5rem;
      }
      .title {
        display: flex;
        justify-content: center;
        h2 {
          text-align: center;
          margin-bottom: 0;
          font-size: 1.5rem;
          line-height: 2rem;
        }
      }
    }

    .procedure-content {
      padding: 1.5rem 1rem;

      .procedure-content-block {
        padding-bottom: 1rem;
        p {
          margin-bottom: 1rem;
        }
        .title {
          font-weight: 700;
        }
      }
    }

    .procedure-action-buttons {
      position: fixed;
      bottom: 0;
      left: 50%;
      transform: translateX(-50%);
      padding: 1rem;
      width: 100%;
      background-color: var(--blue-france-975-sun-113);

      .procedure-start {
        height: 3rem;
        margin-bottom: .5rem;
        background-color: var(--text-action-high-blue-france);
        color: var(--text-inverted-blue-france);

        a {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 100%;
          height: 100%;
          text-decoration: none;
          --underline-img: none;
        }
      }
      .procedure-add-agenda {
        display: flex;
        justify-content: center;
        height: 2.5rem;
        .fr-icon-calendar-event-fill {
          padding-right: .5rem;
          &::before {
            width: 1rem;
            color: var(--blue-france-sun-113-625);
          }
        }
      }
    }
  }
</style>
