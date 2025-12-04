<script lang="ts">
import Navigation from '$lib/Navigation.svelte'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'
import { buildAgenda } from '$lib/agenda'
import type { Agenda } from '$lib/agenda'
import AgendaItem from '$lib/AgendaItem.svelte'
import Card from '$lib/components/Card.svelte'
import accountSvg from '@gouvfr/dsfr/dist/icons/user/account-circle-line.svg'
import { userStore } from '$lib/state/User.svelte'

onMount(async () => {
  if (!userStore.isConnected()) {
    goto('/')
  }
})
</script>

<nav class="fr-pb-0 fr-px-4v fr-pt-6v">
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
  <Card iconHref="/remixicons/account-circle-line.svg" title="Mon identité">
    Vous êtes:<br />
    <b>{userStore.connected.identity.given_name},</b><br />
    née <b>{userStore.connected.identity.family_name}</b>
    le <b>{userStore.connected.identity.birthdate}</b>
    à <b>{userStore.connected.identity.birthplace} ({userStore.connected.pivot.birthplace.toString().slice(0,2)}) {userStore.connected.identity.birthcountry}</b><br />
    <span class="fr-text--xs">Informations fournies par FranceConnect</span><br />
    <br />
    <button type="button" class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary">Modifier</button>
  </Card>

  <Card iconHref="/remixicons/mail-line.svg" title="Contact">
    Pour vous contacter&nbsp;:<br />
    <b>{userinfo.email}</b><br />
    <span class="fr-text--xs">Informations fournies par FranceConnect</span><br />
    <br />
    <button type="button" class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary">Modifier</button>
  </Card>

  <Card iconHref="/remixicons/map-pin-user-line.svg" title="Mon adresse">
    <button type="button" class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary">Définir une adresse</button>
  </Card>
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
</style>
