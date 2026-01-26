<script lang="ts">
  import applicationSvg from '@gouvfr/dsfr/dist/artwork/pictograms/digital/application.svg'
  import { onMount } from 'svelte'
  import { goto } from '$app/navigation'
  import { page } from '$app/state'
  import { PUBLIC_API_URL, PUBLIC_CONTACT_URL } from '$env/static/public'
  import { apiFetch } from '$lib/auth'
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte'
  import Navigation from '$lib/Navigation.svelte'
  import { toastStore } from '$lib/state/toast.svelte'
  import { userStore } from '$lib/state/User.svelte'

  let error: string = $state('')
  let error_description: string = $state('')
  const contactUrl = PUBLIC_CONTACT_URL

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
        localStorage.setItem(
          'is_logged_in',
          page.url.searchParams.get('is_logged_in') || ''
        )
        localStorage.setItem('id_token', page.url.searchParams.get('id_token') || '')
        localStorage.setItem('user_data', page.url.searchParams.get('user_data') || '')
        localStorage.setItem(
          'user_fc_hash',
          page.url.searchParams.get('user_fc_hash') || ''
        )
        localStorage.setItem(
          'user_api_particulier_encoded_address',
          page.url.searchParams.get('address') || ''
        )
        await userStore.checkLoggedIn()
        if (page.url.searchParams.get('user_first_login') === 'true') {
          goto('/#/notifications-welcome-page')
        } else {
          goto('/')
        }
      }
      if (page.url.searchParams.has('is_logged_out')) {
        toastStore.addToast('Vous avez bien été déconnecté(e)', 'neutral')
        goto('/')
      }
    } catch (error) {
      console.error(error)
    }
  })

  // FC - Step 3
  const franceConnectLogin = async () => {
    try {
      await fetch(`${PUBLIC_API_URL}/ping`, {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-store',
      })
      window.location.href = `${PUBLIC_API_URL}/login-france-connect`
    } catch {
      goto('/#/network-error')
    }
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

      <div class="contact-link-wrapper">
        <p>Difficultés de connexion&nbsp;?</p>
        <p>
          <a
            href="{contactUrl}"
            title="Contactez-nous sur Tchap"
            aria-label="Contactez-nous sur Tchap"
            data-testid="contact-link"
          >
            Contactez-nous sur Tchap
          </a>
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
    height: 100vh;

    .homepage-not-connected {
      display: flex;
      flex-direction: column;
      position: relative;
      margin: 24px 16px;
      height: 100vh;

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

      .contact-link-wrapper {
        flex-grow: 1;
        align-content: end;
        text-align: center;

        p {
          margin: 0;
          font-size: 14px;

          a {
            color: var(--text-active-blue-france);
          }
        }
      }
    }
  }
</style>
