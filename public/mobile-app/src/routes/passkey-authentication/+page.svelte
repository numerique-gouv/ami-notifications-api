<script lang="ts">
  import { startAuthentication } from '@simplewebauthn/browser';

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

  const authenticate = async () => {
    const resp = await fetch('/api/v1/fi/passkey/generate-authentication-options');

    let attResp: unknown;
    try {
      const opts = await resp.json();

      log('Authentication Options', JSON.stringify(opts, null, 2));

      attResp = await startAuthentication({ optionsJSON: opts });
      log('Authentication Response', JSON.stringify(attResp, null, 2));
    } catch (error) {
      log('ERROR', `${error}`);
      throw error;
    }

    const verificationResp = await fetch('/api/v1/fi/passkey/verify-authentication', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attResp),
    });

    const verificationJSON = await verificationResp.json();
    log('Server Response', JSON.stringify(verificationJSON, null, 2));

    if (verificationJSON?.verified) {
      logMore('User authenticated!');
    } else {
      logMore(
        `Oh no, something went wrong! Response: ${JSON.stringify(verificationJSON)}`
      );
    }

    window.location = verificationJSON?.redirect_uri;
  };
</script>

<button
  onclick="{authenticate}"
  title="Données biométriques"
  type="button"
  class="fr-btn"
>
  Données biométriques
</button>

{#if debugTitle}
  <p>{debugTitle}: {debugMessage}</p>
  <p>{debugMoreMessage}</p>
{/if}
