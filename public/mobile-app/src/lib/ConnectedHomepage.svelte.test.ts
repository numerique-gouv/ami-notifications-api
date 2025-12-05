import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import WS from 'vitest-websocket-mock'
import type { WS as WSType } from 'vitest-websocket-mock'
import { render, screen, waitFor } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'
import * as notificationsMethods from '$lib/notifications'
import * as agendaMethods from '$lib/agenda'
import * as authMethods from '$lib/auth'
import { Agenda, Item } from '$lib/agenda'
import { PUBLIC_API_WS_URL } from '$lib/notifications'
import { franceConnectLogout } from './france-connect'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'

let wss: WSType

describe('/ConnectedHomepage.svelte', () => {
  beforeEach(() => {
    vi.stubGlobal('navigator', {
      ...navigator,
      permissions: undefined,
    })
    userStore.login(mockUserInfo)

    vi.mock('$lib/api-particulier', () => ({
      getQuotientData: vi.fn().mockImplementation(() => {
        return {
          data: { foo: 'bar' },
        }
      }),
    }))

    vi.mock('$lib/notifications', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, any>
      const registration = { id: 'fake-registration-id' }
      return {
        ...original,
        enableNotifications: vi.fn(() => Promise.resolve(registration)),
        disableNotifications: vi.fn(() => Promise.resolve()),
        countUnreadNotifications: vi.fn(() => 3),
      }
    })

    vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda([]))

    window.localStorage.setItem('user_address', '')
    window.localStorage.setItem('notifications_enabled', 'false')
    window.localStorage.setItem('user_data', 'fake-user-data')
    window.localStorage.setItem('emailLocalStorage', 'test@email.fr')
    window.localStorage.setItem('pushSubscriptionLocalStorage', '{}')

    wss = new WS(`${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`)
  })

  afterEach(() => {
    wss.close()
  })

  test("should display user's initials on menu", async () => {
    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const initials = container.querySelector('.user-profile')
      expect(initials).toHaveTextContent('ACL')
    })
  })

  test("should display user's quotient data", async () => {
    // When
    const { container } = await render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const accordion = container.querySelector('#accordion-1')
      expect(accordion).toHaveTextContent('quotientinfo: { "data": { "foo": "bar" }')
    })
  })

  test("should display user's notification count", async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'countUnreadNotifications')
      .mockResolvedValue(3)

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      const icon = container.querySelector('#notification-icon')
      expect(icon).toHaveTextContent('3')
    })
  })

  test("should refresh user's notification count", async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'countUnreadNotifications')
      .mockResolvedValueOnce(3)
      .mockResolvedValueOnce(4)

    const { container } = render(ConnectedHomepage)
    await waitFor(() => {
      const icon = container.querySelector('#notification-icon')
      expect(icon).toHaveTextContent('3')
    })

    // When
    wss.send('ping')

    // Then
    expect(spy).toHaveBeenCalledTimes(2)
    await waitFor(() => {
      const icon = container.querySelector('#notification-icon')
      expect(icon).toHaveTextContent('4')
    })
  })

  test("should display 'Ne plus recevoir de notifications' link when notifications are enabled", async () => {
    // Given
    window.localStorage.setItem('notifications_enabled', 'true')

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const menu = container.querySelector('.menu')
      expect(menu).toHaveTextContent(
        'Ne plus recevoir de notifications sur ce terminal'
      )
    })
  })

  test("should display 'Ne plus recevoir de notifications' link when click on enable notifications", async () => {
    // Given
    const spy = vi.spyOn(notificationsMethods, 'enableNotifications')

    const { container } = render(ConnectedHomepage)

    const toggleMenuButton = await waitFor(() =>
      screen.getByTestId('toggle-menu-button')
    )
    await toggleMenuButton.click()

    const enableNotificationsLink = await waitFor(() =>
      screen.getByTestId('enable-notifications')
    )

    // When
    await enableNotificationsLink.click()

    // Then
    await waitFor(() => {
      const menu = container.querySelector('.menu')
      expect(spy).toHaveBeenCalled()
      expect(menu).toHaveTextContent(
        'Ne plus recevoir de notifications sur ce terminal'
      )
      expect(window.localStorage.getItem('notifications_enabled')).toBe('true')
    })
  })

  test("should display 'Recevoir des notifications' link when notifications are disabled", async () => {
    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const menu = container.querySelector('.menu')
      expect(menu).toHaveTextContent('Recevoir des notifications sur ce terminal')
    })
  })

  test("should display 'Recevoir des notifications' link when click on disable notifications", async () => {
    // Given
    const fakeRegistrationId = 'fake-registration-id'
    const spy = vi.spyOn(notificationsMethods, 'disableNotifications')

    const { container } = render(ConnectedHomepage)

    const toggleMenuButton = await waitFor(() =>
      screen.getByTestId('toggle-menu-button')
    )
    await toggleMenuButton.click()

    const enableNotificationsLink = await waitFor(() =>
      screen.getByTestId('enable-notifications')
    )
    await enableNotificationsLink.click()

    const disableNotificationsLink = await waitFor(() =>
      screen.getByTestId('disable-notifications')
    )

    // When
    await disableNotificationsLink.click()

    // Then
    await waitFor(() => {
      const menu = container.querySelector('.menu')
      expect(spy).toHaveBeenCalledWith(fakeRegistrationId)
      expect(menu).toHaveTextContent('Recevoir des notifications sur ce terminal')
      expect(window.localStorage.getItem('notifications_enabled')).toBe('false')
    })
  })

  test('should display address block when user address is not known (empty)', async () => {
    // Given
    window.localStorage.setItem('user_address', '')

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.address-container')
      expect(addressBlock).toHaveTextContent(
        'Gagnez du temps en renseignant votre adresse une seule fois !'
      )
    })
  })

  test('should display address block when user address is not known (null)', async () => {
    // Given
    window.localStorage.removeItem('user_address')

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.address-container')
      expect(addressBlock).toHaveTextContent(
        'Gagnez du temps en renseignant votre adresse une seule fois !'
      )
    })
  })

  test('should not display address block when user address is known', async () => {
    // Given
    window.localStorage.setItem('user_address', '26 rue Desaix 75015 Paris')

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.first-block-container')
      expect(addressBlock).toBeNull()
    })
  })

  test('Should display first holiday found from API', async () => {
    // Given
    const agenda = new Agenda([])
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([
      new Item('holiday', 'Holiday 1', null, new Date()),
      new Item('holiday', 'Holiday 2', null, new Date()),
    ])
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('holiday', 'Holiday 3', null, new Date()),
      new Item('holiday', 'Holiday 4', null, new Date()),
    ])
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda)

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const agendaBlock = container.querySelector('.agenda-container')
      expect(spy).toHaveBeenCalledTimes(1)
      expect(agendaBlock).toHaveTextContent('Holiday 1')
      expect(agendaBlock).not.toHaveTextContent('Holiday 2')
      expect(agendaBlock).not.toHaveTextContent('Holiday 3')
      expect(agendaBlock).not.toHaveTextContent('Holiday 4')
      expect(agendaBlock).not.toHaveTextContent(
        'Retrouvez les temps importants de votre vie administrative ici'
      )
    })
  })

  test('Should display first holiday found from API - now is empty', async () => {
    // Given
    const agenda = new Agenda([])
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([])
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('holiday', 'Holiday 1', null, new Date()),
      new Item('holiday', 'Holiday 2', null, new Date()),
    ])
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda)

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const agendaBlock = container.querySelector('.agenda-container')
      expect(spy).toHaveBeenCalledTimes(1)
      expect(agendaBlock).toHaveTextContent('Holiday 1')
      expect(agendaBlock).not.toHaveTextContent('Holiday 2')
      expect(agendaBlock).not.toHaveTextContent(
        'Retrouvez les temps importants de votre vie administrative ici'
      )
    })
  })

  test('should display calendar block if agenda is empty', async () => {
    // Given
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda([]))

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const agendaBlock = container.querySelector('.agenda-container')
      expect(agendaBlock).toHaveTextContent(
        'Retrouvez les temps importants de votre vie administrative ici'
      )
    })
  })

  test('should call userStore.logout', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }))
    const spyLogout = vi.spyOn(userStore, 'logout').mockResolvedValue()

    // When
    render(ConnectedHomepage)
    const franceConnectLogoutButton = screen.getByRole('button', {
      name: 'Me déconnecter',
    })
    await franceConnectLogoutButton.click()

    // Then
    expect(spyLogout).toHaveBeenCalled()
  })
})
