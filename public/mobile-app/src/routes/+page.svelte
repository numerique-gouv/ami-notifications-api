<script lang="ts">
import {
  PUBLIC_API_URL,
  PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL,
  PUBLIC_FC_AUTHORIZATION_ENDPOINT,
} from '$env/static/public'
import { onMount } from 'svelte'
import FranceConnectSvgIcon from './FranceConnectSvgIcon.svelte'

let userinfo: Object = $state({})
let isFranceConnected: boolean = $state(false)

onMount(async () => {
  try {
    const response = await fetch(`${PUBLIC_API_URL}/api/v1/userinfo`)

    if (response.status == 200) {
      isFranceConnected = true
      const userData = await response.json()
      userinfo = userData

      console.log(userData)
    }
  } catch (error) {
    console.error(error)
  }
})

// FC - Step 3
const franceConnect = async () => {
  const STATE = 'not-implemented-yet-and-has-more-than-32-chars'
  const NONCE = 'not-implemented-yet-and-has-more-than-32-chars'

  const query = {
    scope:
      'openid given_name family_name preferred_username birthdate gender birthplace birthcountry sub email given_name_array',
    redirect_uri: PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL,
    response_type: 'code',
    client_id: PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID,
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
          onclick={franceConnect}
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
  <h1>Bonjour { userinfo.given_name }</h1>

  <ul>
    <li>userinfo: <pre>{ JSON.stringify(userinfo, null, 2) }</pre></li>
    <li>sub: { userinfo.sub }</li>
    <li>given_name: { userinfo.given_name }</li>
    <li>given_name_array: { userinfo.given_name_array }</li>
    <li>family_name: { userinfo.family_name }</li>
    <li>birthdate: { userinfo.birthdate }</li>
    <li>gender: { userinfo.gender }</li>
    <li>birthplace: { userinfo.birthplace }</li>
    <li>birthcountry: { userinfo.birthcountry }</li>
    <li>email: { userinfo.email }</li>
    <li>aud: { userinfo.aud }</li>
    <li>exp: { userinfo.exp }</li>
    <li>iat: { userinfo.iat }</li>
    <li>iss: { userinfo.iss }</li>
  </ul>
{/if}
</div>

<style>
  .homepage {
		margin: 24px 16px;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

	.homepage-not-connected {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
	}

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
	}

  .fr-connect {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  h1 {
    font-weight: 700;
    font-size: 28px;
    line-height: 36px;
  }
</style>
