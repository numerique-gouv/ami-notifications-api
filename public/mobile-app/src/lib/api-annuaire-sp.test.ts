import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveMairie } from '$lib/api-annuaire-sp';

const apiMairieData = {
  url_service_public: 'url1',
  expires_at: new Date('2025-11-02T12:00:00Z'),
};

const mairieData = {
  url_service_public: 'url1',
};

describe('/api-annuaire-sp', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
  });
  describe('retrieveMairie', () => {
    test('should get mairie from API', async () => {
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiMairieData), { status: 200 })
        );

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/mairie/00001');
      expect(result).toEqual(mairieData);
      expect(window.localStorage.getItem('mairie_00001')).toEqual(
        JSON.stringify(apiMairieData)
      );
    });
    test('should get mairie from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/mairie/00001');
      expect(result).toEqual(null);
      expect(window.localStorage.getItem('mairie_00001')).toEqual(null);
    });
    test('should get mairie from localstorage', async () => {
      // Given
      const date = new Date(2025, 10, 1, 12, 22);
      vi.setSystemTime(date);
      window.localStorage.setItem('mairie_00001', JSON.stringify(apiMairieData));

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(result).toEqual(mairieData);
    });
    test('should get mairie from API - data is wrong in localstorage', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiMairieData), { status: 200 })
        );
      window.localStorage.setItem('mairie_00001', 'wrong');

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/mairie/00001');
      expect(result).toEqual(mairieData);
      expect(window.localStorage.getItem('mairie_00001')).toEqual(
        JSON.stringify(apiMairieData)
      );
    });
    test('should get mairie from API - data as no expiration in localstorage', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiMairieData), { status: 200 })
        );
      window.localStorage.setItem('mairie_00001', JSON.stringify(mairieData));

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/mairie/00001');
      expect(result).toEqual(mairieData);
      expect(window.localStorage.getItem('mairie_00001')).toEqual(
        JSON.stringify(apiMairieData)
      );
    });
    test('should get mairie from API - data has no expiration in localstorage - with error', async () => {
      // Given
      const date = new Date(2025, 10, 3, 12, 22);
      vi.setSystemTime(date);
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));
      window.localStorage.setItem('mairie_00001', JSON.stringify(mairieData));

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/mairie/00001');
      expect(result).toEqual(mairieData);
      expect(window.localStorage.getItem('mairie_00001')).toEqual(
        JSON.stringify(mairieData)
      );
    });
    test('should get mairie from API - data is expired in localstorage', async () => {
      // Given
      const date = new Date(2025, 10, 3, 12, 22);
      vi.setSystemTime(date);
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiMairieData), { status: 200 })
        );
      window.localStorage.setItem('mairie_00001', JSON.stringify(mairieData));

      // When
      const result = await retrieveMairie('00001');

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/mairie/00001');
      expect(result).toEqual(mairieData);
      expect(window.localStorage.getItem('mairie_00001')).toEqual(
        JSON.stringify(apiMairieData)
      );
    });
  });
});
