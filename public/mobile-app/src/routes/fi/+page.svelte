<script lang="ts">
  import { PUBLIC_API_URL } from '$env/static/public';
  import { franceConnectLogout } from '$lib/france-connect';

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
