import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
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

  test('should set token in localStorage', async () => {
    // Given
    const { page } = await import('$app/state');
    vi.spyOn(navigationMethods, 'goto').mockImplementation(() => Promise.resolve());
    const mockSearchParams = new URLSearchParams({
      is_logged_in: 'true',
      id_token: 'fake-id-token',
    });
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(window.localStorage.getItem('id_token')).toEqual('fake-id-token');
    });
  });
  test('should redirect to redirect_url as redirect_url is provided', async () => {
    // Given
    const { page } = await import('$app/state');
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    const mockSearchParams = new URLSearchParams({
      redirect_url: 'http://foo.bar',
    });
    vi.stubGlobal('location', { href: 'fake-link' });
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).not.toHaveBeenCalled();
      expect(globalThis.window.location.href).toEqual('http://foo.bar');
    });
  });
  test('should redirect to home as redirect_url is not provided', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
});
