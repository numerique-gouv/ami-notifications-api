<script lang="ts">
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
    const personalDataConsent: PersonalDataConsent = new PersonalDataConsent({
      consent_datetime: null,
    });
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
    <div data-testid="personal-data-consent-modal">
      <h2 class="fr-h4 fr-mb-2w">Utiliser mes données administratives</h2>
      <p>
        L’application peut utiliser vos données pour
        <strong>préremplir vos demandes</strong> et
        <strong>personnaliser votre profil</strong>.
      </p>
      <ul class="fr-list fr-mb-3w">
        <li>Nom de famille</li>
        <li>Nom d’usage</li>
        <li>Prénom(s)</li>
        <li>Sexe</li>
        <li>Date de naissance</li>
        <li>Lieu de naissance</li>
        <li>Pays de naissance</li>
        <li>Adresse e-mail</li>
        <li>Adresse</li>
      </ul>
      <div>
        <button
          type="button"
          class="fr-btn fr-mb-1w fr-btn--lg am-btn-w100"
          data-testid="accept-button"
          onclick={acceptAndCloseModal}
        >
          Accepter
        </button>
        <button
          type="button"
          class="fr-btn fr-btn--secondary fr-btn--lg am-btn-w100"
          data-testid="dismiss-button"
          onclick={dismissAndCloseModal}
        >
          Accepter plus tard
        </button>
      </div>
    </div>
  {/snippet}
</BottomModal>

<style>
</style>
