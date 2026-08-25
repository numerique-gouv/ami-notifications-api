<script lang="ts">
  import type { AuthenticationResponseJSON } from '@simplewebauthn/browser';
  import { startAuthentication } from '@simplewebauthn/browser';
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { apiFetch } from '$lib/auth';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import Toast from '$lib/components/Toast.svelte';
  import { trackPasskey } from '$lib/matomo';
  import { userStore } from '$lib/state/User.svelte';

  let hasPasskeyError: boolean = $state(false);
  let hasNetworkError: boolean = $state(false);

  const passkeyError = () => {
    hasPasskeyError = true;
    hasNetworkError = false;
  };

  const networkError = () => {
    hasPasskeyError = true;
    hasNetworkError = true;
  };

  const authenticate = async () => {
    let optionsResp: Response;
    try {
      optionsResp = await fetch('/api/v1/fi/passkey/generate-authentication-options');
      if (!optionsResp.ok) {
        return networkError();
      }
    } catch (error) {
      console.log('ERROR', `${error}`);
      return passkeyError();
    }

    let attResp: AuthenticationResponseJSON;
    try {
      const opts = await optionsResp.json();

      console.log('Authentication Options', JSON.stringify(opts, null, 2));
      attResp = await startAuthentication({ optionsJSON: opts });
      console.log('Authentication Response', JSON.stringify(attResp, null, 2));
      trackPasskey('startAuthentication', 'success');
    } catch (error) {
      trackPasskey('startAuthentication', 'error');
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
        return networkError();
      }
    } catch (error) {
      console.log('ERROR', `${error}`);
      return passkeyError();
    }

    const verificationJSON = await verificationResp.json();
    console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      console.log('User authenticated!');
      trackPasskey('userAuthentication', 'success');
      userStore.setHasWorkingPasskey();
      window.location.href = verificationJSON?.redirect_uri;
    } else {
      trackPasskey('userAuthentication', 'error');
      console.log(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
      return passkeyError();
    }
  };

  const closeModal = () => {
    const hash = page.url.searchParams.get('redirect_to_hash') || '';
    if (hash !== '') {
      goto(`/#${hash}`);
      return;
    }
    goto('/');
  };

  const bypassPasskey = async () => {
    userStore.unsetHasWorkingPasskey();
    goto('/#/relogin');
  };
</script>

<BottomModal onClose={closeModal}>
  {#snippet header()}
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
  {/snippet}
  {#snippet footer()}
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
      {#if hasPasskeyError}
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
    {#if hasPasskeyError}
      <Toast
        id="error"
        title={hasNetworkError ? 'Problème de connexion Internet, veuillez réessayer': 'Erreur lors de l’utilisation de votre clé d’accès'}
        toastType="error"
        duration={null}
        hasCloseLink={false}
      />
    {/if}
  {/snippet}
</BottomModal>
