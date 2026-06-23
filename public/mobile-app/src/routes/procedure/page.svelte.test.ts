import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import { FollowUp } from '$lib/follow-up';
import * as procedureMethods from '$lib/procedure';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockAddress, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window;

  beforeEach(async () => {
    originalWindow = globalThis.window;

    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_API_URL: 'https://localhost:8000',
        PUBLIC_FEATURE_FLAG_SILENT_FC_OTV: 'true',
        PUBLIC_MATOMO_ENABLED: 'false',
        PUBLIC_FC_PROXY_BASE_URL: 'https://proxy',
        PUBLIC_FC_BASE_URL: 'https://fc',
        PUBLIC_FC_LOGOUT_ENDPOINT: '/api/v2/session/end',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_OTV = 'true';

    await userStore.login(mockUserInfo);
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    globalThis.window = originalWindow;
    vi.resetAllMocks();
    vi.useRealTimers();
  });

  test('user has to be connected', async () => {
    // Given
    userStore.connected = null;
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should display date from url param', async () => {
    // Given
    window.location.hash = '#/procedure?date=2025-12-05';

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-date')).toHaveTextContent(
        'À partir du 5 décembre'
      );
    });
  });

  test('should display default date if url param is empty', async () => {
    // Given
    const date = new Date(2026, 5, 17, 12, 22);
    vi.setSystemTime(date);
    window.location.hash = '#/procedure?date=';

    // When
    render(Page);

    // Then
    expect(screen.getByTestId('item-date')).toHaveTextContent(`À partir du 17 juin`);
  });

  test('should display default date if url param is missing', async () => {
    // Given
    const date = new Date(2026, 5, 17, 12, 22);
    vi.setSystemTime(date);
    window.location.hash = '#/procedure';

    // When
    render(Page);

    // Then
    expect(screen.getByTestId('item-date')).toHaveTextContent(`À partir du 17 juin`);
  });

  test('should display default if url param is an invalid date', async () => {
    // Given
    const date = new Date(2026, 5, 17, 12, 22);
    vi.setSystemTime(date);
    window.location.hash = '#/procedure?date=coucou';

    // When
    render(Page);

    // Then
    expect(screen.getByTestId('item-date')).toHaveTextContent(`À partir du 17 juin`);
  });

  test('should retrieve procedure url', async () => {
    // Given
    await userStore.login(mockUserInfo);
    userStore.connected?.setPreferredUsername('Dupont');
    userStore.connected?.setAddress(mockAddress);

    const expectedProcedureUrl = 'fake-public-otv-url?caller=fake.jwt.token';
    const spy = vi
      .spyOn(procedureMethods, 'retrieveProcedureUrl')
      .mockResolvedValue(expectedProcedureUrl);
    vi.spyOn(FollowUp.prototype, 'hasNonArchivedItems').mockReturnValue(false);
    vi.stubGlobal('location', {
      href: 'fake-link',
      hash: '',
      origin: 'http://localhost',
    });

    // When
    render(Page);

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'Dupont',
        'some@email.com',
        'Paris',
        '75007',
        'Avenue de Ségur'
      );
      expect(screen.queryByTestId('procedure-button')).not.toBeNull();
      expect(screen.queryByTestId('followup-button')).toBeNull();
    });

    // When
    const procedureButton = screen.getByTestId('procedure-button');
    await fireEvent.click(procedureButton);

    // Then
    await waitFor(() => {
      expect(window.location.href).toBe(
        'https://localhost:8000/silent-login-ami-fi?redirect_url=fake-public-otv-url%3Fcaller%3Dfake.jwt.token'
      );
    });
  });

  test('should retrieve procedure url - non archived items exists', async () => {
    // Given
    await userStore.login(mockUserInfo);
    userStore.connected?.setPreferredUsername('Dupont');
    userStore.connected?.setAddress(mockAddress);

    const expectedProcedureUrl = 'fake-public-otv-url?caller=fake.jwt.token';
    const spy = vi
      .spyOn(procedureMethods, 'retrieveProcedureUrl')
      .mockResolvedValue(expectedProcedureUrl);
    vi.spyOn(FollowUp.prototype, 'hasNonArchivedItems').mockReturnValue(true);
    vi.stubGlobal('location', {
      href: 'fake-link',
      hash: '',
      origin: 'http://localhost',
    });
    const spy2 = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith(
        'Dupont',
        'some@email.com',
        'Paris',
        '75007',
        'Avenue de Ségur'
      );
      expect(screen.queryByTestId('procedure-button')).not.toBeNull();
      expect(screen.queryByTestId('followup-button')).not.toBeNull();
    });

    // When
    const procedureButton = screen.getByTestId('procedure-button');
    await fireEvent.click(procedureButton);

    // Then
    await waitFor(() => {
      expect(window.location.href).toBe(
        'https://localhost:8000/silent-login-ami-fi?redirect_url=fake-public-otv-url%3Fcaller%3Dfake.jwt.token'
      );
    });

    // When
    const followupButton = screen.getByTestId('followup-button');
    await fireEvent.click(followupButton);

    // Then
    await waitFor(() => {
      expect(spy2).toHaveBeenCalledTimes(1);
      expect(spy2).toHaveBeenCalledWith('/#/requests');
    });
  });

  test('should disable button when procedure url is empty', async () => {
    // Given
    await userStore.login(mockUserInfo);

    const procedureUrl = '';
    const spy = vi
      .spyOn(procedureMethods, 'retrieveProcedureUrl')
      .mockResolvedValue(procedureUrl);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      const procedureButton = screen.getByTestId('procedure-button');
      expect(procedureButton).toBeDisabled();
    });
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });

  describe('user click on procedure button', () => {
    test('should redirect to procedure url', async () => {
      // Given
      const locationMock = {
        href: '',
        hash: '#/procedure',
        origin: 'http://localhost',
      };
      vi.stubGlobal('location', locationMock);
      await userStore.login(mockUserInfo);
      vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_OTV = 'false';
      const procedureUrl = 'fake-public-otv-url?caller=fake.jwt.token';
      vi.spyOn(procedureMethods, 'retrieveProcedureUrl').mockResolvedValue(
        procedureUrl
      );

      render(Page);
      const procedureButton = await screen.getByTestId('procedure-button');

      // When
      await fireEvent.click(procedureButton);

      // Then
      await waitFor(() => {
        expect(procedureMethods.retrieveProcedureUrl).toHaveBeenCalled();
        expect(locationMock.href).toEqual('fake-public-otv-url?caller=fake.jwt.token');
      });
    });

    test('should redirect to silent login', async () => {
      // Given
      const locationMock = {
        href: '',
        hash: '#/procedure',
        origin: 'http://localhost',
      };
      vi.stubGlobal('location', locationMock);
      await userStore.login(mockUserInfo);
      const procedureUrl = 'fake-public-otv-url?caller=fake.jwt.token';
      vi.spyOn(procedureMethods, 'retrieveProcedureUrl').mockResolvedValue(
        procedureUrl
      );

      render(Page);
      const procedureButton = await screen.getByTestId('procedure-button');

      // When
      await fireEvent.click(procedureButton);

      // Then
      await waitFor(() => {
        expect(procedureMethods.retrieveProcedureUrl).toHaveBeenCalled();
        expect(locationMock.href).toEqual(
          'https://localhost:8000/silent-login-ami-fi?redirect_url=fake-public-otv-url%3Fcaller%3Dfake.jwt.token'
        );
      });
    });
  });
});
