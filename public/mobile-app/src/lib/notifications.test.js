import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import {
  enableNotifications,
  getSubscription,
  retrieveNotifications,
  subscribePush,
} from '$lib/notifications.ts'
import * as registrationMethods from '$lib/registration.js'

describe('/notifications.ts', () => {
  describe('retrieveNotifications', () => {
    test('should get messages from API', async () => {
      // Given
      window.localStorage.setItem('user_id', 'fake-user-id')
      const messages = [
        {
          date: '2025-09-19T12:59:04.950812',
          user_id: 42,
          sender: 'test',
          message: 'test',
          id: 29,
          title: 'test',
        },
        {
          date: '2025-09-19T13:52:23.279545',
          user_id: 42,
          sender: 'test 2',
          message: 'test 2',
          id: 30,
          title: 'test 2',
        },
      ]
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => Promise.resolve(messages),
        })
      )

      // When
      const result = await retrieveNotifications()

      // Then
      expect(result).toEqual(messages)
    })
  })

  describe('getSubscription', () => {
    test('should get subscription from pushManager when user is registered in service worker', async () => {
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
        pushManager: {
          getSubscription: vi.fn(() => pushSubscription),
        },
      }
      globalThis.navigator = {
        serviceWorker: {
          ready: new Promise((resolve) => {
            resolve(registration)
          }),
        },
      }

      // When
      const result = await getSubscription()

      // Then
      expect(result).toEqual(pushSubscription)
      expect(result.endpoint).toEqual('fake-endpoint')
      expect(result.toJSON().keys.auth).toEqual('fake-auth')
      expect(result.toJSON().keys.p256dh).toEqual('fake-p256dh')
    })
  })

  describe('subscribePush', () => {
    test('should return PushSubscription when user subscribes to PushManager', async () => {
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
        pushManager: {
          subscribe: vi.fn(() => pushSubscription),
        },
      }
      globalThis.navigator = {
        serviceWorker: {
          ready: new Promise((resolve) => {
            resolve(registration)
          }),
        },
      }
      const mockFetchResponse = {
        text: () => Promise.resolve('fake applicationKeyResponse'),
      }
      globalThis.fetch = vi.fn(() => Promise.resolve(mockFetchResponse))

      // When
      const result = await subscribePush()

      // Then
      expect(result).toEqual(pushSubscription)
      expect(result.endpoint).toEqual('fake-endpoint')
      expect(result.toJSON().keys.auth).toEqual('fake-auth')
      expect(result.toJSON().keys.p256dh).toEqual('fake-p256dh')
    })
  })

  describe('enableNotifications', () => {
    test('should call registerUser permission is granted and is registered to service worker', async () => {
      // Given
      globalThis.Notification = {
        requestPermission: () => true,
      }
      const pushSubscription = {}
      const registration = {
        pushManager: {
          subscribe: vi.fn(() => pushSubscription),
        },
      }
      globalThis.navigator = {
        serviceWorker: {
          ready: new Promise((resolve) => {
            resolve(registration)
          }),
        },
      }

      vi.mock('$lib/registration', () => ({
        registerUser: vi.fn(() => true),
      }))
      const spy = vi.spyOn(registrationMethods, 'registerUser')

      // When
      await enableNotifications()

      // Then
      expect(spy).toHaveBeenCalled()
    })
  })
})
