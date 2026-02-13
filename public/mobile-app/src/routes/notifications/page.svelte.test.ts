import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import type { WS as WSType } from 'vitest-websocket-mock';
import WS from 'vitest-websocket-mock';
import * as navigationMethods from '$app/navigation';
import * as notificationsMethods from '$lib/notifications';
import { PUBLIC_API_WS_URL } from '$lib/notifications';
import { expectBackButtonPresent } from '$tests/utils';
import Page from './+page.svelte';

let wss: WSType;

describe('/+page.svelte', () => {
  beforeEach(() => {
    wss = new WS(`${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`);
  });

  afterEach(() => {
    wss.close();
  });

  test('user has to be connected', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });

  test('should navigate to Settings when user clicks on Gérer button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    render(Page);

    // When
    const button = screen.getByTestId('settings-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(2);
      expect(spy).toHaveBeenNthCalledWith(1, '/');
      expect(spy).toHaveBeenNthCalledWith(2, '/#/settings');
    });
  });

  test('notification display', async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementation(async () => [
        {
          created_at: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          read: false,
          item_external_url: '',
        },
        {
          created_at: new Date('2025-09-19T12:59:04.950812'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          content_icon: 'some-icon',
          read: true,
          item_external_url: '',
        },
      ]);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      const notification1 = screen.getByTestId(
        'notification-f62c66b2-7bd5-4696-8383-2d40c08a1'
      );
      expect(notification1).not.toHaveClass('read');
      const notification2 = screen.getByTestId(
        'notification-2689c3b3-e95c-4d73-b37d-55f430688af9'
      );
      expect(notification2).toHaveClass('read');
    });
  });

  test('notification mark as read', async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementationOnce(async () => [
        {
          created_at: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          read: false,
          item_external_url: '',
        },
        {
          created_at: new Date('2025-09-19T12:59:04.950812'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          read: true,
          item_external_url: '',
        },
      ])
      .mockImplementationOnce(async () => [
        {
          created_at: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          read: true,
          item_external_url: '',
        },
        {
          created_at: new Date('2025-09-19T12:59:04.950812'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          read: true,
          item_external_url: '',
        },
      ]);
    const spy2 = vi
      .spyOn(notificationsMethods, 'readNotification')
      .mockImplementation(async () => {
        return {
          created_at: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          read: true,
          item_external_url: '',
        };
      });

    render(Page);
    const notificationLink = await waitFor(() =>
      screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
    );

    // When
    await notificationLink.click();
    wss.send('ping');

    // Then
    expect(spy).toHaveBeenCalledTimes(2);
    expect(spy2).toHaveBeenCalledTimes(1);
    expect(spy2).toHaveBeenCalledWith('f62c66b2-7bd5-4696-8383-2d40c08a1');
    await waitFor(() => {
      const notification1 = screen.getByTestId(
        'notification-f62c66b2-7bd5-4696-8383-2d40c08a1'
      );
      expect(notification1).toHaveClass('read');
    });
    const notification2 = screen.getByTestId(
      'notification-2689c3b3-e95c-4d73-b37d-55f430688af9'
    );
    expect(notification2).toHaveClass('read');
  });

  test('should redirect to item_external_url when is set and user clicks on notification', async () => {
    // Given
    vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
      async () => [
        {
          created_at: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          read: false,
          item_external_url: 'https://www.service-public.gouv.fr',
        },
      ]
    );
    vi.stubGlobal('location', { href: 'fake-link' });

    render(Page);
    const notificationLink = await waitFor(() =>
      screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
    );

    // When
    await notificationLink.click();
    wss.send('ping');

    // Then
    expect(globalThis.window.location.href).toBe('https://www.service-public.gouv.fr');
  });

  test('should not redirect when item_external_url is not set and user clicks on notification', async () => {
    // Given
    vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
      async () => [
        {
          created_at: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          read: false,
          item_external_url: '',
        },
      ]
    );
    vi.stubGlobal('location', { href: 'fake-link' });

    render(Page);
    const notificationLink = await waitFor(() =>
      screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
    );

    // When
    await notificationLink.click();
    wss.send('ping');

    // Then
    expect(globalThis.window.location.href).toBe('fake-link');
  });
});
