<script lang="ts">
  import { startAuthentication } from '@simplewebauthn/browser';
  import { apiFetch } from '$lib/auth';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import { trackPasskey } from '$lib/matomo';

  const authenticate = async () => {
    const resp = await fetch('/api/v1/fi/passkey/generate-authentication-options');

    let attResp: unknown;
    try {
      const opts = await resp.json();

      console.log('Authentication Options', JSON.stringify(opts, null, 2));
      attResp = await startAuthentication({ optionsJSON: opts });
      console.log('Authentication Response', JSON.stringify(attResp, null, 2));
      trackPasskey('startAuthentication', 'success');
    } catch (error) {
      trackPasskey('startAuthentication', 'error');
      console.log('ERROR', `${error}`);
      throw error;
    }

    const verificationResp = await apiFetch(
      '/api/v1/fi/passkey/verify-authentication',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(attResp),
      }
    );

    const verificationJSON = await verificationResp.json();
    console.log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      console.log('User authenticated!');
      trackPasskey('userAuthentication', 'success');
      window.location = verificationJSON?.redirect_uri;
    } else {
      trackPasskey('userAuthentication', 'error');
      console.log(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
    }
  };

  const closeModal = () => {
    // TODO: (maybe the modal shouldn't have a close button)
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
        >
          Utiliser ma clé d’accès
        </button>
      </li>
    </ul>
  {/snippet}
</BottomModal>
