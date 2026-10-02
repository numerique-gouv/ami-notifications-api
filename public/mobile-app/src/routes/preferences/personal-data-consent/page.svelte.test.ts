import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as personalDataConsentMethods from '$lib/personal-data-consent';
import { PersonalDataConsent } from '$lib/personal-data-consent';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  describe('When user toggles on', () => {
    test('should enable personal-data-consent', async () => {
      // Given
      await userStore.login(mockUserInfo);

      const apiPersonalDataConsent = { consent_datetime: null };
      const personalDataConsent = new PersonalDataConsent(apiPersonalDataConsent);
      vi.spyOn(
        personalDataConsentMethods,
        'buildPersonalDataConsent'
      ).mockResolvedValue(personalDataConsent);

      const spy = vi
        .spyOn(personalDataConsent, 'updateConsent')
        .mockResolvedValue(true);

      await render(Page);

      // When
      const toggleInput: HTMLInputElement = screen.getByTestId(
        'personal-data-consent-toggle'
      );
      expect(toggleInput.checked).toBeFalsy();
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith(true);
      });
    });
  });

  describe('When user toggles off', () => {
    test('should disable personal-data-consent', async () => {
      // Given
      await userStore.login(mockUserInfo);

      const apiPersonalDataConsent = { consent_datetime: null };
      const personalDataConsent = new PersonalDataConsent(apiPersonalDataConsent);
      vi.spyOn(
        personalDataConsentMethods,
        'buildPersonalDataConsent'
      ).mockResolvedValue(personalDataConsent);

      const spy = vi
        .spyOn(personalDataConsent, 'updateConsent')
        .mockResolvedValue(true);

      await render(Page);

      // When
      let toggleInput: HTMLInputElement = screen.getByTestId(
        'personal-data-consent-toggle'
      );
      expect(toggleInput.checked).toBeFalsy();
      await fireEvent.click(toggleInput);

      toggleInput = screen.getByTestId('personal-data-consent-toggle');
      expect(toggleInput.checked).toBeTruthy();
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith(true);
      });
    });
  });

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page);
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Consentement données personnelles')).toBeInTheDocument();
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });
});
