import { describe, expect, test, vi } from 'vitest';
import { userStore } from '$lib/state/User.svelte';
import { load } from './+layout';

vi.mock('$app/state', () => {
  return {
    page: {
      url: new URL('https://example.com/?foo=bar'),
    },
  };
});

vi.mock('$env/static/public', async (importOriginal) => {
  const original = (await importOriginal()) as Record<string, unknown>;
  return Promise.resolve({
    ...original,
    PUBLIC_PROMPT_FOR_ACCESS_KEY: null,
  });
});

describe('+layout.ts', () => {
  test('should call buildUser', async () => {
    // Given
    const spy = vi.spyOn(userStore, 'buildUser').mockResolvedValue();

    // When
    // @ts-expect-error
    await load();

    // Then
    expect(spy).toHaveBeenCalled();
  });
});
