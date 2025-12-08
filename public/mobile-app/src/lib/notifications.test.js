import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import {
  countUnreadNotifications,
  disableNotifications,
  enableNotifications,
  readNotification,
  retrieveNotifications,
  subscribePush,
  unsubscribePush,
} from '$lib/notifications'
import * as registrationMethods from '$lib/registration'
import { mockPushSubscription } from '$tests/utils'

describe('/notifications', () => {
  describe('retrieveNotifications', () => {
    test('should get notifications from API', async () => {
      // Given
      const notifications = [
        {
          send_date: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          content_title: 'test 2',
          unread: true,
        },
        {
          send_date: '2025-09-19T12:59:04.950812',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          unread: false,
        },
      ]
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(notifications), { status: 200 })
      )

      // When
      const result = await retrieveNotifications()

      // Then
      expect(result).toEqual(notifications)
    })
  })

  describe('countUnreadNotifications', () => {
    test('should count unread notifications from API', async () => {
      // Given
      const notifications = [
        {
          send_date: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          content_title: 'test 2',
          unread: true,
        },
      ]
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(notifications), { status: 200 })
      )

      // When
      const result = await countUnreadNotifications()

      // Then
      expect(result).toEqual(1)
    })
  })

  describe('readNotification', () => {
    test('should mark notification as read', async () => {
      // Given
      const read_notification = [
        {
          send_date: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          content_title: 'test 2',
          unread: false,
        },
      ]
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(read_notification), { status: 200 })
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
      vi.stubGlobal('navigator', {
        ...navigator,
        serviceWorker: {
          ready: Promise.resolve(registration),
        },
      })
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('fake applicationKeyResponse', { status: 200 })
      )

      // When
      const result = await subscribePush()

      // Then
      expect(result).toEqual(pushSubscription)
      expect(result?.endpoint).toEqual('fake-endpoint')
      expect(result?.toJSON()?.keys?.auth).toEqual('fake-auth')
      expect(result?.toJSON()?.keys?.p256dh).toEqual('fake-p256dh')
    })
  })

  describe('enableNotifications', () => {
    test('should call registerDevice when permission is granted and is registered to service worker', async () => {
      // Given
      vi.stubGlobal('Notification', {
        requestPermission: () => Promise.resolve(true),
      })
      const pushSubscription = {}
      const registration = {
        pushManager: {
          subscribe: vi.fn(() => pushSubscription),
        },
      }
      vi.stubGlobal('navigator', {
        ...navigator,
        serviceWorker: {
          ready: Promise.resolve(registration),
        },
      })
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('fake applicationKeyResponse', { status: 200 })
      )

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
    test('should call unsubscribe and return true when success', async () => {
      // Given
      const pushSubscription = {
        ...mockPushSubscription,
        unsubscribe: () => Promise.resolve(true),
      }

      // When
      const hasUnsubscribed = await unsubscribePush(pushSubscription)

      // Then
      expect(hasUnsubscribed).toEqual(true)
    })

    test('should call unsubscribe and return false when failure', async () => {
      // Given
      const pushSubscription = {
        ...mockPushSubscription,
        unsubscribe: () => Promise.resolve(false),
      }

      // When
      const hasUnsubscribed = await unsubscribePush(pushSubscription)

      // Then
      expect(hasUnsubscribed).toEqual(false)
    })
  })

  describe('disableNotifications', () => {
    test('should call unregisterDevice and unsubscribePush when permission is granted and is registered to service worker', async () => {
      // Given
      vi.stubGlobal('Notification', {
        requestPermission: () => Promise.resolve(true),
      })
      const pushSubscription = {
        ...mockPushSubscription,
        unsubscribe: () => Promise.resolve(true),
      }
      const registration = {
        pushManager: {
          getSubscription: vi.fn(() => Promise.resolve(pushSubscription)),
        },
      }
      vi.stubGlobal('navigator', {
        ...navigator,
        serviceWorker: {
          ready: Promise.resolve(registration),
        },
      })

      vi.mock('$lib/registration', () => ({
        registerDevice: vi.fn(() => true),
        unregisterDevice: vi.fn(() => true),
      }))
      const spyUnregisterDevice = vi.spyOn(registrationMethods, 'unregisterDevice')

      // When
      const result = await disableNotifications('11')

      // Then
      expect(spyUnregisterDevice).toHaveBeenCalledWith('11')
      expect(result).toEqual(pushSubscription)
    })

    test('should return false when Notification permission is not granted', async () => {
      // Given
      vi.stubGlobal('Notification', {
        requestPermission: () => Promise.resolve(false),
      })

      // When
      const result = await disableNotifications('11')

      // Then
      expect(result).toEqual(false)
    })
  })
})
