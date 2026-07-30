<script lang="ts">
  import type { RegistrationResponseJSON } from '@simplewebauthn/browser';
  import { startRegistration } from '@simplewebauthn/browser';
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED } from '$env/static/public';
  import { AMIGoto } from '$lib/ami-navigation';
  import { apiFetch } from '$lib/auth';
  import { initializeData, initializeLocalStorage } from '$lib/initializeDataFromAPI';
  import { toastStore } from '$lib/state/toast.svelte';
  import type { UserIdentity } from '$lib/state/User.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import * as telemetry from '$lib/telemetry';

  let wrapperEl: HTMLDivElement;

  const redirectLoggedInUser = (createdPasskey: boolean) => {
    initializeData();
    const passKeyParam = createdPasskey ? '?passkey_toast=true' : '';
    const redirect_url = page.url.searchParams.get('login_redirect_url');
    if (redirect_url) {
      AMIGoto(redirect_url);
    } else {
      AMIGoto(`/${passKeyParam}#/welcome/zones`);
    }
  };

  const silent_fc_enabled = PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED === 'true';
  let hasWorkingPassKey: boolean = $state(true);
  let hasSuggestPasskeyCreationToday: boolean = $state(false);

  onMount(async () => {
    try {
      initializeLocalStorage(page.url.searchParams);
      await userStore.buildUser();
      if (!userStore.connected) {
        AMIGoto('/#/login');
        return;
      }
      telemetry.info('User logged in');
      hasWorkingPassKey = userStore.getHasWorkingPasskey();
      if (hasWorkingPassKey) {
        telemetry.info('User has working passkey');
      }
      hasSuggestPasskeyCreationToday = userStore.getHasSuggestPasskeyCreationToday();
      console.log(hasSuggestPasskeyCreationToday);
      if (!silent_fc_enabled || hasWorkingPassKey || hasSuggestPasskeyCreationToday) {
        // if silent fc is not enabled,
        // if user has a working pass key,
        // or is we already asked the user to create a passkey today,
        // we directly redirect to homepage
        redirectLoggedInUser(false);
      }
    } catch (error) {
      console.error(error);
      AMIGoto('/#/login');
    }

    wrapperEl.style.height = `${window.innerHeight}px`;
    console.log('innerHeight:', window.innerHeight);
  });

  const passkeyError = () => {
    return toastStore.addToast(
      'Erreur lors de l’ajout de votre clé d’accès',
      'error',
      3000,
      false
    );
  };

  const networkError = () => {
    return toastStore.addToast(
      'Problème de connexion Internet, veuillez réessayer',
      'error',
      3000,
      false
    );
  };

  const bypassPasskey = async () => {
    userStore.setLastPasskeyCreationSuggestion();
    telemetry.info('User skipped passkey generation');
    redirectLoggedInUser(false);
  };

  const createPasskey = async () => {
    if (!userStore.connected) {
      return;
    }
    let identity: UserIdentity = userStore.connected.identity;
    let display_name = `${identity.given_name} ${identity.preferred_username || identity.family_name}`;
    let optionsResp: Response;
    telemetry.info('Generating passkey');
    try {
      optionsResp = await apiFetch('/api/v1/fi/passkey/generate-registration-options', {
        method: 'POST',
        body: JSON.stringify({ displayName: display_name }),
        headers: { 'Content-Type': 'application/json' },
      });
      if (!optionsResp.ok) {
        telemetry.error('Error generating passkey', {
          error: '!options resp.ok',
        });
        return passkeyError();
      }
    } catch (error) {
      console.log('ERROR', `${error}`);
      if (error instanceof TypeError) {
        telemetry.error('Error generating passkey', {
          error: 'network error',
        });
        return networkError();
      } else {
        telemetry.error('Error generating passkey', {
          error: `${error}`,
        });
        return passkeyError();
      }
    }

    let attResp: RegistrationResponseJSON;
    try {
      const opts = await optionsResp.json();

      console.log('Registration Options', JSON.stringify(opts, null, 2));

      attResp = await startRegistration({ optionsJSON: opts });
      console.log('Registration Response', JSON.stringify(attResp, null, 2));
    } catch (error) {
      telemetry.error('Error generating passkey', { error: `${error}` });
      console.log('ERROR', `${error}`);
      return passkeyError();
    }

    let verificationResp: Response;
    try {
      verificationResp = await apiFetch('/api/v1/fi/passkey/verify-registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(attResp),
      });
      if (!verificationResp.ok) {
        telemetry.error('Error generating passkey', {
          error: '!verification resp.ok',
        });
        return passkeyError();
      }
    } catch (error) {
      console.log('ERROR', `${error}`);
      if (error instanceof TypeError) {
        telemetry.error('Error generating passkey', {
          error: 'network error',
        });
        return networkError();
      } else {
        telemetry.error('Error generating passkey', {
          error: `${error}`,
        });
        return passkeyError();
      }
    }

    const verificationJSON = await verificationResp.json();
    console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      console.log('Authenticator registered!');
      userStore.setHasWorkingPasskey();
      telemetry.info('User added a passkey');
      redirectLoggedInUser(true);
    } else {
      telemetry.error('Error generating passkey', {
        error: '!verified',
      });
      console.log(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
      return passkeyError();
    }
  };
</script>

<div class="fr-container passkeys-full-page" bind:this={wrapperEl}>
  {#if silent_fc_enabled && !hasWorkingPassKey && !hasSuggestPasskeyCreationToday}
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
              onclick="{bypassPasskey}"
              data-testid="bypass-passkey-button"
              type="button"
              class="fr-btn fr-btn--tertiary"
            >
              Peut-être plus tard
            </button>
          </li>
        </ul>
      </div>
    </div>
  {/if}
</div>
<style>
  .passkeys-full-page {
    height: 100vh;
    display: flex;
    align-items: center;
  }
</style>
