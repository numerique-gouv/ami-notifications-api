import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import * as notificationsMethods from '$lib/notifications'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mock('$lib/notifications', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, any>
      const registration = { id: 'fake-registration-id' }
      return {
        ...original,
        enableNotifications: vi.fn(() => Promise.resolve(registration)),
        disableNotifications: vi.fn(() => Promise.resolve()),
      }
    })
  })

  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue()

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/')
    })
  })

  test('should enable notifications when user toggles on', async () => {
    // Given
    const spy = vi.spyOn(notificationsMethods, 'enableNotifications')
    window.localStorage.setItem('notifications_enabled', 'false')
    render(Page)

    // When
    const toggleInput = screen.getByTestId('toggle-input')
    await fireEvent.click(toggleInput)

    // Then
    await waitFor(async () => {
      const saveSettingsButton = screen.getByTestId('save-settings-button')
      await fireEvent.click(saveSettingsButton)
    })

    await waitFor(async () => {
      expect(spy).toHaveBeenCalled()
      expect(window.localStorage.getItem('registration_id')).toEqual(
        'fake-registration-id'
      )
      expect(window.localStorage.getItem('notifications_enabled')).toEqual('true')
    })
  })

  test('should disable notifications when user toggles off', async () => {
    // Given
    const spy = vi.spyOn(notificationsMethods, 'disableNotifications')
    window.localStorage.setItem('registration_id', 'fake-registration-id')
    window.localStorage.setItem('notifications_enabled', 'true')
    render(Page)

    // When
    const toggleInput = screen.getByTestId('toggle-input')
    await fireEvent.click(toggleInput)

    // Then
    await waitFor(async () => {
      const saveSettingsButton = screen.getByTestId('save-settings-button')
      await fireEvent.click(saveSettingsButton)
    })

    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('fake-registration-id')
      expect(window.localStorage.getItem('registration_id')).toEqual('')
      expect(window.localStorage.getItem('notifications_enabled')).toEqual('false')
    })
  })

  test('should navigate to previous page when user clicks on Back button', async () => {
    // Given
    const backSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {})

    // When
    render(Page)
    const backButton = screen.getByTestId('back-button')
    await fireEvent.click(backButton)

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1)
    backSpy.mockRestore()
  })
})
