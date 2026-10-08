<script lang="ts">
  import { page } from '$app/state';
  import { AMIGoto } from '$lib/ami-navigation';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import Toast from '$lib/components/Toast.svelte';
  import {
    authenticateWithPasskey,
    PasskeyBreakingError,
    PasskeyError,
    PasskeyNetworkError,
  } from '$lib/passkey';
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
    try {
      const url: string = await authenticateWithPasskey();
      userStore.setHasWorkingPasskey();
      telemetry.info('User used a passkey successfully');
      AMIGoto(url);
    } catch (error) {
      if (error instanceof PasskeyError) {
        passkeyError();
      } else if (error instanceof PasskeyBreakingError) {
        breakingPasskeyError();
      } else if (error instanceof PasskeyNetworkError) {
        networkError();
      }
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
    {:else if hasBreakingPasskeyError || hasPasskeyError}
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
