import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import * as notificationsMethods from '$lib/notifications'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mock('$lib/notifications', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, any>
      const registration = { id: 'fake-registration-id' }
      return {
        ...original,
        enableNotifications: vi.fn(() => Promise.resolve(registration)),
      }
    })
  })

  test('user has to be connected', async () => {
    // Given
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

  test('should enable notifications when user clicks on Activer button', async () => {
    // Given
    await userStore.login(mockUserInfo)
    const spy = vi.spyOn(notificationsMethods, 'enableNotifications')
    window.localStorage.setItem('notifications_enabled', 'false')
    render(Page)

    // When
    const button = screen.getByTestId('enable-button')
    await fireEvent.click(button)

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalled()
      expect(window.localStorage.getItem('registration_id')).toEqual(
        'fake-registration-id'
      )
      expect(window.localStorage.getItem('notifications_enabled')).toEqual('true')
    })
  })

  test('should navigate to the homepage when user clicks on Activer button', async () => {
    // Given
    await userStore.login(mockUserInfo)
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('enable-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/?has_enabled_notifications')
    })
  })

  test('should navigate to the homepage when user clicks on Skip button', async () => {
    // Given
    await userStore.login(mockUserInfo)
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('skip-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/')
    })
  })
})
