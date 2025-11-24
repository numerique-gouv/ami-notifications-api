import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { registerDevice, unregisterDevice } from '$lib/registration.js'

describe('/registration.js', () => {
  describe('registerDevice', () => {
    test('should call registrations endpoint from API', async () => {
      // Given
      const pushSubscription = {
        endpoint: 'fake-endpoint',
        toJSON: () => ({
          keys: {
            auth: 'fake-auth',
            p256dh: 'fake-p256dh',
          },
        }),
      }
      const registration = {
        created_at: '2025-09-30T11:16:33.760588',
        id: '15d6be79-94de-4675-b9c3-4eb3207aff21',
        subscription: pushSubscription,
        user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
      }
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => Promise.resolve(registration),
        })
      )

      // When
      const result = await registerDevice(pushSubscription)

      // Then
      expect(result).toEqual(registration)
      expect(result.created_at).toEqual('2025-09-30T11:16:33.760588')
      expect(result.id).toEqual('15d6be79-94de-4675-b9c3-4eb3207aff21')
      expect(result.subscription.endpoint).toEqual('fake-endpoint')
      expect(result.subscription.toJSON().keys.auth).toEqual('fake-auth')
      expect(result.subscription.toJSON().keys.p256dh).toEqual('fake-p256dh')
      expect(result.user_id).toEqual('3ac73f4f-4be2-456a-9c2e-ddff480d5767')
    })
  })

  describe('unregisterDevice', () => {
    test('should call delete registrations endpoint from API', async () => {
      // Given
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 204,
        })
      )

      // When
      const responseStatus = await unregisterDevice()

      // Then
      expect(responseStatus).toEqual(204)
    })

    test('should call delete registrations endpoint from API and return error status when deletion failed', async () => {
      // Given
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 400,
          statusText: 'fake status text',
          body: 'fake body',
        })
      )
      const consoleMock = vi.spyOn(console, 'log')

      // When
      const responseStatus = await unregisterDevice()

      // Then
      expect(responseStatus).toEqual(400)
    })
  })
})
