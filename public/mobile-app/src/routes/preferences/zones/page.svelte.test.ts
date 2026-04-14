import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
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
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should enable zone when user toggles on', async () => {
    // Given
    await userStore.login(mockUserInfo);
    render(Page);

    // When
    const toggleInput = screen.getByTestId('Martinique');
    await fireEvent.click(toggleInput);

    // Then
    expect(userStore.connected?.identity.preferences.zones).toEqual([
      'Zone A',
      'Zone B',
      'Zone C',
      'Corse',
      'Martinique',
    ]);
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
    expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
  });

  test('should disable zone when user toggles off', async () => {
    // Given
    await userStore.login(mockUserInfo);
    render(Page);

    // When
    const toggleInput = screen.getByTestId('Zone C');
    await fireEvent.click(toggleInput);

    // Then
    expect(userStore.connected?.identity.preferences.zones).toEqual([
      'Zone A',
      'Zone B',
      'Corse',
    ]);
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
    expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
  });

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page);
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Zones scolaires')).toBeInTheDocument();
  });

  test('should navigate to previous page when user clicks on Close button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const backSpy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);
    const closeButton = screen.getByTestId('close-button');
    await fireEvent.click(closeButton);

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1);
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });
});
