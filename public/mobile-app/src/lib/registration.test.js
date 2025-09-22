import { describe, test, expect, vi, afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { registerUser } from '$lib/registration.js'

describe('/registration.js', () => {
  afterEach(() => {
    window.localStorage.clear()
  })

  describe('registerUser', () => {
    test('should call registrations endpoint from API', async () => {
      // Given
      vi.mock('$lib/notifications', () => {
        const pushSubscription = {
          endpoint: 'fake-endpoint',
          toJSON: () => ({
            keys: {
              auth: 'fake-auth',
              p256dh: 'fake-p256dh',
            },
          }),
        }
        return {
          subscribePush: vi.fn(() => pushSubscription),
        }
      })
      window.localStorage.setItem('user_id', 'fake-user-id')

      let registration
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
    })
  })
})
