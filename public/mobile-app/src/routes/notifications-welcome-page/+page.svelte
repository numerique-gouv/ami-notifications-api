<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { runOrNativeEvent } from '$lib/nativeEvents';
  import { enableNotificationsAndUpdateLocalStorage } from '$lib/notifications';
  import { toastStore } from '$lib/state/toast.svelte';
  import { userStore } from '$lib/state/User.svelte';

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }
  });

  const enableNotificationsFunc = async () => {
    await enableNotificationsAndUpdateLocalStorage();
    toastStore.addToast('Les notifications ont été activées', 'success');
    goto('/');
  };

  const clickOnEnable = async () => {
    runOrNativeEvent(enableNotificationsFunc, 'notification_permission_requested');
  };

  const goToHomepage = () => {
    goto('/');
  };
</script>

<div class="notifications-welcome-page">
  <div class="image-wrapper">
    <img
      class="address-icon"
      src="/remixicons/notification.svg"
      alt="Icône de notification"
    >
  </div>
  <h1>Activez les notifications pour suivre vos démarches</h1>
  <div class="descriptive-text">
    <p>
      Recevez des alertes de suivi et des rappels utiles quand vous en avez besoin. Vous
      pourrez les désactiver à tout moment.
    </p>
  </div>

  <div class="action-buttons">
    <button
      class="fr-btn fr-btn--lg"
      type="button"
      onclick="{clickOnEnable}"
      data-testid="enable-button"
    >
      Activer
    </button>
    <button
      class="fr-btn fr-btn--lg fr-btn--tertiary"
      type="button"
      onclick="{goToHomepage}"
      data-testid="skip-button"
    >
      Peut-être plus tard
    </button>
  </div>
</div>

<style>
  .notifications-welcome-page {
    padding: 1.5rem 1rem;
    margin-top: 9rem;

    .image-wrapper {
      display: flex;
      justify-content: center;
      margin-bottom: 1rem;
    }
    h1 {
      margin-bottom: 0.5rem;
      font-size: 22px;
      line-height: 1.75rem;
      font-weight: 700;
    }
    .descriptive-text {
      margin-bottom: 2.5rem;
      font-size: 1rem;
      line-height: 1.5rem;
      font-weight: 400;
    }

    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 1rem;

      button {
        display: flex;
        justify-content: center;
        width: 100%;
      }
    }
  }
</style>
