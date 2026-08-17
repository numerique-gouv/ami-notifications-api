import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as envModule from '$env/static/public';
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
  beforeEach(() => {
    vi.resetAllMocks();
    localStorage.clear();
  });

  test('should call buildUser', async () => {
    // Given

    const spy = vi.spyOn(userStore, 'buildUser').mockResolvedValue();

    // When
    // @ts-expect-error
    await load();

    // Then
    expect(spy).toHaveBeenCalled();
  });

  test('should ask and check access key when configured', async () => {
    vi.mocked(envModule).PUBLIC_PROMPT_FOR_ACCESS_KEY =
      'Veuillez entrer le code d’accès';

    Object.defineProperty(window, 'cookieStore', {
      value: {
        _store: Object(),
        get: function (name: string) {
          if (this._store[name]) {
            return this._store[name];
          } else {
            return undefined;
          }
        },
        set: function (cookie: Record<string, string>) {
          this._store[cookie.name] = cookie.value;
        },
        delete: function (name: string) {
          this._store[name] = undefined;
        },
      },
    });
    Object.defineProperty(window, 'prompt', {
      value: () => 'ABC',
    });
    const spyOnPrompt = vi.spyOn(window, 'prompt');

    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({}), { status: 401 })
    );

    expect(window.location instanceof Location).toBe(true);
    // @ts-expect-error
    await load();
    expect(spyOnPrompt).toHaveBeenCalledTimes(1);
    expect(window.location).toEqual('/'); // set to / to trigger a redirect
    expect(window.cookieStore.get('access_key')).toEqual(undefined); // cookie not set

    (window as Window).location = '';
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({}), { status: 200 })
    );
    // @ts-expect-error
    await load();
    expect(window.location).toEqual(''); // not touched
    expect(window.cookieStore.get('access_key')).toEqual('ABC');
    expect(spyOnPrompt).toHaveBeenCalledTimes(2);

    // @ts-expect-error
    await load();
    expect(spyOnPrompt).toHaveBeenCalledTimes(2); // access key from cookie was used

    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({}), { status: 401 })
    );
    // @ts-expect-error
    await load();
    expect(window.location).toEqual('/'); // set to / to trigger a redirect
    expect(window.cookieStore.get('access_key')).toEqual(undefined); // cookie not set
  });
});
