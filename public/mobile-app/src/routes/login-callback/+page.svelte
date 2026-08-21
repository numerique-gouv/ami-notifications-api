<script lang="ts">
  import { startRegistration } from '@simplewebauthn/browser';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-goto';
  import { apiFetch } from '$lib/auth';
  import { initializeData, initializeLocalStorage } from '$lib/initializeDataFromAPI';
  import { trackPasskey } from '$lib/matomo';
  import type { UserIdentity } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';

  let wrapperEl: HTMLDivElement | undefined = $state();

  const redirectLoggedInUser = (createdPasskey: boolean) => {
    initializeData();
    const passKeyParam = createdPasskey ? '?passkey_toast=true' : '';
    const redirect_url = page.url.searchParams.get('login_redirect_url');
    if (redirect_url) {
      AMIGoto(redirect_url);
    } else if (page.url.searchParams.get('user_first_login') === 'true') {
      goto(`/${passKeyParam}#/welcome/zones`);
    } else {
      goto(`/${passKeyParam}`);
    }
  };

  const silent_fc_enabled = PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED === 'true';

  onMount(async () => {
    try {
      initializeLocalStorage(page.url.searchParams);
      await userStore.buildUser();
      if (!userStore.connected) {
        goto('/#/login');
        return;
      }
      if (!silent_fc_enabled || userStore.getHasWorkingPasskey()) {
        // if silent fc is not enabled, we directly redirect to homepage
        redirectLoggedInUser(false);
      }
    } catch (error) {
      console.error(error);
      goto('/#/login');
    }

    if (wrapperEl) {
      wrapperEl.style.height = `${window.innerHeight}px`;
      console.log('innerHeight:', window.innerHeight);
    }
  });

  const bypassPasskey = async () => {
    trackPasskey('generatePasskey', 'skip');
    redirectLoggedInUser(false);
  };

  const createPasskey = async () => {
    if (!userStore.connected) {
      return;
    }
    let identity: UserIdentity = userStore.connected.identity;
    let display_name = `${identity.given_name} ${identity.preferred_username || identity.family_name}`;
    const resp = await apiFetch('/api/v1/fi/passkey/generate-registration-options', {
      method: 'POST',
      body: JSON.stringify({ displayName: display_name }),
      headers: { 'Content-Type': 'application/json' },
    });

    let attResp: unknown;
    try {
      const opts = await resp.json();

      console.log('Registration Options', JSON.stringify(opts, null, 2));

      attResp = await startRegistration({ optionsJSON: opts });
      console.log('Registration Response', JSON.stringify(attResp, null, 2));
    } catch (error) {
      trackPasskey('generatePasskey', 'error');
      console.log('ERROR', `${error}`);
      throw error;
    }

    const verificationResp = await fetch('/api/v1/fi/passkey/verify-registration', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attResp),
    });

    const verificationJSON = await verificationResp.json();
    console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      trackPasskey('generatePasskey', 'success');
      console.log('Authenticator registered!');
      userStore.setHasWorkingPasskey();
      redirectLoggedInUser(true);
    } else {
      trackPasskey('generatePasskey', 'error');
      console.log(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
    }
  };
</script>

{#if silent_fc_enabled}
  <div class="fr-container passkeys-full-page" bind:this={wrapperEl}>
    <div class="fr-grid-row fr-grid-row--middle fr-grid-row--center">
      <div class="image-wrapper">
        <img src="/icons/passkeys.svg" alt="">
      </div>

      <h1 class="fr-h4 fr-mb-1w">Une connexion simplifée et sécurisée</h1>

      <p>
        Utiliser une clé d’accès pour vous connecter plus rapidement et de manière plus
        sécurisée qu’avec un mot de passe.
      </p>

      <div class="fr-grid-row fr-grid-row--middle fr-grid-row--center">
        <ul class="fr-btns-group">
          <li>
            <button
              onclick="{createPasskey}"
              data-testid="create-passkey-button"
              title="Ajouter une clé d’accès"
              type="button"
              class="fr-btn"
            >
              Ajouter une clé d’accès
            </button>
          </li>
          <li>
            <button
              type="button"
              class="fr-btn fr-btn--tertiary"
              onclick="{bypassPasskey}"
            >
              Peut-être plus tard
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
{/if}
<style>
  .passkeys-full-page {
    height: 100vh;
    display: flex;
    align-items: center;
  }
</style>
