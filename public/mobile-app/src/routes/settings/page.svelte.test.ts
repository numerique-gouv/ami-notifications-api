import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as notificationsMethods from '$lib/notifications';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mock('$lib/notifications', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, any>;
      const registration = { id: 'fake-registration-id' };
      return {
        ...original,
        enableNotificationsAndUpdateLocalStorage: vi.fn(() =>
          Promise.resolve(registration)
        ),
        disableNotifications: vi.fn(() => Promise.resolve()),
      };
    });
  });

  test('user has to be connected', async () => {
    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(window.location.href).toEqual('/');
    });
  });

  test('should enable notifications when user toggles on', async () => {
    // Given
    const spy = vi.spyOn(
      notificationsMethods,
      'enableNotificationsAndUpdateLocalStorage'
    );
    render(Page);

    // When
    const toggleInput = screen.getByTestId('toggle-input');
    await fireEvent.click(toggleInput);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalled();
    });
  });

  test('should disable notifications when user toggles off', async () => {
    // Given
    const spy = vi.spyOn(notificationsMethods, 'disableNotifications');
    window.localStorage.setItem('registration_id', 'fake-registration-id');
    window.localStorage.setItem('notifications_enabled', 'true');
    render(Page);

    // When
    const toggleInput = screen.getByTestId('toggle-input');
    await fireEvent.click(toggleInput);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('fake-registration-id');
      expect(window.localStorage.getItem('registration_id')).toEqual('');
      expect(window.localStorage.getItem('notifications_enabled')).toEqual('false');
    });
  });

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page);
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Paramètres')).toBeInTheDocument();
  });

  test('should navigate to previous page when user clicks on Close button', async () => {
    // Given
    await userStore.login(mockUserInfo);

    // When
    render(Page);
    const closeButton = screen.getByTestId('close-button');
    await fireEvent.click(closeButton);

    // Then
    expect(window.location.href).toEqual('/');
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });
});
