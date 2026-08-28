import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveConsents, updateApiConsent } from '$lib/api-consents';

const apiConsents = {
  consents: [
    {
      partner_id: 'dinum-ami',
      consent_datetime: '2026-01-23T15:50:00Z',
    },
    {
      partner_id: 'dinum-dn',
      consent_datetime: '2026-01-22T14:55:00Z',
    },
  ],
};

describe('/api-consents', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  describe('retrieveConsents', () => {
    test('should get consents from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiConsents.consents), { status: 200 })
        );

      // When
      const result = await retrieveConsents();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/consents');
      expect(result.consents.length).toEqual(2);
      expect(result.consents[0].partner_id).toEqual(apiConsents.consents[0].partner_id);
      expect(result.consents[0].consent_datetime).toEqual(
        apiConsents.consents[0].consent_datetime
      );
      expect(result.consents[1].partner_id).toEqual(apiConsents.consents[1].partner_id);
      expect(result.consents[1].consent_datetime).toEqual(
        apiConsents.consents[1].consent_datetime
      );
    });

    test('should get consents items from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrieveConsents();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/consents');
      expect(result).toEqual({ consents: [] });
    });
  });

  describe('updateApiConsent', () => {
    test('should return true', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }));

      // When
      const result = await updateApiConsent('dinum-ami', true);

      // Then
      expect(result).toEqual(true);
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/consents', {
        body: '{"partner_id":"dinum-ami","consent":true}',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });
    });
    test('should return false: 400 error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 400 }));

      // When
      const result = await updateApiConsent('dinum-ami', true);

      // Then
      expect(result).toEqual(false);
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/consents', {
        body: '{"partner_id":"dinum-ami","consent":true}',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });
    });
    test('should return false: 500 error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 500 }));

      // When
      const result = await updateApiConsent('dinum-ami', true);

      // Then
      expect(result).toEqual(false);
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/consents', {
        body: '{"partner_id":"dinum-ami","consent":true}',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });
    });
  });
});
