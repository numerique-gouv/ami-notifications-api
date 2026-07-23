import { beforeEach, describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { hideBanner, isBannerHidden } from '$lib/banner';

describe('/lib/banner.ts', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('hideBanner', () => {
    test('should store banner id in localstorage', () => {
      // When
      hideBanner('banner-id');

      // Then
      expect(localStorage.getItem('hidden_banner_ids')).toEqual('["banner-id"]');
    });
    test('should store banner id in localstorage - localstorage is empty', () => {
      // Given
      localStorage.setItem('hidden_banner_ids', JSON.stringify(['other-banner-id']));

      // When
      hideBanner('banner-id');

      // Then
      expect(localStorage.getItem('hidden_banner_ids')).toEqual(
        '["other-banner-id","banner-id"]'
      );
    });
  });

  describe('isBannerHidden', () => {
    test('should return true if banner id is stored in localStorage', () => {
      // Given
      localStorage.setItem('hidden_banner_ids', JSON.stringify(['other-banner-id']));

      // When
      const result1 = isBannerHidden('banner-id');
      const result2 = isBannerHidden('other-banner-id');

      // Then
      expect(result1).toEqual(false);
      expect(result2).toEqual(true);
    });
  });
});
