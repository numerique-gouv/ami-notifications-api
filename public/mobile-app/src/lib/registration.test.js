import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { registerUser } from '$lib/registration.js'

describe('/registration.js', () => {
  describe('registerUser', () => {
    test('should call registrations endpoint from API', async () => {
      // Given
      vi.mock('$lib/notifications', () => {
        const pushSubscription_ = {
          endpoint: 'fake-endpoint',
          toJSON: () => ({
            keys: {
              auth: 'fake-auth',
              p256dh: 'fake-p256dh',
            },
          }),
        }
        return {
          subscribePush: vi.fn(() => pushSubscription_),
        }
      })
      window.localStorage.setItem('user_id', 'fake-user-id')

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
      const result = await registerUser()

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
})
