import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as initializeDataFromAPIMethods from '$lib/initializeDataFromAPI';
import { userStore } from '$lib/state/User.svelte';
import { load } from './+layout';

vi.mock('$app/environment', () => ({ browser: true }));

vi.mock('$app/state', () => {
  return {
    page: {
      url: new URL('https://example.com/?foo=bar'),
    },
  };
});

describe('+layout.ts', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
  });

  test('should call initializeData when user is logged in', async () => {
    // Given
    window.localStorage.setItem('is_logged_in', 'true');

    const spy = vi
      .spyOn(initializeDataFromAPIMethods, 'initializeData')
      .mockResolvedValue();

    const { page } = await import('$app/state');
    const mockSearchParams = new URLSearchParams();
    mockSearchParams.set('is_logged_in', 'true');
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams);

    // When
    // @ts-expect-error
    await load();

    // Then
    expect(spy).toHaveBeenCalledWith(mockSearchParams, userStore);
  });

  test('should not call initializeData when user is not logged in', async () => {
    // Given
    window.localStorage.removeItem('is_logged_in');

    const spy = vi
      .spyOn(initializeDataFromAPIMethods, 'initializeData')
      .mockResolvedValue();

    // When
    // @ts-expect-error
    await load();

    // Then
    expect(spy).not.toHaveBeenCalled();
  });
});
