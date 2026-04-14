<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import { runOrNativeEvent } from '$lib/nativeEvents';
  import {
    disableNotifications,
    enableNotificationsAndUpdateLocalStorage,
  } from '$lib/notifications';
  import type { Registration } from '$lib/registration';
  import { userStore } from '$lib/state/User.svelte';

  let backUrl: string = '/#/preferences';
  let registration: Registration | null = $state(null);
  let isChecked = $state(false);

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }

    isChecked = localStorage.getItem('notifications_enabled') === 'true';
  });

  const navigateToPreviousPage = async () => {
    goto(backUrl);
  };

  const enableNotificationsFunc = async () => {
    registration = await enableNotificationsAndUpdateLocalStorage();
  };

  const disableNotificationsFunc = async () => {
    let registrationId: string | null = null;
    if (registration) {
      registrationId = registration.id;
    } else if (localStorage.getItem('registration_id')) {
      registrationId = localStorage.getItem('registration_id');
    } else {
      console.log('no registration');
    }

    if (registrationId) {
      await disableNotifications(registrationId);
      localStorage.setItem('registration_id', '');
      localStorage.setItem('notifications_enabled', 'false');
    }
  };
  const saveSettings = async (id: string, checked: boolean) => {
    if (checked) {
      runOrNativeEvent(enableNotificationsFunc, 'notification_permission_requested');
    } else {
      runOrNativeEvent(disableNotificationsFunc, 'notification_permission_removed');
    }
  };
</script>

<div class="preferences-page">
  <NavWithBackButton title="Notifications" {backUrl} />

  <div class="preferences-content-container">
    <Toggle
      id="notification-toggle"
      label="Recevoir les notifications sur mon appareil mobile"
      isChecked={isChecked}
      onChangeAction={saveSettings}
    />
  </div>

  <button
    class="fr-btn fr-btn--secondary fr-btn--lg save-preferences-button"
    type="button"
    onclick={navigateToPreviousPage}
    title="Retour à la page précédente"
    aria-label="Retour à la page précédente"
    data-testid="close-button"
  >
    Fermer
  </button>
</div>

<style>
  .preferences-page {
    .save-preferences-button {
      position: fixed;
      bottom: 1rem;
      left: 50%;
      transform: translateX(-50%);

      display: block;
      width: 328px;
    }
  }
</style>
