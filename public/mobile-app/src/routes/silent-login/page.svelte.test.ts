import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, waitFor } from '@testing-library/svelte';
import * as AMIGotoMethods from '$lib/ami-goto';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  afterEach(() => {
    vi.resetAllMocks();
  });

  test('should set token in localStorage', async () => {
    // Given
    const { page } = await import('$app/state');
    vi.spyOn(AMIGotoMethods, 'AMIGoto').mockImplementation(() => Promise.resolve());
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
      .spyOn(AMIGotoMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const mockSearchParams = new URLSearchParams({
      redirect_url: 'http://foo.bar',
    });
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('http://foo.bar');
    });
  });
  test('should redirect to home as redirect_url is not provided', async () => {
    // Given
    const spy = vi
      .spyOn(AMIGotoMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
});
