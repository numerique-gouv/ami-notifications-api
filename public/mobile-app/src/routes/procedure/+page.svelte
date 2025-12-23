<script lang="ts">
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { PUBLIC_OTV_URL } from '$env/static/public'
  import { userStore } from '$lib/state/User.svelte'

  const otvUrl = PUBLIC_OTV_URL
  let itemDate: string = $state('')

  const isValidDate = (d: Date | number) =>
    d instanceof Date && !Number.isNaN(d.getTime())

  onMount(async () => {
    if (!userStore.connected) {
      goto('/')
    }

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

  const navigateToPreviousPage = async () => {
    window.history.back()
  }
</script>

<div class="procedure">
  <nav>
    <div class="back-button-wrapper">
      <button onclick={navigateToPreviousPage}
              title="Retour à la page précédente"
              aria-label="Retour à la page précédente"
              data-testid="back-button"
      >
        <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
      </button>
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
      <p><b>Vous serez prévenu</b> en cas d'anomalies (dégradations, cambriolage...).</p>
    </div>
  </div>

  <div class="procedure-action-buttons">
    <div class="procedure-start">
      <a href="{otvUrl}">
        Commencer la démarche
      </a>
    </div>
  </div>
</div>

<style>
  .procedure {
    nav {
      padding: 1.5rem 1rem;
      background-color: var(--green-archipel-975-75);
      border-bottom: .25rem solid var(--green-archipel-sun-391-moon-716);

      .back-button-wrapper {
        margin-bottom: .5rem;
        color: var(--text-active-blue-france);
        button {
          padding: 0;
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
      background-color: var(--grey-1000-50);

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
    }
  }
</style>
