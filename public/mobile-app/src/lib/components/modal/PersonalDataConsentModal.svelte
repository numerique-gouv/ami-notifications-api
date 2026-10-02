<script lang="ts">
  import type { MouseEventHandler } from 'svelte/elements';
  import BottomModal from '$lib/components/modal/BottomModal.svelte';
  import {
    buildPersonalDataConsent,
    PersonalDataConsent,
  } from '$lib/personal-data-consent';
  import { toastStore } from '$lib/state/toast.svelte.js';

  interface Props {
    displayPersonalDataConsentBlock?: boolean;
    displayModal: boolean;
    onClose?: (hasAccepted: boolean) => void | null;
  }
  let {
    displayPersonalDataConsentBlock = $bindable(),
    displayModal = $bindable(),
    onClose,
  }: Props = $props();

  const acceptAndCloseModal = async () => {
    const personalDataConsent: PersonalDataConsent = await buildPersonalDataConsent();
    await personalDataConsent.updateConsent(true);
    displayPersonalDataConsentBlock = false;
    toastStore.addToast(
      'Vos données administratives sont à présent utilisées dans l’application',
      'success',
      3000,
      false
    );
    closeModal(true);
  };

  const dismissAndCloseModal = () => {
    closeModal(false);
  };

  const closeModal = (hasAccepted: boolean = false) => {
    displayModal = false;
    if (onClose) {
      onClose(hasAccepted);
    }
  };
</script>

<BottomModal onClose={closeModal}>
  {#snippet modalContent()}
    <div>
      Utiliser mes données administratives
      <ul>
        <li>
          <button type="button" onclick={acceptAndCloseModal}>Accepter</button>
        </li>
        <li>
          <button type="button" onclick={dismissAndCloseModal}>
            Accepter plus tard
          </button>
        </li>
      </ul>
    </div>
  {/snippet}
</BottomModal>

<style>
</style>
