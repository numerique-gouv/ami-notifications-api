import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as envModule from '$env/static/public';
import { franceConnectLogout } from './france-connect';

describe('/france-connect', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
      });
    });
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe('franceConnectLogout', () => {
    test('should call logout endpoint with login page as return url', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FC_PROXY_BASE_URL = 'https://fake-fc-proxy';
      vi.stubGlobal('location', { href: 'http://example.com' });

      // When
      await franceConnectLogout('fake-id-token');

      // Then
      expect(window.location.href).toBe(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=https%253A%252F%252Flocalhost%253A5173%252F%253Fis_logged_out%2523%252Flogin&post_logout_redirect_uri=https%3A%2F%2Ffake-fc-proxy%2F'
      );
    });
    test('should call logout endpoint with another return url', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FC_PROXY_BASE_URL = 'https://fake-fc-proxy';
      vi.stubGlobal('location', { href: 'http://example.com' });

      // When
      await franceConnectLogout('fake-id-token', 'http://other-return-url/');

      // Then
      expect(window.location.href).toBe(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=http%253A%252F%252Fother-return-url%252F&post_logout_redirect_uri=https%3A%2F%2Ffake-fc-proxy%2F'
      );
    });
  });
});
