import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import * as franceConnectHelpers from '$lib/france-connect';
import * as initializeDataFromAPIMethods from '$lib/initializeDataFromAPI';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(() => {
    originalWindow = globalThis.window;
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

  afterEach(() => {
    globalThis.window = originalWindow;
    vi.resetAllMocks();
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

    vi.spyOn(navigationMethods, 'goto').mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalled();
      expect(initializeDataSpy).toHaveBeenCalled();
    });
  });

  test('should navigate to notifications welcome page when it is the first user login', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('user_first_login', 'true');
    window.localStorage.setItem('user_data', 'fake-user-data');
    vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    vi.spyOn(initializeDataFromAPIMethods, 'initializeData').mockResolvedValue();
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/welcome/zones');
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
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    render(Page);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should navigate to login screen when user is not logged in', async () => {
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    render(Page);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });
});

// tests with passkeys enabled
describe('/+page.svelte - with passkey', () => {
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

  afterEach(() => {
    vi.resetAllMocks();
  });

  test('should create a passkey when appropriate button is clicked', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    window.localStorage.setItem('user_data', 'fake-user-data');
    vi.spyOn(franceConnectHelpers, 'parseJwt').mockReturnValue(mockUserInfo);
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    const fetchSpy = vi
      .spyOn(globalThis, 'fetch')
      .mockImplementation((input: RequestInfo | URL) => {
        const url =
          typeof input === 'string'
            ? input
            : input instanceof URL
              ? input.href
              : input.url;
        if (url.includes('generate-registration-options')) {
          return Promise.resolve(
            new Response(JSON.stringify({ fake: 'option' }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            })
          );
        }
        if (url.includes('verify-registration')) {
          return Promise.resolve(
            new Response(JSON.stringify({ verified: true }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' },
            })
          );
        }
        // Default fallback
        return Promise.resolve(
          new Response(JSON.stringify({}), {
            status: 404,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      });

    // @ts-expect-error
    vi.mock(import('@simplewebauthn/browser'), () => {
      return {
        startRegistration: (opts) => {
          return opts;
        },
      };
    });

    // When
    render(Page);

    // Then
    const createPasskeyButton = screen.getByTestId('create-passkey-button');
    await fireEvent.click(createPasskeyButton);
    await waitFor(async () => {
      // check call is made with connected user name
      expect(fetchSpy).toHaveBeenCalledWith(
        '/api/v1/fi/passkey/generate-registration-options',
        {
          body: '{"displayName":"Angela Claire Louise DUBOIS"}',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
      // check call is made with options returned by mocked startRegistration
      expect(fetchSpy).toHaveBeenCalledWith('/api/v1/fi/passkey/verify-registration', {
        body: '{"optionsJSON":{"fake":"option"}}',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });

      expect(spy).toHaveBeenCalledWith('/?passkey_toast=true');
    });
  });
});
