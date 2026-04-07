import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import Layout from './+layout.svelte';

vi.mock('$env/dynamic/public', () => ({
  env: {
    PUBLIC_WEBSITE_PUBLIC: '',
  },
}));

vi.mock('$lib/dsfr', () => ({
  initDsfr: vi.fn(),
}));

describe('+layout.svelte', () => {
  let mockEnv: any;

  beforeEach(async () => {
    mockEnv = await vi.importMock('$env/dynamic/public');
  });

  afterEach(() => {
    vi.resetAllMocks();
    delete window.NativeBridge;
    delete window.NativeURLs;
  });

  describe('whitelisting', () => {
    test('should redirect to /#/forbidden if the app is not whitelisted', async () => {
      // Given
      delete mockEnv.env.PUBLIC_WEBSITE_PUBLIC;
      const spy = vi
        .spyOn(navigationMethods, 'goto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(Layout, { children: (() => {}) as any });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledWith('/#/forbidden');
      });
    });

    test('should not redirect if PUBLIC_WEBSITE_PUBLIC is set', async () => {
      // Given
      mockEnv.env.PUBLIC_WEBSITE_PUBLIC = 'true';
      const spy = vi
        .spyOn(navigationMethods, 'goto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(Layout, { children: (() => {}) as any });

      // Then
      await waitFor(() => {
        expect(spy).not.toHaveBeenCalledWith('/#/forbidden');
      });
    });

    test('should not redirect if running in a native app', async () => {
      // Given
      delete mockEnv.env.PUBLIC_WEBSITE_PUBLIC;
      window.NativeBridge = {};
      const spy = vi
        .spyOn(navigationMethods, 'goto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(Layout, { children: (() => {}) as any });

      // Then
      await waitFor(() => {
        expect(spy).not.toHaveBeenCalledWith('/#/forbidden');
      });
    });
  });

  describe('cancelling navigation to pages promoted in mobile apps', () => {
    test('should cancel navigation if the URL is in window.NativeURLs', () => {
      // Given
      let beforeNavigateCallback: (navigation: any) => void;
      vi.spyOn(navigationMethods, 'beforeNavigate').mockImplementation((cb) => {
        beforeNavigateCallback = cb;
      });
      window.NativeURLs = ['/#/settings'];
      render(Layout, { children: (() => {}) as any });

      const cancel = vi.fn();

      // When
      beforeNavigateCallback!({
        to: { url: new URL('https://localhost:5173/#/settings') },
        cancel,
      });

      // Then
      expect(cancel).toHaveBeenCalled();
    });

    test('should not cancel navigation if the URL is not in window.NativeURLs', () => {
      // Given
      let beforeNavigateCallback: (navigation: any) => void;
      vi.spyOn(navigationMethods, 'beforeNavigate').mockImplementation((cb) => {
        beforeNavigateCallback = cb;
      });
      window.NativeURLs = ['/#/settings'];
      render(Layout, { children: (() => {}) as any });

      const cancel = vi.fn();

      // When
      beforeNavigateCallback!({
        to: { url: new URL('https://localhost:5173/#/other') },
        cancel,
      });

      // Then
      expect(cancel).not.toHaveBeenCalled();
    });
  });
});
