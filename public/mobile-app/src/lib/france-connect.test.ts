import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as envModule from '$env/static/public';
import * as AMINavigationMethods from '$lib/ami-navigation';
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

  describe('franceConnectLogout', () => {
    test('should call logout endpoint with login page as return url', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FC_PROXY_BASE_URL = '';
      vi.mocked(envModule).PUBLIC_FC_POST_LOGOUT_REDIRECT_URI = '/?is_logged_out';
      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      await franceConnectLogout('fake-id-token');

      // Then
      expect(spy).toHaveBeenCalledWith(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out&post_logout_redirect_uri=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out'
      );
    });
    test('should call logout endpoint with login page as return url - with proxy', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FC_PROXY_BASE_URL = 'https://fake-fc-proxy';
      vi.mocked(envModule).PUBLIC_FC_POST_LOGOUT_REDIRECT_URI = '/?is_logged_out';
      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      await franceConnectLogout('fake-id-token');

      // Then
      expect(spy).toHaveBeenCalledWith(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out&post_logout_redirect_uri=https%3A%2F%2Ffake-fc-proxy%2F'
      );
    });
  });
});
