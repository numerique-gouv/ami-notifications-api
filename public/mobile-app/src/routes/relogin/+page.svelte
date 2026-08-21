<script lang="ts">
  import applicationSvg from '@gouvfr/dsfr/dist/artwork/pictograms/digital/application.svg';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { PUBLIC_CONTACT_EMAIL, PUBLIC_CONTACT_URL } from '$env/static/public';
  import Banner from '$lib/components/Banner.svelte';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import type { UserIdentity } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let error: string = $state('');
  let error_description: string = $state('');
  const contactUrl = PUBLIC_CONTACT_URL;
  const contactEmail = PUBLIC_CONTACT_EMAIL;

  let identity: UserIdentity = $state() as UserIdentity;

  // FC - Step 3
  const franceConnectLogin = async () => {
    try {
      await fetch('/ping', {
        method: 'HEAD',
        mode: 'no-cors',
        cache: 'no-store',
      });
      window.location.href = '/relogin-france-connect';
    } catch {
      goto('/#/network-error');
    }
  };

  function dismissError() {
    error = '';
    error_description = '';
    goto('/#/login');
  }

  let connectionHelpModal = $state(false);
  const onConnectionHelpOpen = () => {
    connectionHelpModal = true;
  };
  const closeConnectionHelpModal = () => {
    connectionHelpModal = false;
  };

  if (!userStore.connected) {
    goto('/#/login');
  } else {
    identity = userStore.connected.identity;
  }
</script>

<div class="relogin-page">
  <Banner
    id="relogin"
    title="Vous devez vous connecter en tant que {identity.given_name} {identity.preferred_username || identity.family_name} pour pouvoir continuer ce parcours."
    bannerType="info"
    closeButton="false"
  />

  <div class="fr-px-2w fr-py-3w relogin-page-not-connected">
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
        <h1 class="fr-h4 fr-mb-1w france-connect-title">La connexion est nécessaire</h1>
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

<style>
  .relogin-page {
    display: flex;
    flex-direction: column;
    height: 100vh;

    .relogin-page-not-connected {
      text-align: center;
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
