import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import {
  createScheduledNotification,
  deleteScheduledNotifications,
} from '$lib/scheduled-notifications';

describe('/scheduled-notifications', () => {
  describe('createScheduledNotification', () => {
    test('should create scheduled notification', async () => {
      // Given
      const scheduledNotification = {
        content_title: 'title',
        content_body: 'body',
        content_icon: 'icon',
        reference: 'reference',
        internal_url: '',
        scheduled_at: new Date(),
      };

      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 200 })
      );

      // When
      const result = await createScheduledNotification(scheduledNotification);

      // Then
      expect(result).toEqual(true);
    });
    test('create scheduled notification failure', async () => {
      // Given
      const scheduledNotification = {
        content_title: 'title',
        content_body: 'body',
        content_icon: 'icon',
        reference: 'reference',
        internal_url: '',
        scheduled_at: new Date(),
      };

      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 400 })
      );

      // When
      const result = await createScheduledNotification(scheduledNotification);

      // Then
      expect(result).toEqual(false);
    });
  });

  describe('deleteScheduledNotifications', () => {
    test('should delete scheduled notifications', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(null, { status: 204 })
      );

      // When
      const result = await deleteScheduledNotifications();

      // Then
      expect(result).toEqual(true);
    });
    test('delete scheduled notification failure', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 400 })
      );

      // When
      const result = await deleteScheduledNotifications();

      // Then
      expect(result).toEqual(false);
    });
  });
});
