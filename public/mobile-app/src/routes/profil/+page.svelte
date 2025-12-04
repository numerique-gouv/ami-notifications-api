<script lang="ts">
import Navigation from '$lib/Navigation.svelte'
import { onMount } from 'svelte'
import { goto } from '$app/navigation'
import { buildAgenda } from '$lib/agenda'
import type { Agenda } from '$lib/agenda'
import AgendaItem from '$lib/AgendaItem.svelte'
import Card from '$lib/components/Card.svelte'
import type { UserInfo } from '$lib/france-connect'
import accountSvg from '@gouvfr/dsfr/dist/icons/user/account-circle-line.svg'

type ParsedUserInfo = {
  gender: string
  birthdate: string
  birthcountry?: string
  birthplace?: string
  given_name: string
  family_name: string
  preferred_username?: string | null
  email: string
}

let isFranceConnected: boolean = $state(false)
let userinfo: UserInfo | null = $state(null)
let parsedUserinfo: ParsedUserInfo | null = $state(null)

onMount(async () => {
  isFranceConnected = !!localStorage.getItem('access_token')
  if (!isFranceConnected) {
    goto('/')
  }

  const storedUserinfo = localStorage.getItem('userinfo')
  if (storedUserinfo) {
    userinfo = JSON.parse(storedUserinfo)
    console.log($state.snapshot(userinfo))

    if (userinfo) {
      parsedUserinfo = fromUserinfo(userinfo)
      console.log($state.snapshot(parsedUserinfo))

      const storedParsedUserinfo = localStorage.getItem('parsedUserinfo')
      if (storedParsedUserinfo) {
        parsedUserinfo = JSON.parse(storedParsedUserinfo)
      }

      if (parsedUserinfo) {
        await updateParsedUserinfo(parsedUserinfo, userinfo)
        localStorage.setItem('parsedUserinfo', JSON.stringify(parsedUserinfo))
      }
    }
  }
})

const fromUserinfo = (userinfo: UserInfo): ParsedUserInfo => {
  return {
    gender: userinfo.gender,
    birthdate: userinfo.birthdate,
    given_name: userinfo.given_name,
    family_name: userinfo.family_name,
    preferred_username: userinfo.preferred_username,
    email: userinfo.email,
  }
}

const updateParsedUserinfo = async (
  parsedUserinfo: ParsedUserInfo,
  userinfo: UserInfo
) => {
  if (userinfo.birthplace) {
    const birthplaceResponse = await fetch(
      `https://geo.api.gouv.fr/communes/${userinfo.birthplace}?fields=nom&format=json`
    )
    const birthplaceJson = await birthplaceResponse.json()
    const birthplace = `${birthplaceJson.nom} (${userinfo.birthplace.toString().slice(0, 2)})`
    parsedUserinfo.birthplace = birthplace
  }
  if (userinfo.birthcountry) {
    const birthcountryResponse = await fetch(
      `https://tabular-api.data.gouv.fr/api/resources/3580bf65-1d11-4574-a2ca-903d64ad41bd/data/?page=1&page_size=20&COG__exact=${userinfo.birthcountry}`
    )
    const birthcountryJson = await birthcountryResponse.json()
    const birthcountry = birthcountryJson?.data[0]?.LIBCOG
    parsedUserinfo.birthcountry = birthcountry
  }
}
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

{#if parsedUserinfo}
<div class="fr-m-4v profile-content-container">
  <Card iconHref="/remixicons/account-circle-line.svg" title="Mon identité">
      Vous êtes&nbsp;:<br />
      <b>{parsedUserinfo.given_name} {parsedUserinfo.preferred_username || parsedUserinfo.family_name},</b><br />
      né{#if parsedUserinfo.gender == "female"}e{/if}{#if parsedUserinfo.preferred_username} <b>{parsedUserinfo.family_name}</b>{/if}
      le <b>{parsedUserinfo.birthdate}</b>
      {#if parsedUserinfo.birthplace}à <b>{parsedUserinfo.birthplace} {parsedUserinfo.birthcountry}</b><br />{/if} 
      <span class="fr-text--xs">Informations fournies par FranceConnect</span><br />
      <br />
      <button type="button" class="fr-btn fr-icon-edit-line fr-btn--icon-left fr-btn--tertiary">Modifier</button>
  </Card>

  <Card iconHref="/remixicons/mail-line.svg" title="Contact">
    Pour vous contacter&nbsp;:<br />
    <b>{userinfo?.email}</b><br />
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
