import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(() => {
    originalWindow = globalThis.window;
  });

  afterEach(() => {
    globalThis.window = originalWindow;
    vi.resetAllMocks();
  });

  test('should go to login page if ?is_logged_out is present', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('is_logged_out');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/?is_logged_out#/login');
    });
  });

  test('should get out if user is not connected', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('should add toast when user does not match after relogin - without redirect', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('user_does_not_match');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const spy = vi.spyOn(toastStore, 'addToast');
    const spy2 = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
        'warning',
        null,
        true
      );
      expect(spy2).not.toHaveBeenCalled();
    });
  });

  test('should add toast when user does not match after relogin - with redirect', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('user_does_not_match');
    mockSearchParams.set('redirect_to_hash', '/page');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const spy = vi.spyOn(toastStore, 'addToast');
    const spy2 = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
        'warning',
        null,
        true
      );
      expect(spy2).toHaveBeenCalledWith('/#/page');
    });
  });
});
