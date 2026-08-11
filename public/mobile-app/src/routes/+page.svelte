<script lang="ts">
  import applicationSvg from '@gouvfr/dsfr/dist/artwork/pictograms/digital/application.svg';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { PUBLIC_CONTACT_EMAIL, PUBLIC_CONTACT_URL } from '$env/static/public';
  import ConnectedHomepage from '$lib/ConnectedHomepage.svelte';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
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
      await fetch('/ping', {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-store',
      });
      window.location.href = '/login-france-connect';
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
    <div class="fr-px-2w fr-py-3w homepage-not-connected">
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
                type="button"
                onclick="{dismissError}"
                title="Masquer le message"
                class="fr-btn--close fr-btn"
              >
                Masquer le message
              </button>
            </div>
          </div>
        </div>
      {/if}
      <div class="france-connect-wrapper">
        <div class="fr-mb-4w france-connect-svg-icon">
          <img src="{applicationSvg}" alt="">
        </div>

        <div class="france-connect-text">
          <h1 class="fr-h4 fr-mb-1w france-connect-title">Me connecter à AMI</h1>
          <p class="fr-text--sm">
            <strong>FranceConnect</strong> est la solution proposée par l’État pour
            <strong>sécuriser</strong> et <strong>simplifier</strong> la connexion à vos
            services en ligne.
          </p>
        </div>

        <div class="fr-connect-group">
          <button
            type="button"
            class="fr-connect"
            id="fr-connect-button"
            onclick={franceConnectLogin}
          >
            <span class="fr-connect__login">S’identifier avec</span>
            <span class="fr-connect__brand">FranceConnect</span>
          </button>
          <p>
            <button
              onclick={()=> window.open("https://franceconnect.gouv.fr/", "_blank")}
              aria-label="Qu’est-ce que FranceConnect ? - nouvelle fenêtre"
              class="fr-link fr-text--sm am-link-bordered"
            >
              Qu’est-ce que FranceConnect&nbsp;?
            </button>
          </p>
        </div>
      </div>

      <div class="connection-help-wrapper">
        <button
          id="connection-help-button"
          class="fr-link fr-px-4w fr-py-3v"
          onclick={onConnectionHelpOpen}
          data-testid="connection-help-button"
        >
          Je n’arrive pas à me connecter
        </button>
      </div>

      {#if connectionHelpModal}
        <BottomModal onClose={closeConnectionHelpModal}>
          {#snippet header()}
            <div class="fr-sidemenu">
              <ul class="fr-sidemenu__list connection-help-links">
                <li>
                  <button
                    type="button"
                    class="fr-sidemenu__link fr-text--regular fr-icon-edit-fill"
                    onclick={()=> goto(contactUrl)}
                    data-testid="connection-help-link-url"
                  >
                    Faire une demande en ligne
                  </button>
                </li>
                <li>
                  <button
                    type="button"
                    class="fr-sidemenu__link fr-text--regular fr-icon-mail-fill"
                    onclick={()=> window.location.href="mailto:"+contactEmail}
                    data-testid="connection-help-link-email"
                  >
                    Envoyer un mail
                  </button>
                </li>
              </ul>
            </div>
          {/snippet}
          {#snippet footer()}
          {/snippet}
        </BottomModal>
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
    text-align: center;

    .homepage-not-connected {
      display: flex;
      flex-direction: column;
      position: relative;
      height: 100vh;

      .france-connect-wrapper {
        display: flex;
        flex-direction: column;
        flex: 1;
        align-items: center;
        justify-content: center;

        .france-connect-svg-icon img {
          height: 6.25rem;
          width: 6.25rem;
        }

        .france-connect-text p {
          text-align: left;
        }
      }

      .connection-help-wrapper {
        #connection-help-button {
          text-decoration: underline;
          text-underline-offset: 0.5rem;
          &:hover {
            background: inherit;
            text-decoration-thickness: 2px;
          }
        }
      }
      ul.connection-help-links {
        button {
          color: var(--text-default-grey);
          &:before {
            margin-right: 0.5rem;
            color: var(--text-action-high-blue-france);
          }
        }
      }

      .fr-sidemenu {
        box-shadow: none;
      }
    }
  }
</style>
