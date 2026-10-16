import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { waitFor } from '@testing-library/svelte';
import {
  retrievePersonalDataConsent,
  updateApiPersonalDataConsent,
} from '$lib/api-personal-data-consent';

const apiPersonalDataConsent = {
  consent_datetime: '2026-01-23T15:50:00Z',
};

describe('/api-personal-data-consent', () => {
  describe('retrievePersonalDataConsent', () => {
    test('should get personal-data-consent from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiPersonalDataConsent), { status: 200 })
        );

      // When
      const result = await retrievePersonalDataConsent();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/personal-data-consent'
      );
      expect(result.consent_datetime).toEqual(apiPersonalDataConsent.consent_datetime);
    });
    test('should store personal-data-consent to localStorage', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(apiPersonalDataConsent), { status: 200 })
      );

      // When
      await retrievePersonalDataConsent();

      // Then
      const result = JSON.parse(
        localStorage.getItem('personal-data-consent') || '{"consent_datetime":null}'
      );
      expect(result.consent_datetime).toEqual(apiPersonalDataConsent.consent_datetime);
    });

    test('should get personal-data-consent from localStorage - when status code is not 200', async () => {
      // Given
      localStorage.setItem(
        'personal-data-consent',
        JSON.stringify(apiPersonalDataConsent)
      );

      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrievePersonalDataConsent();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/personal-data-consent'
      );
      expect(result.consent_datetime).toEqual(apiPersonalDataConsent.consent_datetime);
    });
    test('should get personal-data-consent with no consent_datetime when localStorage has no key - when status code is not 200', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrievePersonalDataConsent();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/personal-data-consent'
      );
      expect(result.consent_datetime).toBeNull();
    });
    test('should get personal-data-consent from localStorage - when fetch fails', async () => {
      // Given
      localStorage.setItem(
        'personal-data-consent',
        JSON.stringify(apiPersonalDataConsent)
      );

      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Fetch failed'));

      // When
      const result = await retrievePersonalDataConsent();

      // Then
      expect(result.consent_datetime).toEqual(apiPersonalDataConsent.consent_datetime);
    });
    test('should get personal-data-consent with no consent_datetime when localStorage has no key - when fetch fails', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Fetch failed'));

      // When
      const result = await retrievePersonalDataConsent();

      // Then
      await waitFor(() => {
        expect(result.consent_datetime).toBeNull();
      });
    });
  });

  describe('updateApiPersonalDataConsent', () => {
    test('should return true', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }));

      // When
      const result = await updateApiPersonalDataConsent(true);

      // Then
      expect(result).toEqual(true);
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/personal-data-consent',
        {
          body: '{"consent":true}',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
    });
    test('should return false: 400 error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 400 }));

      // When
      const result = await updateApiPersonalDataConsent(true);

      // Then
      expect(result).toEqual(false);
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/personal-data-consent',
        {
          body: '{"consent":true}',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
    });
    test('should return false: 500 error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 500 }));

      // When
      const result = await updateApiPersonalDataConsent(true);

      // Then
      expect(result).toEqual(false);
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        '/api/v1/users/personal-data-consent',
        {
          body: '{"consent":true}',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
    });
  });
});
