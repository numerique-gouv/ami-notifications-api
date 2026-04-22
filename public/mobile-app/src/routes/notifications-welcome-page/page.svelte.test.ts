import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as notificationsMethods from '$lib/notifications';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mock('$lib/notifications', () => ({
      enableNotificationsAndUpdateLocalStorage: vi.fn().mockReturnValue(true),
    }));
  });

  test('user has to be connected', async () => {
    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(window.location.href).toEqual('/');
    });
  });

  test('should enable notifications when user clicks on Activer button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const spy = vi.spyOn(
      notificationsMethods,
      'enableNotificationsAndUpdateLocalStorage'
    );
    render(Page);

    // When
    const button = screen.getByTestId('enable-button');
    await fireEvent.click(button);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalled();
    });
  });

  test('should add toast when user clicks on Activer button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const spy = vi.spyOn(toastStore, 'addToast');
    render(Page);

    // When
    const button = screen.getByTestId('enable-button');
    await fireEvent.click(button);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('Les notifications ont été activées', 'success');
    });
  });

  test('should navigate to the homepage when user clicks on Activer button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    render(Page);

    // When
    const button = screen.getByTestId('enable-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(window.location.href).toEqual('/');
    });
  });

  test('should navigate to the homepage when user clicks on Skip button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    render(Page);

    // When
    const button = screen.getByTestId('skip-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(window.location.href).toEqual('/');
    });
  });
});
