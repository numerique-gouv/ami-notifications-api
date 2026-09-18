import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import type { WS as WSType } from 'vitest-websocket-mock';
import WS from 'vitest-websocket-mock';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import * as notificationsMethods from '$lib/notifications';
import { type AppNotification, PUBLIC_APP_WS_URL } from '$lib/notifications';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

let wss: WSType;

describe('/+page.svelte', () => {
  beforeEach(() => {
    wss = new WS(`${PUBLIC_APP_WS_URL}/api/v1/users/notification/events/stream`);

    const notifications: AppNotification[] = [];
    vi.spyOn(notificationsMethods, 'retrieveNotifications').mockResolvedValue(
      notifications
    );
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
  });

  afterEach(() => {
    wss.close();
  });

  test('user has to be connected', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
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
    await userStore.login(mockUserInfo);
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    render(Page);

    // When
    const button = screen.getByTestId('settings-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/preferences/notifications');
    });
  });

  test('notification display', async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementation(async () => [
        {
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
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
          content_icon: 'some-icon',
          partner_id: 'dinum-ami',
          item_type: null,
          item_id: null,
          item_parent_partner_id: null,
          item_parent_type: null,
          item_parent_id: null,
          url: '',
          read: true,
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

  describe('click on notification', async () => {
    test('mark notification as read', async () => {
      // Given
      const spy = vi
        .spyOn(notificationsMethods, 'retrieveNotifications')
        .mockImplementationOnce(async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
            created_at: new Date('2025-09-19T13:52:23.279545'),
            content_title: 'test 2',
            content_body: 'test 2',
            content_icon: 'fr-icon-mail-star-line',
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
        ])
        .mockImplementationOnce(async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
            created_at: new Date('2025-09-19T13:52:23.279545'),
            content_title: 'test 2',
            content_body: 'test 2',
            content_icon: 'fr-icon-smartphone-line',
            partner_id: 'dinum-ami',
            item_type: null,
            item_id: null,
            item_parent_partner_id: null,
            item_parent_type: null,
            item_parent_id: null,
            url: '',
            read: true,
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
        ]);
      const spy2 = vi
        .spyOn(notificationsMethods, 'readNotification')
        .mockImplementation(async () => {
          return {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
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
            read: true,
          };
        });

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );
      await waitFor(() => {
        const notification1 = screen.getByTestId(
          'notification-f62c66b2-7bd5-4696-8383-2d40c08a1'
        );
        expect(notification1).not.toHaveClass('read');
        const icon = notification1.querySelector('.notification__icon');
        expect(icon).toHaveClass('fr-icon-mail-star-line');
      });

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
        const icon = notification1.querySelector('.notification__icon');
        expect(icon).toHaveClass('fr-icon-smartphone-line');
      });
      const notification2 = screen.getByTestId(
        'notification-2689c3b3-e95c-4d73-b37d-55f430688af9'
      );
      expect(notification2).toHaveClass('read');
    });

    test('should redirect to parent item page when found', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
        async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
            created_at: new Date('2025-09-19T13:52:23.279545'),
            content_title: 'test 2',
            content_body: 'test 2',
            content_icon: 'icon',
            partner_id: 'dinum-ami',
            item_type: 'JCC',
            item_id: '35',
            item_parent_partner_id: 'psl',
            item_parent_type: 'OTV',
            item_parent_id: '42',
            url: 'https://www.service-public.gouv.fr',
            read: false,
          },
        ]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spyFind = vi
        .spyOn(followup, 'findItem')
        .mockReturnValue(
          new FollowupItem(
            'psl',
            'OTV',
            '42',
            'ref',
            'notifications',
            null,
            null,
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est terminée.',
            'icon',
            new Date('2026-02-20T15:55:00.000Z'),
            'closed',
            'Terminée',
            false,
            'url',
            []
          )
        );

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );

      // When
      await notificationLink.click();

      // Then
      expect(spy).toHaveBeenCalledWith('/#/followup/item/psl/OTV/42');
      expect(spyFind).toHaveBeenCalledWith('psl', 'OTV', '42');
    });

    test('should redirect to item page when parent is not found and item is found', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
        async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
            created_at: new Date('2025-09-19T13:52:23.279545'),
            content_title: 'test 2',
            content_body: 'test 2',
            content_icon: 'icon',
            partner_id: 'dinum-ami',
            item_type: 'JCC',
            item_id: '35',
            item_parent_partner_id: 'psl',
            item_parent_type: 'OTV',
            item_parent_id: '42',
            url: 'https://www.service-public.gouv.fr',
            read: false,
          },
        ]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spyFind = vi
        .spyOn(followup, 'findItem')
        .mockReturnValueOnce(null)
        .mockReturnValueOnce(
          new FollowupItem(
            'dinum-ami',
            'JCC',
            '35',
            'ref',
            'notifications',
            null,
            null,
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est terminée.',
            'icon',
            new Date('2026-02-20T15:55:00.000Z'),
            'closed',
            'Terminée',
            false,
            'url',
            []
          )
        );

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );

      // When
      await notificationLink.click();

      // Then
      expect(spy).toHaveBeenCalledWith('/#/followup/item/dinum-ami/JCC/35');
      expect(spyFind).toHaveBeenNthCalledWith(1, 'psl', 'OTV', '42');
      expect(spyFind).toHaveBeenNthCalledWith(2, 'dinum-ami', 'JCC', '35');
    });

    test('should redirect to item page when found', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
        async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
            created_at: new Date('2025-09-19T13:52:23.279545'),
            content_title: 'test 2',
            content_body: 'test 2',
            content_icon: 'icon',
            partner_id: 'dinum-ami',
            item_type: 'JCC',
            item_id: '35',
            item_parent_partner_id: null,
            item_parent_type: null,
            item_parent_id: null,
            url: 'https://www.service-public.gouv.fr',
            read: false,
          },
        ]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spyFind = vi
        .spyOn(followup, 'findItem')
        .mockReturnValue(
          new FollowupItem(
            'dinum-ami',
            'JCC',
            '35',
            'ref',
            'notifications',
            null,
            null,
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est terminée.',
            'icon',
            new Date('2026-02-20T15:55:00.000Z'),
            'closed',
            'Terminée',
            false,
            'url',
            []
          )
        );

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );

      // When
      await notificationLink.click();

      // Then
      expect(spy).toHaveBeenCalledWith('/#/followup/item/dinum-ami/JCC/35');
      expect(spyFind).toHaveBeenCalledWith('dinum-ami', 'JCC', '35');
    });

    test('should redirect to url when url is set and item is not found', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
        async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
            created_at: new Date('2025-09-19T13:52:23.279545'),
            content_title: 'test 2',
            content_body: 'test 2',
            content_icon: 'icon',
            partner_id: 'dinum-ami',
            item_type: 'JCC',
            item_id: '35',
            item_parent_partner_id: null,
            item_parent_type: null,
            item_parent_id: null,
            url: 'https://www.service-public.gouv.fr',
            read: false,
          },
        ]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spyFind = vi.spyOn(followup, 'findItem').mockReturnValue(null);

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );

      // When
      await notificationLink.click();

      // Then
      expect(spy).toHaveBeenCalledWith('https://www.service-public.gouv.fr');
      expect(spyFind).toHaveBeenCalledWith('dinum-ami', 'JCC', '35');
    });

    test('should redirect to url when is set', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
        async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
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
            url: 'https://www.service-public.gouv.fr',
            read: false,
          },
        ]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spyFind = vi.spyOn(followup, 'findItem').mockReturnValue(null);

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );

      // When
      await notificationLink.click();

      // Then
      expect(spy).toHaveBeenCalledWith('https://www.service-public.gouv.fr');
      expect(spyFind).not.toHaveBeenCalled();
    });

    test('should not redirect when url is not set', async () => {
      // Given
      vi.spyOn(notificationsMethods, 'retrieveNotifications').mockImplementationOnce(
        async () => [
          {
            id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
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
        ]
      );
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
      const followup = new Followup();
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spyFind = vi.spyOn(followup, 'findItem').mockReturnValue(null);

      render(Page);
      const notificationLink = await waitFor(() =>
        screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
      );

      // When
      await notificationLink.click();

      // Then
      expect(spy).not.toHaveBeenCalled();
      expect(spyFind).not.toHaveBeenCalled();
    });
  });
});
