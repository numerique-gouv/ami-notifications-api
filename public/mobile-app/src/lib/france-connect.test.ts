import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as AMIGotoMethods from '$lib/ami-goto';
import { franceConnectLogout } from './france-connect';

describe('/france-connect', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe('franceConnectLogout', () => {
    test('should call logout endpoint with home as return url', async () => {
      // Given
      const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

      // When
      await franceConnectLogout('fake-id-token');

      // Then
      expect(spy).toHaveBeenCalledWith(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=https%253A%252F%252Flocalhost%253A5173%252F%253Fis_logged_out&post_logout_redirect_uri=https%3A%2F%2Fami-fc-proxy-dev.osc-fr1.scalingo.io%2F'
      );
    });
    test('should call logout endpoint with another return url', async () => {
      // Given
      const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

      // When
      await franceConnectLogout('fake-id-token', 'http://other-return-url/');

      // Then
      expect(spy).toHaveBeenCalledWith(
        'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?id_token_hint=fake-id-token&state=http%253A%252F%252Fother-return-url%252F&post_logout_redirect_uri=https%3A%2F%2Fami-fc-proxy-dev.osc-fr1.scalingo.io%2F'
      );
    });
  });
});
