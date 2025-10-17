import { afterEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import {
  countUnreadNotifications,
  disableNotifications,
  enableNotifications,
  readNotification,
  retrieveNotifications,
  subscribePush,
  unsubscribePush,
} from '$lib/notifications.ts'
import * as registrationMethods from '$lib/registration.js'

describe('/notifications.ts', () => {
  afterEach(() => {
    window.localStorage.clear()
  })

  describe('retrieveNotifications', () => {
    test('user_id should be set', async () => {
      // Given
      expect(window.localStorage.getItem('user_id')).toEqual(null)

      // When
      const result = await retrieveNotifications()

      // Then
      expect(result).toEqual([])
    })

    test('should get notifications from API', async () => {
      // Given
      window.localStorage.setItem('user_id', 'fake-user-id')
      const notifications = [
        {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          title: 'test 2',
          unread: true,
        },
        {
          created_at: '2025-09-19T12:59:04.950812',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          message: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          title: 'test',
          unread: false,
        },
      ]
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => Promise.resolve(notifications),
        })
      )

      // When
      const result = await retrieveNotifications()

      // Then
      expect(result).toEqual(notifications)
    })
  })

  describe('countUnreadNotifications', () => {
    test('user_id should be set', async () => {
      // Given
      expect(window.localStorage.getItem('user_id')).toEqual(null)

      // When
      const result = await countUnreadNotifications()

      // Then
      expect(result).toEqual(0)
    })

    test('should count unread notifications from API', async () => {
      // Given
      window.localStorage.setItem('user_id', 'fake-user-id')
      const notifications = [
        {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          title: 'test 2',
          unread: true,
        },
      ]
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => Promise.resolve(notifications),
        })
      )

      // When
      const result = await countUnreadNotifications()

      // Then
      expect(result).toEqual(1)
    })
  })

  describe('readNotification', () => {
    test('user_id should be set', async () => {
      // Given
      expect(window.localStorage.getItem('user_id')).toEqual(null)

      // When
      const result = await readNotification('unknown')

      // Then
      expect(result).toEqual(undefined)
    })

    test('should mark notification as read', async () => {
      // Given
      window.localStorage.setItem('user_id', 'fake-user-id')
      const read_notification = [
        {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          title: 'test 2',
          unread: false,
        },
      ]
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => Promise.resolve(read_notification),
        })
      )

      // When
      const result = await readNotification('f62c66b2-7bd5-4696-883-2d40c08a1')

      // Then
      expect(result).toEqual(read_notification)
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
    test('should call registerDevice when permission is granted and is registered to service worker', async () => {
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
      const mockFetchResponse = {
        text: () => Promise.resolve('fake applicationKeyResponse'),
      }
      globalThis.fetch = vi.fn(() => Promise.resolve(mockFetchResponse))

      const registrationResult = {}
      vi.mock('$lib/registration', () => ({
        registerDevice: vi.fn(() => Promise.resolve(registrationResult)),
      }))
      const spy = vi.spyOn(registrationMethods, 'registerDevice')

      // When
      await enableNotifications()

      // Then
      expect(spy).toHaveBeenCalledWith(pushSubscription)
    })
  })

  describe('unsubscribePush', () => {
    test('should call unsubscribe and log result when success', async () => {
      // Given
      const pushSubscription = {
        unsubscribe: () => Promise.resolve(true),
      }
      const consoleMock = vi.spyOn(console, 'log')

      // When
      await unsubscribePush(pushSubscription)

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(1)
      expect(consoleMock).toHaveBeenCalledWith('unsubscribed to the push manager')
    })

    test('should call unsubscribe and log result when failure', async () => {
      // Given
      const pushSubscription = {
        unsubscribe: () => Promise.resolve(false),
      }
      const consoleMock = vi.spyOn(console, 'log')

      // When
      await unsubscribePush(pushSubscription)

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(1)
      expect(consoleMock).toHaveBeenCalledWith(
        'failed to unsubscribe to the push manager'
      )
    })
  })

  describe('disableNotifications', () => {
    test('should call unregisterDevice and unsubscribePush when permission is granted and is registered to service worker', async () => {
      // Given
      globalThis.Notification = {
        requestPermission: () => true,
      }
      const pushSubscription = {
        unsubscribe: () => Promise.resolve(true),
      }
      const registration = {
        pushManager: {
          getSubscription: vi.fn(() => Promise.resolve(pushSubscription)),
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
        registerDevice: vi.fn(() => true),
        unregisterDevice: vi.fn(() => true),
      }))
      const spyUnregisterDevice = vi.spyOn(registrationMethods, 'unregisterDevice')
      const consoleMock = vi.spyOn(console, 'log')

      // When
      await disableNotifications(11)

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(2)
      expect(consoleMock).toHaveBeenCalledWith('unregisterDevice')
      expect(spyUnregisterDevice).toHaveBeenCalledWith(11)
      expect(consoleMock).toHaveBeenCalledWith('unsubscribed to the push manager')
    })

    test('should log error message when Notification permission is not granted', async () => {
      // Given
      globalThis.Notification = {
        requestPermission: () => false,
      }
      const consoleMock = vi.spyOn(console, 'log')

      // When
      await disableNotifications(11)

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(1)
      expect(consoleMock).toHaveBeenCalledWith(
        'No notification: missing permission or missing service worker registration'
      )
    })

    test('should log error message when serviceWorker is not ready', async () => {
      // Given
      globalThis.Notification = {
        requestPermission: () => true,
      }
      globalThis.navigator = {
        serviceWorker: {
          ready: new Promise((reject) => {
            reject()
          }),
        },
      }
      const consoleMock = vi.spyOn(console, 'log')

      // When
      await disableNotifications(11)

      // Then
      expect(consoleMock).toHaveBeenCalledTimes(1)
      expect(consoleMock).toHaveBeenCalledWith(
        'No notification: missing permission or missing service worker registration'
      )
    })
  })
})
