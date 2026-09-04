import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import type { AuthenticationResponseJSON } from '@simplewebauthn/browser';
import * as simplewebauthnMethods from '@simplewebauthn/browser';
import { render, screen, waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { userStore } from '$lib/state/User.svelte';
import Page from './+page.svelte';

vi.mock('@simplewebauthn/browser', () => ({
  startAuthentication: vi.fn(),
}));

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(() => {
    originalWindow = globalThis.window;
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();
  });

  afterEach(() => {
    globalThis.window = originalWindow;
  });

  test('should display passkey error message and bypass button on options response error', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('{}', { status: 400 })
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    const networkErrorMessage = await screen.queryByText(
      'Problème de connexion Internet, veuillez réessayer'
    );
    expect(networkErrorMessage).toBeNull();
    const passkeyErrorMessage = await screen.queryByText(
      'Erreur lors de l’utilisation de votre clé d’accès'
    );
    expect(passkeyErrorMessage).not.toBeNull();

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display network error message and bypass button on options TypeError', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError());
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    const networkErrorMessage = await screen.queryByText(
      'Problème de connexion Internet, veuillez réessayer'
    );
    expect(networkErrorMessage).not.toBeNull();
    const passkeyErrorMessage = await screen.queryByText(
      'Erreur lors de l’utilisation de votre clé d’accès'
    );
    expect(passkeyErrorMessage).toBeNull();

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button on options error', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error());
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    const networkErrorMessage = await screen.queryByText(
      'Problème de connexion Internet, veuillez réessayer'
    );
    expect(networkErrorMessage).toBeNull();
    const passkeyErrorMessage = await screen.queryByText(
      'Erreur lors de l’utilisation de votre clé d’accès'
    );
    expect(passkeyErrorMessage).not.toBeNull();

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button on startAuthentication error', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('{}', { status: 200 })
    );
    vi.mocked(simplewebauthnMethods.startAuthentication).mockRejectedValue(new Error());
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).not.toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button on verify response error with retry', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ retry: true }), { status: 400 })
      );
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).not.toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button on verify response error', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockResolvedValueOnce(new Response('{}', { status: 400 }));
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).not.toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('back');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/');
    expect(unsetHasWorkingPasskeySpy).not.toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button on verify response error - with redirect_to_hash param', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('user_does_not_match');
    mockSearchParams.set('redirect_to_hash', '/page');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockResolvedValueOnce(new Response('{}', { status: 400 }));
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).not.toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('back');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/page');
    expect(unsetHasWorkingPasskeySpy).not.toHaveBeenCalled();
  });
  test('should display network error message and bypass button on verify Type', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockRejectedValueOnce(new TypeError());
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).not.toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button on verify error', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockRejectedValueOnce(new Error());
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).not.toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should display passkey error message and bypass button when user is not authenticated', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ verified: false }), { status: 200 })
      );
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).not.toBeNull();
    });

    await waitFor(() => {
      const bypass = screen.getByTestId('bypass-passkey');
      bypass.click();
    });
    expect(spy).toHaveBeenCalledWith('/#/relogin');
    expect(unsetHasWorkingPasskeySpy).toHaveBeenCalled();
  });
  test('should redirect when user is authenticated', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(new Response('{}', { status: 200 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ verified: true, redirect_uri: 'fake-redirect-uri' }),
          { status: 200 }
        )
      );
    vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
      {} as AuthenticationResponseJSON
    );
    vi.stubGlobal('location', { href: 'fake-link' });
    render(Page);

    // When
    await waitFor(() => {
      const button = screen.getByTestId('use-passkey');
      button.click();
    });

    // Then
    await waitFor(async () => {
      const networkErrorMessage = await screen.queryByText(
        'Problème de connexion Internet, veuillez réessayer'
      );
      expect(networkErrorMessage).toBeNull();
      const passkeyErrorMessage = await screen.queryByText(
        'Erreur lors de l’utilisation de votre clé d’accès'
      );
      expect(passkeyErrorMessage).toBeNull();

      expect(globalThis.window.location.href).toEqual('fake-redirect-uri');
    });
  });
});
