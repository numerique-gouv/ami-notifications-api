import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen } from '@testing-library/svelte'
import WS from 'vitest-websocket-mock'
import Page from './+page.svelte'
import * as navigationMethods from '$app/navigation'
import * as notificationsMethods from '$lib/notifications'
import { PUBLIC_API_WS_URL } from '$lib/notifications'
import { PUBLIC_API_URL } from '$env/static/public'

let wss

describe('/+page.svelte', () => {
  beforeEach(() => {
    wss = new WS(
      `${PUBLIC_API_WS_URL}/api/v1/users/3ac73f4f-4be2-456a-9c2e-ddff480d5767/notification/events/stream`
    )
  })

  afterEach(() => {
    wss.close()
  })

  test('user has to be connected', () => {
    // Given
    expect(window.localStorage.getItem('access_token')).toEqual(null)
    const spy = vi.spyOn(navigationMethods, 'goto').mockImplementation(() => 'mocked')

    // When
    render(Page)

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith('/')
  })

  test('notification display', async () => {
    // Given
    window.localStorage.setItem('access_token', 'fake-access-token')
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementation(async () => [
        {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
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
      ])

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
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

  test('notification mark as read', async () => {
    // Given
    window.localStorage.setItem('user_id', '3ac73f4f-4be2-456a-9c2e-ddff480d5767')
    window.localStorage.setItem('access_token', 'fake-access-token')
    const spy = vi
      .spyOn(notificationsMethods, 'retrieveNotifications')
      .mockImplementationOnce(async () => [
        {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
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
      ])
      .mockImplementationOnce(async () => [
        {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          title: 'test 2',
          unread: false,
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
      ])
    const spy2 = vi
      .spyOn(notificationsMethods, 'readNotification')
      .mockImplementation(async () => {
        return {
          created_at: '2025-09-19T13:52:23.279545',
          user_id: '3ac73f4f-4be2-456a-9c2e-ddff480d5767',
          sender: 'test 2',
          message: 'test 2',
          id: 'f62c66b2-7bd5-4696-8383-2d40c08a1',
          title: 'test 2',
          unread: false,
        }
      })

    render(Page)
    await new Promise(setTimeout) // wait for async calls
    const notificationLink = screen.getByTestId(
      'notification-link-f62c66b2-7bd5-4696-8383-2d40c08a1'
    )

    // When
    await notificationLink.click()
    wss.send('ping')
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(2)
    expect(spy2).toHaveBeenCalledTimes(1)
    expect(spy2).toHaveBeenCalledWith('f62c66b2-7bd5-4696-8383-2d40c08a1')
    const notification1 = screen.getByTestId(
      'notification-f62c66b2-7bd5-4696-8383-2d40c08a1'
    )
    expect(notification1).not.toHaveClass('unread')
    const notification2 = screen.getByTestId(
      'notification-2689c3b3-e95c-4d73-b37d-55f430688af9'
    )
    expect(notification2).not.toHaveClass('unread')
  })
})
