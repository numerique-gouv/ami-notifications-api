import { describe, test, expect, vi, beforeEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'
import * as notificationsMethods from '$lib/notifications.js'

describe('/ConnectedHomepage.svelte', () => {
  beforeEach(() => {
    globalThis.navigator = {
      permissions: undefined,
    }

    vi.mock('$lib/france-connect', () => ({
      parseJwt: vi.fn().mockImplementation(() => {
        return {
          given_name_array: ['Pierre', 'Arthur', 'Félix'],
        }
      }),
      franceConnectLogout: vi.fn(),
    }))

    vi.mock('$lib/api-particulier', () => ({
      getQuotientData: vi.fn().mockImplementation(() => {
        return {
          data: { foo: 'bar' },
        }
      }),
    }))

    vi.mock('$lib/notifications', async (importOriginal) => {
      const original = await importOriginal()
      const registration = { id: 'fake-registration-id' }
      return {
        ...original,
        enableNotifications: vi.fn(() => Promise.resolve(registration)),
        disableNotifications: vi.fn(() => Promise.resolve()),
        countUnreadNotifications: vi.fn().mockImplementation(() => 3),
      }
    })

    window.localStorage.setItem('notifications_enabled', 'false')
    window.localStorage.setItem('user_data', 'fake-user-data')
    window.localStorage.setItem('emailLocalStorage', 'test@email.fr')
    window.localStorage.setItem('pushSubscriptionLocalStorage', '{}')
  })

  test("should display user's initials on menu", async () => {
    // When
    const { container } = render(ConnectedHomepage)
    await new Promise(setTimeout) // wait for async calls

    // Then
    const initials = container.querySelector('.user-profile')
    expect(initials).toHaveTextContent('PAF')
    const accordion = container.querySelector('#accordion-1')
    expect(accordion).toHaveTextContent('quotientinfo: { "data": { "foo": "bar" }')
    const icon = container.querySelector('#notification-icon')
    expect(icon).toHaveTextContent('3')
  })

  test("should display 'Ne plus recevoir de notifications' link when notifications are enabled", async () => {
    // Given
    window.localStorage.setItem('notifications_enabled', 'true')

    // When
    const { container } = render(ConnectedHomepage)
    await new Promise(setTimeout) // wait for async calls

    // Then
    const menu = container.querySelector('.menu')
    expect(menu).toHaveTextContent('Ne plus recevoir de notifications sur ce terminal')
  })

  test("should display 'Ne plus recevoir de notifications' link when click on enable notifications", async () => {
    // Given
    const spy = vi.spyOn(notificationsMethods, 'enableNotifications')

    const { container } = render(ConnectedHomepage)
    await new Promise(setTimeout) // wait for async calls

    const toggleMenuButton = screen.getByTestId('toggle-menu-button')
    await toggleMenuButton.click()
    await new Promise(setTimeout) // wait for async calls

    const enableNotificationsLink = screen.getByTestId('enable-notifications')

    // When
    await enableNotificationsLink.click()
    await new Promise(setTimeout) // wait for async calls

    // Then
    const menu = container.querySelector('.menu')
    expect(spy).toHaveBeenCalled()
    expect(menu).toHaveTextContent('Ne plus recevoir de notifications sur ce terminal')
    expect(window.localStorage.getItem('notifications_enabled')).toBe('true')
  })

  test("should display 'Recevoir des notifications' link when notifications are disabled", async () => {
    // When
    const { container } = render(ConnectedHomepage)
    await new Promise(setTimeout) // wait for async calls

    // Then
    const menu = container.querySelector('.menu')
    expect(menu).toHaveTextContent('Recevoir des notifications sur ce terminal')
  })

  test("should display 'Recevoir des notifications' link when click on disable notifications", async () => {
    // Given
    const fakeRegistrationId = 'fake-registration-id'
    const spy = vi.spyOn(notificationsMethods, 'disableNotifications')

    const { container } = render(ConnectedHomepage)
    await new Promise(setTimeout) // wait for async calls

    const toggleMenuButton = screen.getByTestId('toggle-menu-button')
    await toggleMenuButton.click()
    await new Promise(setTimeout) // wait for async calls

    const enableNotificationsLink = screen.getByTestId('enable-notifications')
    await enableNotificationsLink.click()
    await new Promise(setTimeout) // wait for async calls

    const disableNotificationsLink = screen.getByTestId('disable-notifications')

    // When
    await disableNotificationsLink.click()
    await new Promise(setTimeout) // wait for async calls

    // Then
    const menu = container.querySelector('.menu')
    expect(spy).toHaveBeenCalledWith(fakeRegistrationId)
    expect(menu).toHaveTextContent('Recevoir des notifications sur ce terminal')
    expect(window.localStorage.getItem('notifications_enabled')).toBe('false')
  })
})
