<script lang="ts">
  import applicationSvg from '@gouvfr/dsfr/dist/artwork/pictograms/digital/application.svg';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import {
    PUBLIC_API_URL,
    PUBLIC_CONTACT_EMAIL,
    PUBLIC_CONTACT_URL,
  } from '$env/static/public';
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte';
  import ItemModal from '$lib/components/modal/ItemModal.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { initializeData } from '$lib/initializeDataFromAPI';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let error: string = $state('');
  let error_description: string = $state('');
  const contactUrl = PUBLIC_CONTACT_URL;
  const contactEmail = PUBLIC_CONTACT_EMAIL;

  onMount(async () => {
    // User state already initialized in +layout.svelte

    try {
      if (page.url.searchParams.has('error')) {
        error = page.url.searchParams.get('error') || '';
      }
      if (page.url.searchParams.has('error_description')) {
        error_description = page.url.searchParams.get('error_description') || '';
      }
      if (
        page.url.searchParams.has('error_type') &&
        page.url.searchParams.get('error_type') === 'FranceConnect'
      ) {
        // Error during login, logout, token query... => logout the app.
        localStorage.clear();
      }
      if (error === 'access_denied' && error_description === 'User auth aborted') {
        // The user has aborted the FranceConnection, don't display any error message.
        error = '';
        error_description = '';
      }
      if (page.url.searchParams.has('is_logged_in')) {
        await initializeData(page.url.searchParams, userStore);
        if (page.url.searchParams.get('user_first_login') === 'true') {
          goto('/#/welcome/zones');
        } else {
          goto('/');
        }
      }
      if (page.url.searchParams.has('is_logged_out')) {
        toastStore.addToast('Vous avez bien été déconnecté(e)', 'success', 3000, false);
        goto('/');
      }
    } catch (error) {
      console.error(error);
    }
  });

  // FC - Step 3
  const franceConnectLogin = async () => {
    try {
      await fetch(`${PUBLIC_API_URL}/ping`, {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-store',
      });
      window.location.href = `${PUBLIC_API_URL}/login-france-connect`;
    } catch {
      goto('/#/network-error');
    }
  };

  function dismissError() {
    error = '';
    error_description = '';
    goto('/');
  }

  let connectionHelpModal = $state(false);
  const onConnectionHelpOpen = () => {
    connectionHelpModal = true;
  };
  const closeConnectionHelpModal = () => {
    connectionHelpModal = false;
  };
</script>

{#if !userStore.connected}
  <div class="homepage">
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
      <div class="france-connect-wrapper">
        <div class="france-connect-svg-icon">
          <img src="{applicationSvg}" alt="">
        </div>

        <div class="france-connect-text">
          <h1 class="fr-h4 france-connect-title">Me connecter à AMI</h1>
          <p class="fr-text--sm">
            <strong>FranceConnect</strong> est la solution proposée par l’État pour
            <strong>sécuriser</strong> et <strong>simplifier</strong> la connexion à vos
            services en ligne.
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
              >Qu’est-ce que FranceConnect&nbsp;?</a
            >
          </p>
        </div>
      </div>

      <div class="connection-help-wrapper">
        <a
          role="button"
          href="."
          onclick={onConnectionHelpOpen}
          data-testid="connection-help-link"
          >Je n’arrive pas à me connecter</a
        >
      </div>

      {#if connectionHelpModal}
        <ItemModal onClose={closeConnectionHelpModal}>
          {#snippet header()}
            <ul class="connection-help-links">
              <li>
                <a
                  class="fr-icon-edit-fill"
                  href="{contactUrl}"
                  data-testid="connection-help-link-url"
                  >Faire une demande en ligne</a
                >
              </li>
              <li>
                <a
                  class="fr-icon-mail-fill"
                  href="mailto:{contactEmail}"
                  data-testid="connection-help-link-email"
                  >Envoyer un mail</a
                >
              </li>
            </ul>
          {/snippet}
          {#snippet footer()}
          {/snippet}
        </ItemModal>
      {/if}
    </div>
  </div>
{:else if userStore.connected}
  <Navigation currentItem="home" />
  <ConnectedHomepage />
{/if}

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

      .france-connect-wrapper {
        display: flex;
        flex-direction: column;
        flex: 1;
        align-items: center;
        justify-content: center;

        .france-connect-svg-icon {
          text-align: center;
          margin-bottom: 2rem;
          img {
            height: 100px;
            width: 100px;
          }
        }

        .fr-connect-group {
          display: flex;
          flex-direction: column;
          justify-content: center;
          text-align: center;
        }
        .france-connect-title {
          text-align: center;
          margin-bottom: 8px;
        }
      }

      .connection-help-wrapper {
        text-align: center;
        a {
          color: var(--text-action-high-blue-france);
        }
      }
      .connection-help-links {
        margin: 0;
        padding: 0 0.25em;
        list-style: none;
        display: flex;
        flex-direction: column;
        a {
          padding: 0.5rem 0;
          display: block;
          background: none;
          &::before {
            margin-right: 0.5rem;
            color: var(--text-action-high-blue-france);
          }
        }
      }
    }
  }
</style>
