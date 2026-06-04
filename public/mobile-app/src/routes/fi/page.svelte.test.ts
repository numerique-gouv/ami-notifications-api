import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import { PUBLIC_API_URL } from '$env/static/public';
import * as franceConnectHelpers from '$lib/france-connect';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(() => {
    originalWindow = globalThis.window;

    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_API_URL: 'https://localhost:8000',
        PUBLIC_FEATURE_FLAG_FI_LOGIN_ENABLED: 'true',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_FI_LOGIN_ENABLED = 'true';
  });

  afterEach(() => {
    globalThis.window = originalWindow;
    vi.resetAllMocks();
  });

  describe('user is logged in', () => {
    test('Should redirect to home if feature flag is not enabled', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FEATURE_FLAG_FI_LOGIN_ENABLED = 'false';
      const spy = vi
        .spyOn(navigationMethods, 'goto')
        .mockImplementation(() => Promise.resolve());
      render(Page);

      // When
      render(Page);

      // Then
      expect(spy).toHaveBeenCalledWith('/');
    });
    test('Should not redirect to home if feature flag is enabled', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FEATURE_FLAG_FI_LOGIN_ENABLED = 'true';
      const spy = vi
        .spyOn(navigationMethods, 'goto')
        .mockImplementation(() => Promise.resolve());
      render(Page);

      // When
      render(Page);

      // Then
      expect(spy).not.toHaveBeenCalled();
    });
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

    test('should not display data value if value is not base64 encoded', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        data: 'wrong',
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"data": "DATA"}', { status: 200 })
      );

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('data')).toBeNull();
      });
    });

    test('should not display data value if value is not a json base64 encoded', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        data: btoa('wrong'),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"data": "DATA"}', { status: 200 })
      );

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('data')).toBeNull();
      });
    });

    test('should not display data value if value is an empty json base64 encode', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        data: btoa('{}'),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"data": "DATA"}', { status: 200 })
      );

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('data')).toBeNull();
      });
    });

    test('should not display data if not in providers', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        data: btoa(JSON.stringify({ foo: 'bar' })),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"}', { status: 200 })
      );

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.queryByTestId('data')).toBeNull();
      });
    });

    test('should display data', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        data: btoa(JSON.stringify({ foo: 'bar' })),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"data": "DATA"}', { status: 200 })
      );

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.getByTestId('data')).toHaveTextContent('"foo": "bar"');
      });
    });
  });

  describe('providers', () => {
    test('should display_providers', async () => {
      // Given
      const { page } = await import('$app/state');
      const mockSearchParams = new URLSearchParams({
        is_logged_in: 'true',
        data: btoa(JSON.stringify({ foo: 'bar' })),
      });
      vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(
          '{"api_particulier_quotient": "Quotient", "api_particulier_statut_etudiant": "Etudiant"}',
          { status: 200 }
        )
      );

      // When
      render(Page);

      // Then
      await waitFor(async () => {
        expect(screen.getByTestId('radio-api_particulier_quotient')).toHaveTextContent(
          'Quotient'
        );
        expect(
          screen.getByTestId('radio-api_particulier_statut_etudiant')
        ).toHaveTextContent('Etudiant');
        const radios = screen.getAllByRole('radio') as HTMLInputElement[];
        expect(radios.find((r) => r.checked)?.value).toBe('api_particulier_quotient');
      });
    });
  });

  describe('user wants to login again', () => {
    test('should call authorize endpoint when click on login button', async () => {
      // Given
      vi.stubGlobal('location', { href: 'fake-link' });
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"api_particulier_statut_etudiant": "Etudiant"}', { status: 200 })
      );

      render(Page);
      await waitFor(() => {
        const loginButton = screen.getByRole('button', {
          name: 'Test AMI-FI',
        });

        // When
        loginButton.click();

        // Then
        expect(globalThis.window.location.href).toContain(
          `${PUBLIC_API_URL}/login-ami-fi?provider_id=api_particulier_statut_etudiant`
        );
      });
    });

    test('should call logout endpoint when click on login button as a token is stored in localstorage', async () => {
      // Given
      globalThis.localStorage.setItem('id_token', 'fake-id-token');
      const spyFranceConnectLogout = vi
        .spyOn(franceConnectHelpers, 'franceConnectLogout')
        .mockResolvedValue();
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{"api_particulier_quotient": "Quotient"}', { status: 200 })
      );

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
          `${PUBLIC_API_URL}/login-ami-fi?provider_id=api_particulier_quotient`
        );
      });
    });
  });
});
