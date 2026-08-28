import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import type { APIConsents } from '$lib/api-consents';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('should enable consent when user toggles on', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const apiConsents: APIConsents = { consents: [] };
    const consents: Consents = new Consents(apiConsents);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

    const spy = vi.spyOn(consentsMethods, 'updateConsent');
    render(Page);

    // When
    const toggleInput: HTMLInputElement = screen.getByTestId('psl');
    expect(toggleInput.checked).toBeFalsy();
    await fireEvent.click(toggleInput);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('psl', true);
    });
  });

  test('should disable consent when user toggles off', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const spy = vi.spyOn(consentsMethods, 'updateConsent');
    render(Page);
    const toggleInput: HTMLInputElement = screen.getByTestId('psl');
    await fireEvent.click(toggleInput); // set toggle to checked

    // When
    expect(toggleInput.checked).toBeTruthy();
    await fireEvent.click(toggleInput);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('psl', false);
    });
  });

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page);
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Suivi des démarches')).toBeInTheDocument();
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });
});
