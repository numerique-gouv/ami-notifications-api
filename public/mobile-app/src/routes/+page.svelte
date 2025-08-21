<script lang="ts">
import { PUBLIC_API_URL } from '$env/static/public'
import { onMount } from 'svelte'
import FranceConnectSvgIcon from './FranceConnectSvgIcon.svelte'

let userinfo: Object = $state({})
let isFranceConnected: boolean = $state(false)

onMount(async () => {
  try {
    const response = await fetch(`${PUBLIC_API_URL}/api/v1/userinfo`)

    if (response.status == 200) {
      isFranceConnected = true
      userinfo = await response.json()

      console.log('userinfo', userinfo)
    }
  } catch (error) {
    console.error(error)
  }
})

// FC - Step 3
const franceConnect = async () => {
  const FS_URL = 'https://localhost:5173'
  const DATA_CALLBACK_FS_PATH = '/ami-fs-test-login-callback'
  const DATA_CLIENT_ID =
    '88d6fc32244b89e2617388fb111e668fec7b7383c841a08eefbd58fd11637eec'
  const STATE = 'stateazertyuiopqsdfghjklmwxcvbn012345'
  const NONCE = 'nonceazertyuiopqsdfghjklmwxcvbn012345'
  const FC_URL = 'https://fcp-low.sbx.dev-franceconnect.fr'
  const AUTHORIZATION_FC_PATH = '/api/v2/authorize'

  const query = {
    scope:
      'openid given_name family_name preferred_username birthdate gender birthplace birthcountry sub email given_name_array',
    redirect_uri: `${FS_URL}${DATA_CALLBACK_FS_PATH}`,
    response_type: 'code',
    client_id: DATA_CLIENT_ID,
    state: STATE,
    nonce: NONCE,
    acr_values: 'eidas1',
    prompt: 'login',
  }

  const url = `${FC_URL}${AUTHORIZATION_FC_PATH}`
  const params = new URLSearchParams(query).toString()

  window.location.href = `${url}?${params}`

  return Response.redirect(`${url}?${params}`)
}
</script>

<div class="homepage">
{#if !isFranceConnected}
  <div class="france-connect-svg-icon">
    <svelte:component this={FranceConnectSvgIcon} />
  </div>

  <div class="france-connect-text">
    <p>Pour pouvoir accéder à <strong>vos droits, à des conseils, et aux échéances</strong> liées à votre situation personnelle, veuillez vous connecter via <strong>France Connect</strong>.</p>
  </div>

  <div class="fr-connect-group-wrapper">
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
    <li>userinfo: { userinfo }</li>
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
	div.homepage {
		padding: 24px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
	}

  div.france-connect-text {
    margin-bottom: 20px;
  }

  div.fr-connect-group {
    display: flex;
    flex-direction: column;
    align-items: center;
	}

  button.fr-connect {
    padding-left: 6em !important;
    padding-right: 4em !important;
  }

  button.fr-connect:before {
    width: 3em !important;
    left: 2.5em !important;
  }

  h1 {
    font-weight: 700;
    font-size: 28px;
    line-height: 36px;
  }
</style>
