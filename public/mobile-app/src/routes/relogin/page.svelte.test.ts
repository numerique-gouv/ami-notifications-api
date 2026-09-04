import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('should navigate to login page when user is not already logged in', async () => {
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    render(Page);
    expect(spy).toHaveBeenCalledWith('/#/login');
  });

  test('should render a notice with current identity', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockUserInfo), { status: 200 })
    );

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('banner-relogin')).toBeInTheDocument();
      expect(
        screen.queryByText(/Vous devez vous connecter en tant que Angela/)
      ).toBeInTheDocument();
    });
  });

  test('should render FranceConnect button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockUserInfo), { status: 200 })
    );

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const franceConnectButton = screen.getByRole('button', {
        name: 'S’identifier avec FranceConnect',
      });
      expect(franceConnectButton).toHaveTextContent('S’identifier avec FranceConnect');
    });
  });

  test('should display network-error page on FranceConnect login button when back is down', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error());
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    render(Page);
    await waitFor(() => {
      const franceConnectLoginButton = screen.getByRole('button', {
        name: 'S’identifier avec FranceConnect',
      });

      // When
      franceConnectLoginButton.click();

      // Then
      expect(spy).toHaveBeenCalledWith('/#/network-error');
    });
  });

  test('should call authorize endpoint when click on FranceConnect login button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }));
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    render(Page);
    await waitFor(() => {
      const franceConnectLoginButton = screen.getByRole('button', {
        name: 'S’identifier avec FranceConnect',
      });

      // When
      franceConnectLoginButton.click();

      // Then
      expect(spy).toHaveBeenCalledWith('/relogin-france-connect');
    });
  });

  test('should not display any error message if the user aborted the connection', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams(
      'error=access_denied&error_description=User auth aborted'
    );
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    render(Page);

    // Then
    const errorMessage = await screen.queryByText('access_denied');
    expect(errorMessage).toBeNull();
    const errorDescription = await screen.queryByText('User auth aborted');
    expect(errorDescription).toBeNull();
  });

  test('should display connection help links', async () => {
    // Given
    await userStore.login(mockUserInfo);

    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();

    // When
    render(Page);

    // Then
    const connectionHelpButton = screen.getByTestId('connection-help-button');
    expect(screen.queryByTestId('connection-help-link-url')).not.toBeInTheDocument();
    await waitFor(() => {
      connectionHelpButton.click();
      // now the popup is open
      expect(screen.queryByTestId('connection-help-link-url')).toBeInTheDocument();
      expect(screen.queryByTestId('connection-help-link-email')).toBeInTheDocument();
    });
  });
});
