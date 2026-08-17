import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import * as franceConnectHelpers from '$lib/france-connect';
import * as initializeDataFromAPIMethods from '$lib/initializeDataFromAPI';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(() => {
    originalWindow = globalThis.window;
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
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    const spy = vi
      .spyOn(initializeDataFromAPIMethods, 'initializeLocalStorage')
      .mockResolvedValue();
    vi.spyOn(navigationMethods, 'goto').mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalled();
    });
  });

  test('should navigate to notifications welcome page when it is the first user login', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('user_first_login', 'true');
    window.localStorage.setItem('user_data', 'fake-user-data');
    const spyParseJwt = vi
      .spyOn(franceConnectHelpers, 'parseJwt')
      .mockReturnValue(mockUserInfo);
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
    const spyParseJwt = vi
      .spyOn(franceConnectHelpers, 'parseJwt')
      .mockReturnValue(mockUserInfo);
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
