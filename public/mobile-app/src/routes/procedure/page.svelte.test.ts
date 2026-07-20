import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import * as AMIGotoMethods from '$lib/ami-goto';
import { Followup } from '$lib/followup';
import * as procedureMethods from '$lib/procedure';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockAddress, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_FEATURE_FLAG_SERVICES_ENABLED: 'false',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'false';

    await userStore.login(mockUserInfo);
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });

  afterEach(() => {
    vi.resetAllMocks();
    vi.useRealTimers();
  });

  test('services feature flag is enabled', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'true';
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith(
        '/#/services/service/psl/OperationTranquilliteVacances',
        { replaceState: true }
      );
    });
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
    vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(false);
    const spy2 = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

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
      expect(spy2).toHaveBeenCalledTimes(1);
      expect(spy2).toHaveBeenCalledWith(expectedProcedureUrl, true);
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
    vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);
    const spy2 = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
    const spy3 = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

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
      expect(spy3).toHaveBeenCalledTimes(1);
      expect(spy3).toHaveBeenCalledWith(expectedProcedureUrl, true);
    });

    // When
    const followupButton = screen.getByTestId('followup-button');
    await fireEvent.click(followupButton);

    // Then
    await waitFor(() => {
      expect(spy2).toHaveBeenCalledTimes(1);
      expect(spy2).toHaveBeenCalledWith('/#/followup');
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
});
