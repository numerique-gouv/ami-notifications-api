import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import { PUBLIC_API_URL } from '$env/static/public';
import * as franceConnectHelpers from '$lib/france-connect';
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

  describe('user is logged in', () => {
    test('should set token in localStorage', async () => {
      // Given
      const { page } = await import('$app/state');
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

    test('should not display api_particulier_quotient value if value is not base64 encoded', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        api_particulier_quotient: 'wrong',
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('api_particulier_quotient')).toBeNull();
      });
    });

    test('should not display api_particulier_quotient value if value is not a json base64 encoded', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        api_particulier_quotient: btoa('wrong'),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('api_particulier_quotient')).toBeNull();
      });
    });

    test('should not display api_particulier_quotient value if value is an empty json base64 encode', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        api_particulier_quotient: btoa('{}'),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('api_particulier_quotient')).toBeNull();
      });
    });

    test('should display api_particulier_quotient', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        api_particulier_quotient: btoa(JSON.stringify({ foo: 'bar' })),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.getByTestId('api_particulier_quotient')).toHaveTextContent(
          '"foo": "bar"'
        );
      });
    });
  });

  describe('user wants to login again', () => {
    test('should call authorize endpoint when click on login button', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 200 })
      );
      vi.stubGlobal('location', { href: 'fake-link' });

      render(Page);
      await waitFor(() => {
        const loginButton = screen.getByRole('button', {
          name: 'Test AMI-FI',
        });

        // When
        loginButton.click();

        // Then
        expect(globalThis.window.location.href).toContain(
          `${PUBLIC_API_URL}/login-ami-fi`
        );
      });
    });

    test('should call logout endpoint when click on login button as a token is stored in localstorage', async () => {
      // Given
      globalThis.localStorage.setItem('id_token', 'fake-id-token');
      const spyFranceConnectLogout = vi
        .spyOn(franceConnectHelpers, 'franceConnectLogout')
        .mockResolvedValue();

      render(Page);
      await waitFor(() => {
        const loginButton = screen.getByRole('button', {
          name: 'Test AMI-FI',
        });

        // When
        loginButton.click();

        // Then
        expect(spyFranceConnectLogout).toHaveBeenCalledWith(
          'fake-id-token',
          `${PUBLIC_API_URL}/login-ami-fi`
        );
      });
    });
  });
});
