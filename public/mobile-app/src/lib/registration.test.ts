import { afterEach, describe, expect, test, vi } from 'vitest';
import { PUBLIC_API_URL } from '$env/static/public';
import '@testing-library/jest-dom/vitest';
import * as authMethods from '$lib/auth';
import {
  registerDevice,
  unregisterDesktopRegistration,
  unregisterDevice,
} from '$lib/registration.js';
import { mockPushSubscription } from '$tests/utils';

describe('/registration.ts', () => {
  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('registerDevice', () => {
    test('should call registrations endpoint from API', async () => {
      // Given
      const pushSubscription = {
        ...mockPushSubscription,
        toJSON: () => ({ keys: { auth: 'fake-auth', p256dh: 'fake-p256dh' } }),
      };
      const mockFetch = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify('nothing special'), { status: 200 })
        );

      // When
      await registerDevice(pushSubscription);

      // Then
      expect(mockFetch).toHaveBeenCalledWith(
        `${PUBLIC_API_URL}/api/v1/users/registrations`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{"subscription":{"endpoint":"","keys":{"auth":"fake-auth","p256dh":"fake-p256dh"}}}',
          credentials: 'include',
        }
      );
    });
  });

  describe('unregisterDevice', () => {
    test('should call delete registrations endpoint from API', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(null, { status: 204 })
      );
      const spy = vi
        .spyOn(authMethods, 'apiFetch')
        .mockResolvedValue(new Response(null, { status: 204 }));

      // When
      const responseStatus = await unregisterDevice('some-id');

      // Then
      expect(responseStatus).toEqual(204);
      const expectedRequestInit = {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'DELETE',
      };
      expect(spy).toHaveBeenCalledWith(
        '/api/v1/users/registrations/device_id/some-id',
        expectedRequestInit
      );
    });

    test('should call delete registrations endpoint from API and return error status when deletion failed', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('fake body', { status: 400 })
      );

      // When
      const responseStatus = await unregisterDevice('some-id');

      // Then
      expect(responseStatus).toEqual(400);
    });
  });

  describe('unregisterDesktopRegistration', () => {
    test('should call delete registrations endpoint from API', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(null, { status: 204 })
      );
      const spy = vi
        .spyOn(authMethods, 'apiFetch')
        .mockResolvedValue(new Response(null, { status: 204 }));

      // When
      const responseStatus = await unregisterDesktopRegistration('some-id');

      // Then
      expect(responseStatus).toEqual(204);
      const expectedRequestInit = {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'DELETE',
      };
      expect(spy).toHaveBeenCalledWith(
        '/api/v1/users/registrations/some-id',
        expectedRequestInit
      );
    });

    test('should call delete registrations endpoint from API and return error status when deletion failed', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('fake body', { status: 400 })
      );

      // When
      const responseStatus = await unregisterDesktopRegistration('some-id');

      // Then
      expect(responseStatus).toEqual(400);
    });
  });
});
