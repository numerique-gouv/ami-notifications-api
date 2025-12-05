import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/svelte'
import WS from 'vitest-websocket-mock'
import type { WS as WSType } from 'vitest-websocket-mock'
import Page from './+page.svelte'
import * as navigationMethods from '$app/navigation'
import * as notificationsMethods from '$lib/notifications'
import * as authMethods from '$lib/auth'
import { PUBLIC_API_WS_URL } from '$lib/notifications'

let wss: WSType

describe('/+page.svelte', () => {
  beforeEach(() => {
    wss = new WS(`${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`)
    vi.spyOn(authMethods, 'checkAuth').mockResolvedValue(true)
  })

  afterEach(() => {
    wss.close()
  })

  test('user has to be connected', async () => {
    // Given
    vi.spyOn(authMethods, 'checkAuth').mockResolvedValue(false)
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/')
    })
  })

  test('notification display', async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementation(async () => [
        {
          send_date: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          unread: true,
        },
        {
          send_date: new Date('2025-09-19T12:59:04.950812'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          unread: false,
        },
      ])

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      const notification1 = screen.getByTestId(
        'notification-f62c66b2-7bd5-4696-8383-2d40c08a1'
      )
      expect(notification1).toHaveClass('unread')
      const notification2 = screen.getByTestId(
        'notification-2689c3b3-e95c-4d73-b37d-55f430688af9'
      )
      expect(notification2).not.toHaveClass('unread')
    })
  })

  test('notification mark as read', async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementationOnce(async () => [
        {
          send_date: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          unread: true,
        },
        {
          send_date: new Date('2025-09-19T12:59:04.950812'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          unread: false,
        },
      ])
      .mockImplementationOnce(async () => [
        {
          send_date: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          unread: false,
        },
        {
          send_date: new Date('2025-09-19T12:59:04.950812'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test',
          content_body: 'test',
          id: '2689c3b3-e95c-4d73-b37d-55f430688af9',
          content_title: 'test',
          unread: false,
        },
      ])
    const spy2 = vi
      .spyOn(notificationsMethods, 'readNotification')
      .mockImplementation(async () => {
        return {
          send_date: new Date('2025-09-19T13:52:23.279545'),
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          content_body: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          content_title: 'test 2',
          unread: false,
        }
      })

    render(Page)
    const notificationLink = await waitFor(() =>
      screen.getByTestId('notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1')
    )

    // When
    await notificationLink.click()
    wss.send('ping')

    // Then
    expect(spy).toHaveBeenCalledTimes(2)
    expect(spy2).toHaveBeenCalledTimes(1)
    expect(spy2).toHaveBeenCalledWith('f62c66b2-7bd5-4696-8383-2d40c08a1')
    await waitFor(() => {
      const notification1 = screen.getByTestId(
        'notification-f62c66b2-7bd5-4696-8383-2d40c08a1'
      )
      expect(notification1).not.toHaveClass('unread')
    })
    const notification2 = screen.getByTestId(
      'notification-2689c3b3-e95c-4d73-b37d-55f430688af9'
    )
    expect(notification2).not.toHaveClass('unread')
  })
})
