<script lang="ts">
  import { startRegistration } from '@simplewebauthn/browser';
  import { onMount } from 'svelte';
  import { PUBLIC_API_URL } from '$env/static/public';

  let debugTitle: string = $state('');
  let debugMessage: string = $state('');

  onMount(async () => {});

  const log = (title: string, message: string) => {
    debugTitle = title;
    debugMessage = message;
  };

  const createPasskey = async () => {
    const resp = await fetch(`${PUBLIC_API_URL}/generate-registration-options`);

    try {
      const opts = await resp.json();

      log('Registration Options', JSON.stringify(opts, null, 2));

      const attResp = await startRegistration({ optionsJSON: opts });
      log('Registration Response', JSON.stringify(attResp, null, 2));
    } catch (error) {
      log('ERROR', `${error}`);
      throw error;
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
  <p id="debug">{debugTitle}: {debugMessage}</p>
{/if}
