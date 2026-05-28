<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { PUBLIC_API_URL } from '$env/static/public';
  import { franceConnectLogout } from '$lib/france-connect';

  let api_particulier_quotient = $state({});

  onMount(async () => {
    const searchParams = page.url.searchParams;
    if (searchParams.has('is_logged_in')) {
      if (
        localStorage.getItem('id_token') === null &&
        searchParams.get('id_token') !== ''
      ) {
        localStorage.setItem('id_token', searchParams.get('id_token') || '');
      }
      const encoded_api_particulier_quotient =
        searchParams.get('api_particulier_quotient') || '';
      if (encoded_api_particulier_quotient) {
        try {
          api_particulier_quotient = JSON.parse(atob(encoded_api_particulier_quotient));
        } catch (error) {
          console.error(error);
        }
      }
    }
  });

  const AMIFILogin = async () => {
    const id_token_hint = localStorage.getItem('id_token') || '';
    const redirect_url = `${PUBLIC_API_URL}/login-ami-fi`;
    if (id_token_hint) {
      await franceConnectLogout(id_token_hint, redirect_url);
    } else {
      window.location.href = redirect_url;
    }
  };
</script>

<div>
  <button class="fr-connect" type="button" id="fr-connect-button" onclick={AMIFILogin}>
    Test AMI-FI
  </button>
</div>

{#if Object.keys(api_particulier_quotient).length}
  <section class="fr-accordion">
    <h3 class="fr-accordion__title">
      <button
        type="button"
        class="fr-accordion__btn"
        aria-expanded="false"
        aria-controls="accordion-1"
      >
        API particulier quotient
      </button>
    </h3>
    <div id="accordion-1" class="fr-collapse">
      <pre
        data-testid="api_particulier_quotient"
      >{ JSON.stringify(api_particulier_quotient, null, 2) }</pre>
    </div>
  </section>
{/if}
