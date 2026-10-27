import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import { load } from './+page';

describe('/+page.ts', () => {
  test('should get out if user is not connected', async () => {
    // Given
    vi.stubGlobal('location', { href: '/', search: '' });
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
    vi.stubGlobal('location', { href: '/', search: '?user_does_not_match' });

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
    vi.stubGlobal('location', {
      href: '/',
      search: '?user_does_not_match&redirect_to_hash=/page',
    });

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
});
