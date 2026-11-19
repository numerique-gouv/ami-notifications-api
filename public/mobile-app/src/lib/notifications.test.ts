import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as nativeInfosMethods from '$lib/bridges/nativeInfos';
import type { AppNotification } from '$lib/notifications';
import * as notificationMethods from '$lib/notifications';
import {
  countUnreadNotifications,
  countUnreadNotificationsFromStore,
  disableNotificationsAtLogout,
  fetchAndStoreNotifications,
  getNotificationsFromStore,
  readNotification,
  retrieveNotifications,
} from '$lib/notifications';
import * as registrationMethods from '$lib/registration';

describe('/notifications', () => {
  beforeEach(() => {
    vi.mock('$lib/registration', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return {
        ...original,
        unregisterRegistrationsForNative: vi.fn(() => true),
      };
    });

    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_MATOMO_ENABLED: 'true',
      });
    });
  });

  describe('fetchAndStoreNotifications', () => {
    test('should get notifications from API and store them to localStorage', async () => {
      // Given
      window.localStorage.removeItem('notifications');
      const notifications = [
        {
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          created_at: '2025-09-19T13:52:23.279545',
          content_title: 'test 2',
          content_body: 'test 2',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: false,
        },
        {
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          created_at: '2025-09-19T12:59:04.950812',
          content_title: 'test',
          content_body: 'test',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: true,
        },
      ];
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(notifications), { status: 200 })
      );

      // When
      await fetchAndStoreNotifications();

      // Then
      expect(window.localStorage.getItem('notifications')).toEqual(
        JSON.stringify(notifications)
      );
    });

    test('should not update notifications store in localStorage when API call fails', async () => {
      // Given
      const expectedNotifications: AppNotification[] = [];
      window.localStorage.setItem(
        'notifications',
        JSON.stringify(expectedNotifications)
      );
      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error());

      // When
      await fetchAndStoreNotifications();

      // Then
      expect(window.localStorage.getItem('notifications')).toEqual(
        JSON.stringify(expectedNotifications)
      );
    });
  });

  describe('getNotificationsFromStore', () => {
    test('should get notifications from localStorage and not from API', async () => {
      // Given
      const expectedNotifications: AppNotification[] = [];
      window.localStorage.setItem(
        'notifications',
        JSON.stringify(expectedNotifications)
      );
      const spy = vi.spyOn(globalThis, 'fetch');

      // When
      const result = await getNotificationsFromStore();

      // Then
      expect(result).toEqual(expectedNotifications);
      expect(spy).not.toHaveBeenCalled();
    });

    test('should return empty list if localStorage is empty', async () => {
      // Given
      const expectedNotifications: AppNotification[] = [];
      window.localStorage.removeItem('notifications');
      const spy = vi.spyOn(globalThis, 'fetch');

      // When
      const result = await getNotificationsFromStore();

      // Then
      expect(result).toEqual(expectedNotifications);
      expect(spy).not.toHaveBeenCalled();
    });
  });

  describe('getNotifications', () => {
    test('should call fetchAndStoreNotifications then getNotificationsFromStore', async () => {
      // Given
      const expectedNotifications: AppNotification[] = [];
      const fetchSpy = vi
        .spyOn(notificationMethods, 'fetchAndStoreNotifications')
        .mockResolvedValue(undefined);
      const getSpy = vi
        .spyOn(notificationMethods, 'getNotificationsFromStore')
        .mockResolvedValue(expectedNotifications);

      // When
      const result = await notificationMethods.getNotifications();

      // Then
      expect(fetchSpy).toHaveBeenCalledOnce();
      expect(getSpy).toHaveBeenCalledOnce();
      expect(result).toEqual(expectedNotifications);
    });
  });

  describe('retrieveNotifications', () => {
    test('should call getNotifications', async () => {
      // Given
      const notifications: AppNotification[] = [
        {
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          created_at: new Date('2025-09-19T13:52:23.279545'),
          content_title: 'test 2',
          content_body: 'test 2',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: false,
        },
        {
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          created_at: new Date('2025-09-19T12:59:04.950812'),
          content_title: 'test',
          content_body: 'test',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: true,
        },
      ];
      vi.spyOn(notificationMethods, 'getNotifications').mockResolvedValue(
        notifications
      );

      // When
      const result = await retrieveNotifications();

      // Then
      expect(result).toEqual(notifications);
    });
  });

  describe('countUnreadNotifications', () => {
    test('should call fetchAndStoreNotifications and return unread notifications', async () => {
      // Given
      const spy = vi.spyOn(notificationMethods, 'fetchAndStoreNotifications');
      vi.spyOn(
        notificationMethods,
        'countUnreadNotificationsFromStore'
      ).mockReturnValue(1);

      // When
      const result = await countUnreadNotifications();

      // Then
      expect(result).toEqual(1);
      expect(spy).toHaveBeenCalled();
    });
  });

  describe('countUnreadNotificationsFromStore', () => {
    test('should call getNotificationsFromStore and filter unread notifications', async () => {
      // Given
      const notifications: AppNotification[] = [
        {
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          created_at: new Date('2025-09-19T13:52:23.279545'),
          content_title: 'test 2',
          content_body: 'test 2',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: false,
        },
        {
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          created_at: new Date('2025-09-19T12:59:04.950812'),
          content_title: 'test',
          content_body: 'test',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: true,
        },
      ];
      vi.spyOn(notificationMethods, 'getNotificationsFromStore').mockReturnValue(
        notifications
      );

      // When
      const result = countUnreadNotificationsFromStore();

      // Then
      expect(result).toEqual(1);
    });
  });

  describe('readNotification', () => {
    test('should mark notification as read', async () => {
      // Given
      const read_notification = [
        {
          id: 'f62c66b2-7bd5-4696-883-2d40c08a1',
          created_at: '2025-09-19T13:52:23.279545',
          content_title: 'test 2',
          content_body: 'test 2',
          content_icon: 'icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: true,
        },
      ];
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(read_notification), { status: 200 })
      );

      // When
      const result = await readNotification('f62c66b2-7bd5-4696-883-2d40c08a1');

      // Then
      expect(result).toEqual(read_notification);
    });
  });

  describe('disableNotificationsAtLogout', () => {
    test('should call unregisterRegistrationsForNative when user has deviceId', async () => {
      // Given
      vi.spyOn(nativeInfosMethods, 'getDeviceId').mockReturnValue('fake-device-id');
      const spyUnregisterRegistrationsForNative = vi.spyOn(
        registrationMethods,
        'unregisterRegistrationsForNative'
      );

      // When
      await disableNotificationsAtLogout();

      // Then
      expect(spyUnregisterRegistrationsForNative).toHaveBeenCalledWith(
        'fake-device-id'
      );
    });
  });
});
