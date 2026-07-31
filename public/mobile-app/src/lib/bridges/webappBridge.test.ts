import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as UrlAliasesMethods from '$lib/urlAliases';

describe('/webappBridge.ts', () => {
  describe('getUrlAliases', () => {
    test('should return url aliases', async () => {
      // Given
      const aliases = [
        { pattern: '/#/resources', alias: 'resource:list' },
        { pattern: '/#/resources/:id', alias: 'resource:detail' },
      ];
      vi.spyOn(UrlAliasesMethods, 'getUrlAliases').mockReturnValue(aliases);
      await import('$lib/bridges/webappBridge');

      // When
      const result = window.WebAppBridge.getUrlAliases();

      // Then
      expect(result).toBe(JSON.stringify(aliases));
    });
  });
});
