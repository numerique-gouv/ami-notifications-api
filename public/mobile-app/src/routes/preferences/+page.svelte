<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Modal from '$lib/components/modal/Modal.svelte';
  import ZonePreferences from '$lib/components/modal/ZonePreferences.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { runOrNativeEvent } from '$lib/nativeEvents';
  import {
    disableNotifications,
    enableNotificationsAndUpdateLocalStorage,
  } from '$lib/notifications';
  import type { Registration } from '$lib/registration';
  import { userStore } from '$lib/state/User.svelte';

  type ModalInstance = {
    open: () => Promise<void>;
  };

  let backUrl: string = '/';
  let zonePreferencesModal: ModalInstance;

  onMount(async () => {
    if (!userStore.connected) {
      goto('/');
    }
  });

  const navigateToPreviousPage = async () => {
    goto(backUrl);
  };

  const openZonePreferencesModal = () => {
    zonePreferencesModal.open();
  };
</script>

<div class="preferences-page">
  <NavWithBackButton title="Préférences" {backUrl} />

  <div class="preferences-content-container">
    <nav class="fr-sidemenu" aria-labelledby="fr-sidemenu-title">
      <div class="fr-sidemenu__inner">
        <div id="fr-sidemenu-wrapper">
          <ul class="fr-sidemenu__list">
            <li class="fr-sidemenu__item">
              <a
                class="fr-sidemenu__link"
                href="/#/preferences/notifications"
                target="_self"
                ><span class="label">Notifications</span>
                <span aria-hidden="true" class="icon fr-icon-arrow-right-s-line"></span>
              </a>
            </li>
            <li class="fr-sidemenu__item">
              <button
                class="fr-sidemenu__link"
                type="button"
                onclick={openZonePreferencesModal}
              >
                <span class="label">Zones scolaires</span>
                <span aria-hidden="true" class="icon fr-icon-arrow-right-s-line"></span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</div>

<Modal
  bind:this={zonePreferencesModal}
  id="modal-zones-preferences"
  title="Zones scolaires"
  component={ZonePreferences}
/>

<style>
  .preferences-page {
    .fr-sidemenu {
      padding: 1rem;
      box-shadow: none;
      margin: 0;
      .fr-sidemenu__item {
        .fr-sidemenu__link {
          padding: 1.5rem 0;
          font-weight: 500;
          color: #000;
          --hover-tint: none;
          --active-tint: none;
          justify-content: space-between;
          span.icon {
            color: var(--text-active-blue-france);
          }
        }
        &:last-child::before {
          box-shadow:
            0 -1px 0 0 var(--border-default-grey),
            inset 0 -1px 0 0 var(--border-default-grey);
        }
      }
    }
  }
</style>
