import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { unregisterRegistrationsForNative } from '$lib/registration.js';

describe('/registration.ts', () => {
  describe('unregisterRegistrationsForNative', () => {
    test('should call delete registrations endpoint from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(null, { status: 204 }));

      // When
      const responseStatus = await unregisterRegistrationsForNative('some-id');

      // Then
      expect(responseStatus).toEqual(204);
      const expectedRequestInit = {
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: 'some-id' }),
        method: 'PUT',
      };
      expect(spy).toHaveBeenCalledWith(
        '/api/v1/users/registrations?action=removeFromDeviceId',
        expectedRequestInit
      );
    });

    test('should call delete registrations endpoint from API and return error status when deletion failed', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('fake body', { status: 400 })
      );

      // When
      const responseStatus = await unregisterRegistrationsForNative('some-id');

      // Then
      expect(responseStatus).toEqual(400);
    });
  });
});
