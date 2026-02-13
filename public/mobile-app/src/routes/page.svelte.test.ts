import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import {
  PUBLIC_API_URL,
  PUBLIC_CONTACT_EMAIL,
  PUBLIC_CONTACT_URL,
} from '$env/static/public';
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

  test('should set localStorage when user is logged in', async () => {
    // Given
    window.localStorage.setItem('user_data', '');
    window.localStorage.setItem('user_id', '');
    window.localStorage.setItem('user_fc_hash', '');
    window.localStorage.setItem('user_api_particulier_encoded_address', '');

    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('is_logged_in', 'true');
    mockSearchParams.set('user_data', 'fake-user-data');
    mockSearchParams.set('user_first_login', 'true');
    mockSearchParams.set('user_fc_hash', 'fake-user-fc-hash');
    mockSearchParams.set('id_token', 'fake-id-token');
    mockSearchParams.set('address', 'fake-address');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(window.localStorage.getItem('user_data')).toEqual('fake-user-data');
      expect(window.localStorage.getItem('user_fc_hash')).toEqual('fake-user-fc-hash');
      expect(window.localStorage.getItem('id_token')).toEqual('fake-id-token');
      expect(
        window.localStorage.getItem('user_api_particulier_encoded_address')
      ).toEqual('fake-address');
    });
  });

  test('should navigate to notifications welcome page when it is the first user login', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('is_logged_in', 'true');
    mockSearchParams.set('user_first_login', 'true');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    vi.spyOn(userStore, 'checkLoggedIn').mockResolvedValue();
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/notifications-welcome-page');
    });
  });

  test('should navigate to homepage when user has already logged in', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('is_logged_in', 'true');
    mockSearchParams.set('user_first_login', 'false');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    vi.spyOn(userStore, 'checkLoggedIn').mockResolvedValue();
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should render FranceConnect button', async () => {
    // Given
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
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error());
    const spy = vi
      .spyOn(navigationMethods, 'goto')
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
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }));
    vi.stubGlobal('location', { href: 'fake-link' });

    render(Page);
    await waitFor(() => {
      const franceConnectLoginButton = screen.getByRole('button', {
        name: 'S’identifier avec FranceConnect',
      });

      // When
      franceConnectLoginButton.click();

      // Then
      expect(globalThis.window.location.href).toContain(PUBLIC_API_URL);
      expect(globalThis.window.location.href).toContain('login-france-connect');
    });
  });

  test('should display an error message if login failed', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams(
      'error=some error message&error_description=some error description'
    );
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    render(Page);

    // Then
    const errorMessage = await screen.findByText('some error message');
    expect(errorMessage).toBeInTheDocument();
    const errorDescription = await screen.findByText('some error description');
    expect(errorDescription).toBeInTheDocument();
  });

  test('should not display any error message if the user aborted the connection', async () => {
    // Given
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

  test('should logout the app if an error is about FranceConnect', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams(
      'error=some error message&error_type=FranceConnect'
    );
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    render(Page);

    // Then
    const errorMessage = await screen.findByText('some error message');
    expect(errorMessage).toBeInTheDocument();
    expect(window.localStorage.getItem('access_token')).toEqual(null);
  });

  test('should add toast when user is logged out', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('is_logged_out');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const spy = vi.spyOn(toastStore, 'addToast');

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('Vous avez bien été déconnecté(e)', 'neutral');
    });
  });

  test('should navigate to the homepage when user is logged out', async () => {
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
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should display contact links when user is logged out', async () => {
    // Given
    await userStore.logout();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const contactLinkTchap = screen.getByTestId('contact-link-tchap');
      expect(contactLinkTchap).toHaveAttribute('href', PUBLIC_CONTACT_URL);
      const contactLinkEmail = screen.getByTestId('contact-link-email');
      expect(contactLinkEmail).toHaveAttribute(
        'href',
        `mailto:${PUBLIC_CONTACT_EMAIL}`
      );
    });
  });
});
