import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { PersonalDataConsent } from '$lib/personal-data-consent';
import { toastStore } from '$lib/state/toast.svelte';
import PersonalDataConsentModal from './PersonalDataConsentModal.svelte';

describe('/PersonalDataConsentModal.svelte', () => {
  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();
  });

  test('should add toast when user clicks on "Accepter" button', async () => {
    // Given
    const apiPersonalDataConsent = { consent_datetime: null };
    const personalDataConsent = new PersonalDataConsent(apiPersonalDataConsent);
    vi.spyOn(personalDataConsent, 'updateConsent').mockResolvedValue(true);
    const spy = vi.spyOn(toastStore, 'addToast');

    const displayPersonalDataConsentBlock: boolean = false;
    const displayModal: boolean = false;
    const onClose = vi.fn();
    render(PersonalDataConsentModal, {
      props: { displayPersonalDataConsentBlock, displayModal, onClose },
    });

    // When
    await waitFor(async () => {
      const acceptButton = screen.getByTestId('accept-button');
      await fireEvent.click(acceptButton);
    });

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'Vos données administratives sont à présent utilisées dans l’application',
        'success',
        3000,
        false
      );
      expect(onClose).toHaveBeenCalledWith(true);
    });
  });

  test('should call callback close function with false when user clicks on "Accepter plus tard" button', async () => {
    // Given
    const apiPersonalDataConsent = { consent_datetime: null };
    const personalDataConsent = new PersonalDataConsent(apiPersonalDataConsent);
    vi.spyOn(personalDataConsent, 'updateConsent').mockResolvedValue(true);
    const spy = vi.spyOn(toastStore, 'addToast');

    const displayPersonalDataConsentBlock: boolean = false;
    const displayModal: boolean = false;
    const onClose = vi.fn();
    render(PersonalDataConsentModal, {
      props: { displayPersonalDataConsentBlock, displayModal, onClose },
    });

    // When
    await waitFor(async () => {
      const dismissButton = screen.getByTestId('dismiss-button');
      await fireEvent.click(dismissButton);
    });

    // Then
    await waitFor(async () => {
      expect(spy).not.toHaveBeenCalled();
      expect(onClose).toHaveBeenCalledWith(false);
    });
  });
});
