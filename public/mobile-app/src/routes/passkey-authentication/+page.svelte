<script lang="ts">
  import type { AuthenticationResponseJSON } from '@simplewebauthn/browser';
  import { startAuthentication } from '@simplewebauthn/browser';
  import { page } from '$app/state';
  import { AMIGoto } from '$lib/ami-navigation';
  import { apiFetch } from '$lib/auth';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import Toast from '$lib/components/Toast.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import * as telemetry from '$lib/telemetry';

  let hasPasskeyError: boolean = $state(false);
  let hasClickedOnPasskeyBtn: boolean = $state(false);
  let hasBreakingPasskeyError: boolean = $state(false);
  let hasNetworkError: boolean = $state(false);

  const passkeyError = () => {
    hasPasskeyError = true;
    hasBreakingPasskeyError = false;
    hasNetworkError = false;
  };

  const breakingPasskeyError = () => {
    hasPasskeyError = true;
    hasBreakingPasskeyError = true;
    hasNetworkError = false;
  };

  const networkError = () => {
    hasPasskeyError = true;
    hasBreakingPasskeyError = false;
    hasNetworkError = true;
  };

  const authenticate = async () => {
    hasClickedOnPasskeyBtn = true;
    let optionsResp: Response;
    telemetry.info('Authenticating with passkey');
    try {
      optionsResp = await fetch('/api/v1/fi/passkey/generate-authentication-options');
      if (!optionsResp.ok) {
        return passkeyError();
      }
    } catch (error) {
      console.log('ERROR', `${error}`);
      if (error instanceof TypeError) {
        return networkError();
      } else {
        return passkeyError();
      }
    }

    let attResp: AuthenticationResponseJSON;
    try {
      const opts = await optionsResp.json();

      console.log('Authentication Options', JSON.stringify(opts, null, 2));
      attResp = await startAuthentication({ optionsJSON: opts });
      console.log('Authentication Response', JSON.stringify(attResp, null, 2));
    } catch (error) {
      telemetry.error('Error using passkey authentication', {
        error: `${error}`,
      });
      console.log('ERROR', `${error}`);
      return passkeyError();
    }

    let verificationResp: Response;
    try {
      verificationResp = await apiFetch('/api/v1/fi/passkey/verify-authentication', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(attResp),
      });
      if (!verificationResp.ok) {
        if (verificationResp.status === 400) {
          const verificationJSON = await verificationResp.json();
          if (verificationJSON.retry === true) {
            // 400 errors without retry are FISession errors
            telemetry.warn('Non-fatal error verifiying passkey authentication');
            return passkeyError();
          }
          telemetry.error('Error using passkey authentication', {
            error: 'breakingPasskeyError',
          });
          return breakingPasskeyError();
        }
        telemetry.error('Error using passkey authentication', {
          error: 'passkeyError',
        });
        return passkeyError();
      }
    } catch (error) {
      console.log('ERROR', `${error}`);
      if (error instanceof TypeError) {
        telemetry.error('Error using passkey authentication', {
          error: 'network error',
        });
        return networkError();
      } else {
        telemetry.error('Error using passkey authentication', {
          error: `${error}`,
        });
        return passkeyError();
      }
    }

    const verificationJSON = await verificationResp.json();
    console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      console.log('User authenticated!');
      userStore.setHasWorkingPasskey();
      telemetry.info('User used a passkey successfully');
      AMIGoto(verificationJSON?.redirect_uri);
    } else {
      telemetry.error('Error using passkey authentication', {
        error: '!verified',
      });
      console.log(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
      return passkeyError();
    }
  };

  const back = () => {
    const hash = page.url.searchParams.get('redirect_to_hash') || '';
    if (hash !== '') {
      AMIGoto(`/#${hash}`);
      return;
    }
    AMIGoto('/');
  };

  const closeModal = () => {
    back();
  };

  const bypassPasskey = async () => {
    userStore.unsetHasWorkingPasskey();
    AMIGoto('/#/relogin');
  };
</script>

<BottomModal onClose={closeModal}>
  {#snippet modalContent()}
    <div class="fr-container">
      <div class="fr-grid-row fr-grid-row--center">
        <div class="image-wrapper">
          <img src="/icons/passkeys.svg" alt="">
        </div>
      </div>

      <div class="fr-grid-row fr-grid-row--center">
        <h1 class="fr-h4 fr-mb-1w">La connexion est nécessaire</h1>
      </div>

      <div class="fr-grid-row fr-grid-row--center">
        <p>Utiliser votre clé d’accès pour vous connecter</p>
      </div>
    </div>
    <ul class="fr-btns-group">
      <li>
        <button
          onclick="{authenticate}"
          title="Utiliser ma clé d’accès"
          type="button"
          class="fr-btn"
          data-testid="use-passkey"
        >
          Utiliser ma clé d’accès
        </button>
      </li>
      {#if hasBreakingPasskeyError}
        <li>
          <button
            type="button"
            class="fr-btn fr-btn--tertiary-no-outline"
            onclick="{back}"
            data-testid="back"
          >
            Revenir à la page précédente
          </button>
        </li>
      {:else if hasClickedOnPasskeyBtn}
        <li>
          <button
            type="button"
            class="fr-btn fr-btn--tertiary-no-outline"
            onclick="{bypassPasskey}"
            data-testid="bypass-passkey"
          >
            Ma clé n’est plus reconnue
          </button>
        </li>
      {/if}
    </ul>
    {#if hasNetworkError}
      <Toast
        id="error"
        title="Problème de connexion Internet, veuillez réessayer"
        toastType="error"
        duration={null}
        hasCloseLink={false}
      />
    {:else if hasBreakingPasskeyError}
      <Toast
        id="error"
        title="Erreur lors de l’utilisation de votre clé d’accès"
        toastType="error"
        duration={null}
        hasCloseLink={false}
      />
    {:else if hasPasskeyError}
      <Toast
        id="error"
        title="Erreur lors de l’utilisation de votre clé d’accès"
        toastType="error"
        duration={null}
        hasCloseLink={false}
      />
    {/if}
  {/snippet}
</BottomModal>
