import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, waitFor } from '@testing-library/svelte';
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
  });

  describe('whitelisting', () => {
    test('should redirect to /forbidden if the app is not whitelisted', async () => {
      // Given
      delete mockEnv.env.PUBLIC_WEBSITE_PUBLIC;

      // When
      render(Layout, { children: (() => {}) as any });

      // Then
      await waitFor(() => {
        expect(window.location.href).toEqual('/forbidden/');
      });
    });

    test('should not redirect if PUBLIC_WEBSITE_PUBLIC is set', async () => {
      // Given
      mockEnv.env.PUBLIC_WEBSITE_PUBLIC = 'true';

      // When
      render(Layout, { children: (() => {}) as any });

      // Then
      await waitFor(() => {
        expect(window.location.href).not.toEqual('/forbidden/');
      });
    });

    test('should not redirect if running in a native app', async () => {
      // Given
      delete mockEnv.env.PUBLIC_WEBSITE_PUBLIC;
      window.NativeBridge = {};

      // When
      render(Layout, { children: (() => {}) as any });

      // Then
      await waitFor(() => {
        expect(window.location.href).not.toEqual('/forbidden/');
      });
    });
  });
});
