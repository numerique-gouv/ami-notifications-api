import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as envModule from '$env/static/public';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as franceConnectHelpers from '$lib/france-connect';
import * as initializeDataFromAPIMethods from '$lib/initializeDataFromAPI';
import * as notificationsMethods from '$lib/notifications';
import * as passkeyMethods from '$lib/passkey';
import { PasskeyError, PasskeyNetworkError } from '$lib/passkey';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

vi.mock('@simplewebauthn/browser', () => ({
  startRegistration: vi.fn(),
}));

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED: 'false',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
    userStore.connected = null;
  });

  test('should initialize data in localStorage when user is logged in', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    window.localStorage.setItem('user_data', 'fake-user-data');
    vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    const spy = vi
      .spyOn(initializeDataFromAPIMethods, 'initializeLocalStorage')
      .mockResolvedValue();
    const initializeDataSpy = vi
      .spyOn(initializeDataFromAPIMethods, 'initializeData')
      .mockResolvedValue();

    vi.spyOn(AMINavigationMethods, 'AMIGoto').mockImplementation(() =>
      Promise.resolve()
    );

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalled();
      expect(initializeDataSpy).toHaveBeenCalled();
    });
  });

  test('should navigate to homepage when user has already logged in', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    window.localStorage.setItem('user_data', 'fake-user-data');
    vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    vi.spyOn(initializeDataFromAPIMethods, 'initializeData').mockResolvedValue();
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    render(Page);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/welcome/zones');
    });
  });

  test('should navigate to login screen when user is not logged in', async () => {
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    render(Page);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('should navigate to URL in login_redirect_url parameter if given', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('login_redirect_url', 'https://www.example.org');
    window.localStorage.setItem('user_data', 'fake-user-data');
    vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    vi.spyOn(initializeDataFromAPIMethods, 'initializeData').mockResolvedValue();
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('https://www.example.org');
    });
  });
});

// tests with passkeys enabled
describe('/+page.svelte - with passkey feature flag', () => {
  beforeEach(() => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED: 'true',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'true';
  });

  describe('passkey creation', async () => {
    test('should display passkey error toast on PasskeyError', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());
      vi.spyOn(passkeyMethods, 'registerPasskey').mockRejectedValue(new PasskeyError());

      const spyToast = vi.spyOn(toastStore, 'addToast');

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        const createPasskeyButton = screen.getByTestId('create-passkey-button');
        await fireEvent.click(createPasskeyButton);
        expect(spy).not.toHaveBeenCalled();
        expect(spyToast).toHaveBeenCalledWith(
          'Erreur lors de l’ajout de votre clé d’accès',
          'error',
          3000,
          false
        );
      });
    });
    test('should display network error toast on PasskeyNetworkError', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());
      vi.spyOn(passkeyMethods, 'registerPasskey').mockRejectedValue(
        new PasskeyNetworkError()
      );

      const spyToast = vi.spyOn(toastStore, 'addToast');

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        const createPasskeyButton = screen.getByTestId('create-passkey-button');
        await fireEvent.click(createPasskeyButton);
        expect(spy).not.toHaveBeenCalled();
        expect(spyToast).toHaveBeenCalledWith(
          'Problème de connexion Internet, veuillez réessayer',
          'error',
          3000,
          false
        );
      });
    });
    test('should create a passkey when appropriate button is clicked', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());
      vi.spyOn(passkeyMethods, 'registerPasskey').mockResolvedValue(undefined);

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        const createPasskeyButton = screen.getByTestId('create-passkey-button');
        await fireEvent.click(createPasskeyButton);
        // check user store registered that the user has a passkey
        expect(userStore.getHasWorkingPasskey()).toBe(true);

        expect(spy).toHaveBeenCalledWith('/?passkey_toast=true#/welcome/zones');
      });
    });
  });

  describe('skip passkey creation', async () => {
    test('should bypass passkey creation if user clicks on bypass button', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockResolvedValue([]);
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      expect(userStore.getHasSuggestPasskeyCreationToday()).toBe(false);

      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        const bypassPasskeyButton = screen.getByTestId('bypass-passkey-button');
        await fireEvent.click(bypassPasskeyButton);
        expect(spy).toHaveBeenCalledWith('/#/welcome/zones');
        expect(userStore.getHasSuggestPasskeyCreationToday()).toBe(true);
      });
    });

    test('should skip passkey creation if user already has one', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockResolvedValue([]);
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      userStore.setHasWorkingPasskey();

      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(Page);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledWith('/#/welcome/zones');
        expect(screen.queryByTestId('create-passkey-button')).toBeNull();
      });
    });

    test('should skip passkey creation if we already asked it today', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockResolvedValue([]);
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      userStore.setLastPasskeyCreationSuggestion();
      expect(userStore.getHasSuggestPasskeyCreationToday()).toBe(true);

      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(Page);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledWith('/#/welcome/zones');
        expect(screen.queryByTestId('create-passkey-button')).toBeNull();
      });
    });

    test('should not skip passkey creation if never asked', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockResolvedValue([]);
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      // When
      render(Page);

      // Then
      await waitFor(() => {
        expect(screen.queryByTestId('create-passkey-button')).not.toBeNull();
      });
    });

    test('should not skip passkey creation if not already asked today', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockResolvedValue([]);
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams();
      window.localStorage.setItem('user_data', 'fake-user-data');
      vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      const yesterday = new Date(Date.now() - 86400000);
      localStorage.setItem('user_last_passkey_suggestion', yesterday.toString());

      // When
      render(Page);

      // Then
      await waitFor(() => {
        expect(screen.queryByTestId('create-passkey-button')).not.toBeNull();
      });
    });
  });
});
