import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as nativeInfosMethods from '$lib/bridges/nativeInfos';
import * as urlAliasesMethods from '$lib/urlAliases';
import { isPromotedUrl, resolveUrl } from '$lib/urlAliases';

describe('/urlAliases.ts', () => {
  describe('resolveUrl', () => {
    test('should return null if url is not matching known aliases', async () => {
      // Given
      const aliases = [
        { pattern: '/#/resources', alias: 'resource:list' },
        { pattern: '/#/resources/:id', alias: 'resource:detail' },
      ];
      vi.spyOn(urlAliasesMethods, 'getUrlAliases').mockReturnValue(aliases);
      const url1 = '/#/unknown';
      const url2 = '/resources';
      const url3 = '/#/resources/foo/bar';

      // When
      const result1 = resolveUrl(url1);
      const result2 = resolveUrl(url2);
      const result3 = resolveUrl(url3);

      // Then
      expect(result1).toEqual(null);
      expect(result2).toEqual(null);
      expect(result3).toEqual(null);
    });

    test('should return alias if url is matching known aliases', async () => {
      // Given
      const aliases = [
        { pattern: '/#/resources', alias: 'resource:list' },
        { pattern: '/#/resources/:id', alias: 'resource:detail' },
      ];
      vi.spyOn(urlAliasesMethods, 'getUrlAliases').mockReturnValue(aliases);
      const url1 = '/#/resources';
      const url2 = '/#/resources/id';
      const url3 = '/#/resources/42';

      // When
      const result1 = resolveUrl(url1);
      const result2 = resolveUrl(url2);
      const result3 = resolveUrl(url3);

      // Then
      expect(result1).toEqual('resource:list');
      expect(result2).toEqual('resource:detail');
      expect(result3).toEqual('resource:detail');
    });
  });

  describe('isPromotedUrl', () => {
    test('should return true if alias is declared as promoted', async () => {
      // Given
      const aliases = [
        { pattern: '/#/resources', alias: 'resource:list' },
        { pattern: '/#/resources/:id', alias: 'resource:detail' },
      ];
      vi.spyOn(urlAliasesMethods, 'getUrlAliases').mockReturnValue(aliases);
      vi.spyOn(nativeInfosMethods, 'getPromotedUrlAliases').mockReturnValue([
        'resource:list',
      ]);
      const url1 = '/#/unknown';
      const url2 = '/#/resources';
      const url3 = '/#/resources/42';

      // When
      const result1 = isPromotedUrl(url1);
      const result2 = isPromotedUrl(url2);
      const result3 = isPromotedUrl(url3);

      // Then
      expect(result1).toEqual(false);
      expect(result2).toEqual(true);
      expect(result3).toEqual(false);
    });
  });
});
