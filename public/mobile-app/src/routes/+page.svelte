<script lang="ts">
import ConnectedHomepage from '$lib/ConnectedHomepage.svelte'
import Navigation from '$lib/Navigation.svelte'
import {
  PUBLIC_API_URL,
  PUBLIC_FC_AMI_CLIENT_ID,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_AMI_REDIRECT_URL,
  PUBLIC_FC_AUTHORIZATION_ENDPOINT,
} from '$env/static/public'
import { onMount } from 'svelte'
import { page } from '$app/state'
import { goto } from '$app/navigation'
import applicationSvg from '@gouvfr/dsfr/dist/artwork/pictograms/digital/application.svg'

let isFranceConnected: boolean = $state(false)
let isLoggedOut: boolean = $state(false)

onMount(async () => {
  isFranceConnected = !!localStorage.getItem('access_token')
  try {
    if (page.url.searchParams.has('is_logged_in')) {
      const access_token = page.url.searchParams.get('access_token') || ''
      const token_type = page.url.searchParams.get('token_type') || ''
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('expires_in', page.url.searchParams.get('expires_in') || '')
      localStorage.setItem('id_token', page.url.searchParams.get('id_token') || '')
      localStorage.setItem('scope', page.url.searchParams.get('scope') || '')
      localStorage.setItem('token_type', token_type)
      localStorage.setItem(
        'is_logged_in',
        page.url.searchParams.get('is_logged_in') || ''
      )
      const userinfo_endpoint_headers = {
        Authorization: `${token_type} ${access_token}`,
      }
      const response = await fetch(`${PUBLIC_API_URL}/fc_userinfo`, {
        headers: userinfo_endpoint_headers,
      })
      const result = await response.json()
      localStorage.setItem('user_data', result.user_data)
      localStorage.setItem('user_id', result.user_id)
      isFranceConnected = true
      goto('/')
    }
    if (page.url.searchParams.has('is_logged_out')) {
      localStorage.clear()
      isFranceConnected = false
      isLoggedOut = true
      goto('/')
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
    scope: 'openid identite_pivot preferred_username email cnaf_quotient_familial',
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
}

function dismissNotice() {
  isLoggedOut = false
}
</script>

<div class="homepage">
{#if !isFranceConnected}
  <div class="homepage-not-connected">
    {#if isLoggedOut}
      <div class="logout-notice fr-py-3v fr-px-4v">
        <div class="container-left">
          <img src="/icons/fr--success-line-green.svg" class="fr-mr-2v" alt="Icône de succès" />
          <span>Vous avez bien été déconnecté</span>
        </div>
        <div class="container-right">
          <button onclick="{dismissNotice}" title="Masquer le message" aria-label="Masquer le message" type="button" class="fr-btn--close fr-btn"></button>
        </div>
       </div>
    {/if}
    <div class="france-connect-svg-icon">
      <img src="{applicationSvg}" alt="Icône de notification" />
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
  <Navigation />
  <ConnectedHomepage />
{/if}
</div>

<style>
  .homepage {
    display: flex;
    flex-direction: column;
    min-height: 100vh;

    .homepage-not-connected {
      position: relative;
      margin: 24px 16px;

      .logout-notice {
        position: absolute;
        width: 100%;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        background-color: var(--background-flat-grey);
        color: white;
        border-left: 3px solid #58B77D;
        border-radius: 0.25rem;

        .container-left {
          display: flex;
          flex-direction: row;
          align-items: center;

          img {
            width: 1.25rem;
            height: 1.25rem;
          }

          span {
            font-size: 14px;
            font-weight: 500;
          }
        }

        .fr-btn--close {
          color: white;
        }
      }

      .france-connect-svg-icon {
        text-align: center;
        margin-top: 7.5rem;
        margin-bottom: 1rem;
      }

      .france-connect-text {
        margin-bottom: 40px;
      }

      .fr-connect-group {
        text-align: center;
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
