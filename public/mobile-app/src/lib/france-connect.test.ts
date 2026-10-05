import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { franceConnectLogout } from './france-connect';

describe('/france-connect', () => {
  describe('franceConnectLogout', () => {
    test('should call logout endpoint', async () => {
      // Given
      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      await franceConnectLogout('fake-id-token');

      // Then
      expect(spy).toHaveBeenCalledWith(
        '/logout-france-connect?id_token_hint=fake-id-token'
      );
    });
  });
});
