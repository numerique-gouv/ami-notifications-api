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
        id: 49,
        subscription: pushSubscription,
        user_id: 44,
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
      expect(result.id).toEqual(49)
      expect(result.subscription.endpoint).toEqual('fake-endpoint')
      expect(result.subscription.toJSON().keys.auth).toEqual('fake-auth')
      expect(result.subscription.toJSON().keys.p256dh).toEqual('fake-p256dh')
      expect(result.user_id).toEqual(44)
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
      const consoleMock = vi.spyOn(console, 'log')

      // When
      await unregisterDevice()

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(2)
      expect(consoleMock).toHaveBeenNthCalledWith(1, 'response:', { status: 204 })
      expect(consoleMock).toHaveBeenNthCalledWith(
        2,
        'The device has been deleted successfully'
      )
    })

    test('should call delete registrations endpoint from API and log error when response status is not 204', async () => {
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
      await unregisterDevice()

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(2)
      expect(consoleMock).toHaveBeenNthCalledWith(1, 'response:', {
        status: 400,
        statusText: 'fake status text',
        body: 'fake body',
      })
      expect(consoleMock).toHaveBeenNthCalledWith(
        2,
        'error 400: fake status text, fake body'
      )
    })
  })
})
