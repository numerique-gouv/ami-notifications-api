<script lang="ts">
  import applicationSvg from '@gouvfr/dsfr/dist/artwork/pictograms/digital/application.svg'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/state'
  import {
    PUBLIC_API_URL,
    PUBLIC_FC_AMI_CLIENT_ID,
    PUBLIC_FC_AMI_REDIRECT_URL,
    PUBLIC_FC_AUTHORIZATION_ENDPOINT,
    PUBLIC_FC_BASE_URL,
    PUBLIC_FC_PROXY,
  } from '$env/static/public'
  import { apiFetch } from '$lib/auth'
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte'
  import Navigation from '$lib/Navigation.svelte'
  import { userStore } from '$lib/state/User.svelte'

  let isLoggedOut: boolean = $state(false)
  let error: string = $state('')
  let error_description: string = $state('')

  onMount(async () => {
    // User state already initialized in +layout.svelte

    try {
      if (page.url.searchParams.has('error')) {
        error = page.url.searchParams.get('error') || ''
      }
      if (page.url.searchParams.has('error_description')) {
        error_description = page.url.searchParams.get('error_description') || ''
      }
      if (
        page.url.searchParams.has('error_type') &&
        page.url.searchParams.get('error_type') === 'FranceConnect'
      ) {
        // Error during login, logout, token query... => logout the app.
        localStorage.clear()
      }
      if (error === 'access_denied' && error_description === 'User auth aborted') {
        // The user has aborted the FranceConnection, don't display any error message.
        error = ''
        error_description = ''
      }
      if (page.url.searchParams.has('is_logged_in')) {
        const access_token = page.url.searchParams.get('access_token') || ''
        const token_type = page.url.searchParams.get('token_type') || ''
        localStorage.setItem('access_token', access_token)
        localStorage.setItem(
          'expires_in',
          page.url.searchParams.get('expires_in') || ''
        )
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
        const response = await apiFetch('/fc_userinfo', {
          headers: userinfo_endpoint_headers,
          credentials: 'include',
        })
        const result = await response.json()
        localStorage.setItem('user_data', result.user_data)
        localStorage.setItem('user_id', result.user_id)
        await userStore.checkLoggedIn()
        goto('/')
      }
      if (page.url.searchParams.has('is_logged_out')) {
        isLoggedOut = true
        goto('/')
      }
    } catch (error) {
      console.error(error)
    }
  })

  // FC - Step 3
  const franceConnectLogin = async () => {
    window.location.href = `${PUBLIC_API_URL}/login-france-connect`
  }

  function dismissNotice() {
    isLoggedOut = false
  }

  function dismissError() {
    error = ''
    error_description = ''
    goto('/')
  }
</script>

<div class="homepage">
  {#if !userStore.connected}
    <div class="homepage-not-connected">
      {#if error}
        <div class="fr-notice fr-notice--alert">
          <div class="fr-container">
            <div class="fr-notice__body">
              <p>
                <span class="fr-notice__title">{error}</span>
                {#if error_description}
                  <span class="fr-notice__desc">{error_description}</span>
                {/if}
              </p>
              <button
                onclick="{dismissError}"
                title="Masquer le message"
                type="button"
                class="fr-btn--close fr-btn"
              >
                Masquer le message
              </button>
            </div>
          </div>
        </div>
      {/if}
      {#if isLoggedOut}
        <div class="logout-notice fr-py-3v fr-px-4v">
          <div class="container-left">
            <img
              src="/icons/fr--success-line-green.svg"
              class="fr-mr-2v"
              alt="Icône de succès"
            >
            <span>Vous avez bien été déconnecté</span>
          </div>
          <div class="container-right">
            <button
              onclick="{dismissNotice}"
              title="Masquer le message"
              aria-label="Masquer le message"
              type="button"
              class="fr-btn--close fr-btn"
            ></button>
          </div>
        </div>
      {/if}
      <div class="france-connect-svg-icon">
        <img src="{applicationSvg}" alt="Icône de notification">
      </div>

      <div class="france-connect-text">
        <p>
          Pour pouvoir accéder à
          <strong>vos droits, à des conseils, et aux échéances</strong> liées à votre
          situation personnelle, veuillez vous connecter via
          <strong>FranceConnect</strong>.
        </p>
        <p class="fr-text--sm">
          FranceConnect est la solution proposée par l’État pour sécuriser et simplifier
          la connexion à vos services en ligne.
        </p>
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
          <a
            href="https://franceconnect.gouv.fr/"
            target="_blank"
            rel="noopener"
            title="Qu’est-ce que FranceConnect ? - nouvelle fenêtre"
            >Qu’est-ce que FranceConnect ?</a
          >
        </p>
      </div>
    </div>
  {:else if userStore.connected}
    <Navigation currentItem="home" />
    <ConnectedHomepage />
  {/if}
</div>

<style>
  .homepage {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    margin-bottom: 68px;

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
        border-left: 3px solid #58b77d;
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
      }
    }
  }
</style>
