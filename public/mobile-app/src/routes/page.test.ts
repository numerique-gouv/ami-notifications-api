import { describe, expect, test, vi } from 'vitest';
import * as consentsMethods from '$lib/consents';
import * as followupMethods from '$lib/followup';
import '@testing-library/jest-dom/vitest';
import { waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { Consents } from '$lib/consents';
import { Followup } from '$lib/followup';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import { load } from './+page';

describe('/+page.ts', () => {
  test('should go to login page if ?is_logged_out is present', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('is_logged_out');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    // @ts-expect-error
    await load({});

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/?is_logged_out#/login');
    });
  });

  test('should get out if user is not connected', async () => {
    // Given
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    // @ts-expect-error
    await load({});

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('should add toast when user does not match after relogin - without redirect', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('user_does_not_match');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const spy = vi.spyOn(toastStore, 'addToast');
    const spy2 = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 400 }));

    // When
    // @ts-expect-error
    await load({});

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
        'warning',
        null,
        true
      );
      expect(spy2).not.toHaveBeenCalled();
    });
  });

  test('should add toast when user does not match after relogin - with redirect', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams('user_does_not_match');
    mockSearchParams.set('redirect_to_hash', '/page');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const spy = vi.spyOn(toastStore, 'addToast');
    const spy2 = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    // @ts-expect-error
    await load({});

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
        'warning',
        null,
        true
      );
      expect(spy2).toHaveBeenCalledWith('/#/page');
    });
  });

  test('load should call build consents and followup', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('redirect_to_hash', '/page');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    vi.spyOn(followup, 'isEmpty').mockReturnValue(false);
    const consents = new Consents();
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
    vi.spyOn(consents, 'hasAnyConsents').mockReturnValue(true);

    // When
    // @ts-expect-error
    const result = await load({});

    // Then
    // @ts-expect-error
    expect(result.followup).toEqual(followup);
    // @ts-expect-error
    expect(result.isFollowupEmpty).toEqual(false);
    // @ts-expect-error
    expect(result.hasAnyConsents).toEqual(true);
  });
});
