<script lang="ts">
import Navigation from '$lib/Navigation.svelte'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'
import { buildAgenda } from '$lib/agenda'
import type { Agenda } from '$lib/agenda'
import AgendaItem from '$lib/AgendaItem.svelte'
import Icon from '$lib/Icon.svelte'
import accountSvg from '@gouvfr/dsfr/dist/icons/user/account-circle-line.svg'
import { userStore } from '$lib/state/User.svelte'

onMount(async () => {
  if (!userStore.isConnected()) {
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
    <h2 class="fr-mb-0">Mon profil</h2>
  </div>
</nav>

{#if userStore.connected}
<div class="fr-m-4v profile-content-container">
  <div class="fr-card fr-enlarge-link">
    <div class="fr-card__body">
      <div class="fr-card__content">
        <h3 class="fr-card__title">
          <Icon className="fr-mr-2v" href="/remixicons/account-circle-line.svg" />
          Mon identité
        </h3>
        <p class="fr-card__desc ">
          Vous êtes:<br />
          <b>{userStore.connected.identity.given_name},</b><br />
          née <b>{userStore.connected.identity.family_name}</b>
          le <b>{userStore.connected.identity.birthdate}</b>
          à <b>{userStore.connected.identity.birthplace} ({userStore.connected.pivot.birthplace.toString().slice(0,2)}) {userStore.connected.identity.birthcountry}</b><br />
          <span class="fr-text--xs">Informations fournies par FranceConnect</span>
        </p>
        <p class="fr-card__desc ">
          <button type="button" class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary">Modifier</button>
        </p>
      </div>
    </div>
  </div>
</div>
{/if}

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
    }
  }
  .profile-content-container {
    .fr-card__title {
      align-items: center;
      display: flex;
      flex-direction: row;
      a {
        color: var(--text-default-grey);
      }
    }
  }
</style>
