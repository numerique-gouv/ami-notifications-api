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
</script>

<nav class="fr-p-4v fr-pt-6v">
  <div class="back-link fr-mb-2v">
    <a href="/" title="Retour à la page d'accueil" aria-label="Retour à la page d'accueil">
      <span aria-hidden="true" class="fr-icon-arrow-left-line"></span>
    </a>
  </div>
  <div class="title">
    <h2 class="fr-mb-0">Notifications</h2>
    <div class="settings-svg-icon fr-pt-1v">
      <img src="/remixicons/settings.svg" alt="Icône de paramétrage" class="fr-mr-2v" />
    </div>
  </div>
</nav>

<style>
  nav {
    .back-link {
      color: var(--text-active-blue-france);
      a {
        text-decoration: none;
        --underline-img: none;
      }
    }
    .title {
      display: flex;
      h2 {
        flex-grow: 1;
      }
      .settings-svg-icon {
        color: var(--text-active-blue-france);
        img {
          width: 20px;
          height: 20px;
        }
      }
    }
  }
</style>
