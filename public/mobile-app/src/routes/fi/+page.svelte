<script lang="ts">
  import { PUBLIC_API_URL } from '$env/static/public';

  const AMIFILogin = async () => {
    window.location.href = `${PUBLIC_API_URL}/login-ami-fi`;
  };
</script>

<div>
  <button class="fr-connect" type="button" id="fr-connect-button" onclick={AMIFILogin}>
    Test AMI-FI
  </button>
</div>
