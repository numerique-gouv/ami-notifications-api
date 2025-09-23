<script lang="ts">
import { PUBLIC_API_URL } from '$env/static/public'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'

let isFranceConnected: boolean = $state(false)
onMount(async () => {
  isFranceConnected = !!localStorage.getItem('access_token')
  if (!isFranceConnected) {
    goto('/')
  }
})

const detail = {
  id: '1',
  when: '2 août 2025 à 15H15',
  who: 'France Travail',
  where: 'dans votre Agence France Travail Paris 18e Ney',
}
</script>

<nav class="fr-py-6v fr-px-4v">
  <div class="back-link fr-mb-6v">
    <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </a>
  </div>
  <div class="title">
    <h3 class="fr-mb-0">Rendez-vous {detail.where}</h3>
  </div>
</nav>

<div class="detail">
  <h2>Quand&nbsp;?</h2>
  <p>{detail.when}</p>

  <h2>Comment m'y rendre&nbsp;?</h2>
  <p>{detail.where}</p>

  <h2>Rappel</h2>
  <p>48h avant</p>

  <h2>Préparer mon rdv / pièces à fournir&nbsp;:</h2>
  <ul>
    <li>lorem ipsum</li>
    <li>dolor amet</li>
    <li>molestie euismod</li>
  </ul>
</div>
<div class="actions">
  <a
    href="{PUBLIC_API_URL}/rvo/detail/1"
    title="annulez votre rendez-vous"
    class="fr-btn fr-btn--lg fr-btn--secondary"
  >Annulez le RDV</a>
</div>

<style>
  nav {
    background-color: var(--artwork-decorative-blue-france);
    border-bottom: 4px solid var(--border-plain-blue-france);
  }
  nav .back-link {
    color: var(--text-active-blue-france);
  }
  nav .back-link a {
    text-decoration: none;
    --underline-img: none;
  }
  nav .title {
    display: flex;
  }
  .detail,
  .actions {
    padding: 24px 16px;
  }
  .actions a {
    display: inline-block;
    text-align: center;
    width: 100%;
  }
</style>
