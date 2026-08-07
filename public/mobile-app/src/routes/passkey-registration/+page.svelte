<script lang="ts">
  import { startRegistration } from '@simplewebauthn/browser';

  let debugTitle: string = $state('');
  let debugMessage: string = $state('');
  let debugMoreMessage: string = $state('');

  const log = (title: string, message: string) => {
    debugTitle = title;
    debugMessage = message;
    debugMoreMessage = '';
  };
  const logMore = (message: string) => {
    debugMoreMessage = message;
  };

  const createPasskey = async () => {
    const resp = await fetch('/api/v1/fi/passkey/generate-registration-options');

    let attResp: unknown;
    try {
      const opts = await resp.json();

      log('Registration Options', JSON.stringify(opts, null, 2));

      attResp = await startRegistration({ optionsJSON: opts });
      log('Registration Response', JSON.stringify(attResp, null, 2));
    } catch (error) {
      log('ERROR', `${error}`);
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
    log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      logMore('Authenticator registered!');
    } else {
      logMore(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
    }
  };
</script>

<button
  onclick="{createPasskey}"
  title="Créer une passkey"
  type="button"
  class="fr-btn"
>
  Créer une passkey
</button>

{#if debugTitle}
  <p>{debugTitle}: {debugMessage}</p>
  <p>{debugMoreMessage}</p>
{/if}
