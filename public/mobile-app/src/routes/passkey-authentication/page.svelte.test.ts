import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as passkeyMethods from '$lib/passkey';
import { PasskeyBreakingError, PasskeyError, PasskeyNetworkError } from '$lib/passkey';
import { userStore } from '$lib/state/User.svelte';
import Page from './+page.svelte';

vi.mock('@simplewebauthn/browser', () => ({
  startAuthentication: vi.fn(),
}));

describe('/+page.svelte', () => {
  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();
  });

  test('should display passkey error message and bypass button on PasskeyError', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    const spyAuth = vi
      .spyOn(passkeyMethods, 'authenticateWithPasskey')
      .mockRejectedValue(new PasskeyError());
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
    expect(spyAuth).toHaveBeenCalledExactlyOnceWith();
  });
  test('should display network error message and bypass button on PasskeyNetworkError', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    const spyAuth = vi
      .spyOn(passkeyMethods, 'authenticateWithPasskey')
      .mockRejectedValue(new PasskeyNetworkError());
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
    expect(spyAuth).toHaveBeenCalledExactlyOnceWith();
  });
  test('should display passkey error message and bypass button on PasskeyBreakingError', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    const spyAuth = vi
      .spyOn(passkeyMethods, 'authenticateWithPasskey')
      .mockRejectedValue(new PasskeyBreakingError());
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
    expect(spyAuth).toHaveBeenCalledExactlyOnceWith();
  });
  test('should display passkey error message and bypass button on PasskeyBreakingError - with redirect_to_hash param', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('user_does_not_match');
    mockSearchParams.set('redirect_to_hash', '/page');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const unsetHasWorkingPasskeySpy = vi
      .spyOn(userStore, 'unsetHasWorkingPasskey')
      .mockResolvedValue();
    const spyAuth = vi
      .spyOn(passkeyMethods, 'authenticateWithPasskey')
      .mockRejectedValue(new PasskeyBreakingError());
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
    expect(spyAuth).toHaveBeenCalledExactlyOnceWith();
  });
  test('should redirect when user is authenticated', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    const spyAuth = vi
      .spyOn(passkeyMethods, 'authenticateWithPasskey')
      .mockResolvedValue('fake-redirect-uri');
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

      expect(spy).toHaveBeenCalledWith('fake-redirect-uri');
      expect(spyAuth).toHaveBeenCalledExactlyOnceWith();
    });
  });
});
