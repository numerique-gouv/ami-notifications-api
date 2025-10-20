import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/svelte'
import Page from './+page.svelte'
import * as navigationMethods from '$app/navigation'
import * as notificationsMethods from '$lib/notifications'

describe('/+page.svelte', () => {
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
          date: '2025-09-19T12:59:04.950812',
          user_id: 42,
          sender: 'test',
          message: 'test',
          id: 29,
          title: 'test',
          unread: false,
        },
        {
          date: '2025-09-19T13:52:23.279545',
          user_id: 42,
          sender: 'test 2',
          message: 'test 2',
          id: 30,
          title: 'test 2',
          unread: true,
        },
      ])

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    const notification1 = screen.getByTestId('notification-29')
    expect(notification1).not.toHaveClass('unread')
    const notification2 = screen.getByTestId('notification-30')
    expect(notification2).toHaveClass('unread')
  })
})
