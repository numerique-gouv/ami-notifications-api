import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import type { WS as WSType } from 'vitest-websocket-mock'
import WS from 'vitest-websocket-mock'
import * as navigationMethods from '$app/navigation'
import * as agendaMethods from '$lib/agenda'
import { Agenda, Item } from '$lib/agenda'
import * as notificationsMethods from '$lib/notifications'
import { PUBLIC_API_WS_URL } from '$lib/notifications'
import { userStore } from '$lib/state/User.svelte'
import { mockAddress, mockUserInfo } from '$tests/utils'
import ConnectedHomepage from './ConnectedHomepage.svelte'

let wss: WSType

describe('/ConnectedHomepage.svelte', () => {
  beforeEach(async () => {
    await userStore.login(mockUserInfo)

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

    vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda())

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
      expect(initials).toHaveTextContent('A')
      expect(initials).not.toHaveTextContent('ACL')
    })
  })

  test('should navigate to User profile page when user clicks on Mon profil button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(ConnectedHomepage)

    // When
    const button = screen.getByTestId('profile-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/#/profile')
    })
  })

  test('should navigate to Settings page when user clicks on Paramétrer button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(ConnectedHomepage)

    // When
    const button = screen.getByTestId('settings-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/#/settings')
    })
  })

  test('should navigate to Contact page when user clicks on Nous contacter button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(ConnectedHomepage)

    // When
    const button = screen.getByTestId('contact-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/contact')
    })
  })

  test('should call userStore.logout when user clicks on Me déconnecter button', async () => {
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

  test('should display address block when user address is not known (empty)', async () => {
    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.address-container')
      expect(addressBlock).toHaveTextContent(
        "Renseignez votre adresse sur l'application pour faciliter vos échanges !"
      )
    })
  })

  test('should display address block when user address is not known (null)', async () => {
    // Given
    delete userStore.connected?.identity?.address

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.address-container')
      expect(addressBlock).toHaveTextContent(
        "Renseignez votre adresse sur l'application pour faciliter vos échanges !"
      )
    })
  })

  test('should not display address block when user address is known', async () => {
    // Given
    userStore.connected!.setAddress(mockAddress)

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
    const agenda = new Agenda()
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
    const agenda = new Agenda()
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
})
