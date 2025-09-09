<script lang="ts">
import ConnectedHomepage from '$lib/ConnectedHomepage.svelte'
import {
  PUBLIC_FC_AMI_CLIENT_ID,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_AMI_REDIRECT_URL,
  PUBLIC_FC_AUTHORIZATION_ENDPOINT,
} from '$env/static/public'
import { onMount } from 'svelte'
import { globalState } from '$lib/state.svelte.ts'
import { page } from '$app/state'

let isFranceConnected: boolean = $state(false)

onMount(async () => {
  // TODO: check if isFranceConnected depending on the localStorage content
  // isFranceConnected = localStorage.getItem("access_token", false);
  try {
    if (page.url.searchParams.has('is_logged_in')) {
      isFranceConnected = true
      console.log(page.url.searchParams)
      localStorage.setItem(
        'access_token',
        page.url.searchParams.get('access_token') || ''
      )
      localStorage.setItem('expires_in', page.url.searchParams.get('expires_in') || '')
      localStorage.setItem('id_token', page.url.searchParams.get('id_token') || '')
      localStorage.setItem('scope', page.url.searchParams.get('scope') || '')
      localStorage.setItem('token_type', page.url.searchParams.get('token_type') || '')
      localStorage.setItem(
        'is_logged_in',
        page.url.searchParams.get('is_logged_in') || ''
      )
    }
  } catch (error) {
    console.error(error)
  }
})

// FC - Step 3
const franceConnectLogin = async () => {
  const STATE = 'not-implemented-yet-and-has-more-than-32-chars'
  const NONCE = 'not-implemented-yet-and-has-more-than-32-chars'

  const query = {
    scope:
      'openid given_name family_name preferred_username birthdate gender birthplace birthcountry sub email given_name_array',
    redirect_uri: PUBLIC_FC_AMI_REDIRECT_URL,
    response_type: 'code',
    client_id: PUBLIC_FC_AMI_CLIENT_ID,
    state: STATE,
    nonce: NONCE,
    acr_values: 'eidas1',
    prompt: 'login',
  }

  const url = `${PUBLIC_FC_BASE_URL}${PUBLIC_FC_AUTHORIZATION_ENDPOINT}`
  const params = new URLSearchParams(query).toString()

  window.location.href = `${url}?${params}`

  return Response.redirect(`${url}?${params}`)
}
</script>

<div class="homepage">
{#if globalState.isLoggedOut}
  <div class="fr-notice fr-notice--info">
    <div class="fr-container">
      <div class="fr-notice__body">
        <p>
          <span class="fr-notice__title">Vous avez été déconnecté</span>
        </p>
      </div>
    </div>
  </div>
{/if}
{#if !isFranceConnected}
  <div class="homepage-not-connected">
    <div class="france-connect-svg-icon">
      <img src="/dsfr-v1.14.0/artwork/pictograms/digital/application.svg" alt="Icône de notification" />
    </div>

    <div class="france-connect-text">
      <p>Pour pouvoir accéder à <strong>vos droits, à des conseils, et aux échéances</strong> liées à votre situation personnelle, veuillez vous connecter via <strong>France Connect</strong>.</p>
    </div>

    <div class="fr-connect-group">
      <button
          class="fr-connect"
          type="button"
          id="fr-connect-button"
          onclick={franceConnectLogin}
      >
        <span class="fr-connect__login">S’identifier avec</span>
        <span class="fr-connect__brand">FranceConnect</span>
      </button>
      <p>
        <a href="https://franceconnect.gouv.fr/" target="_blank" rel="noopener" title="Qu’est-ce que FranceConnect ? - nouvelle fenêtre">Qu’est-ce que FranceConnect ?</a>
      </p>
    </div>
  </div>
{:else}
  <ConnectedHomepage />
{/if}
</div>

<style>
  .homepage {
    margin: 24px 16px;
    display: flex;
    flex-direction: column;
    min-height: 100vh;

    .homepage-not-connected {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;

      .france-connect-svg-icon {
        margin-bottom: 16px;
      }

      .france-connect-text {
        margin-bottom: 40px;
      }

      .fr-connect-group {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;

        .fr-connect {
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
        }
      }
    }
  }
</style>
