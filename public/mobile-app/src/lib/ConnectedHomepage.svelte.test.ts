import { beforeEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'
import { franceConnectLogout } from './france-connect.js'

beforeEach(async () => {
  vi.mock('$lib/france-connect', () => ({
    parseJwt: vi.fn().mockImplementation(() => {
      return {
        aud: 'bc3ef03e2748a585005be828f9d1a9719c46df4e728115a106e6c8ee6ddcbacc',
        birthcountry: '99100',
        birthdate: '1969-03-17',
        birthplace: '95277',
        email: 'ymmyffarapp-1777@yopmail.com',
        exp: 1758012270,
        family_name: 'MERCIER',
        gender: 'male',
        given_name: 'Pierre Arthur Félix',
        given_name_array: ['Pierre', 'Arthur', 'Félix'],
        iat: 1758012216,
        iss: 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2',
        preferred_username: 'DUBOIS',
        sub: '328909e55774c7d7039d2c5716d2c93bf4e368f24fb42dc9e4e8009a82367157v1',
      }
    }),
    franceConnectLogout: vi.fn(),
  }))
})

describe('/ConnectedHomepage.svelte', () => {
  test("should display user's initials on menu", async () => {
    // Given
    globalThis.Notification = {}

    vi.mock('$lib/api-particulier', () => ({
      getQuotientData: vi.fn().mockImplementation(() => {
        return {
          data: { foo: 'bar' },
        }
      }),
    }))

    vi.mock('$lib/notifications', () => ({
      countUnreadNotifications: vi.fn().mockImplementation(() => 3),
    }))

    window.localStorage.setItem('user_data', 'fake-user-data')
    window.localStorage.setItem('emailLocalStorage', 'test@email.fr')
    window.localStorage.setItem('pushSubscriptionLocalStorage', '{}')

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

  test('should logout a user from AMI then from FC', () => {
    // Given
    globalThis.localStorage = {
      getItem: vi.fn().mockImplementation(() => {
        return 'fake-id-token'
      }),
      clear: vi.fn().mockImplementation(() => {
        return
      }),
    }

    // When
    render(ConnectedHomepage)
    const franceConnectLogoutButton = screen.getByRole('button', {
      name: 'Me déconnecter',
    })
    franceConnectLogoutButton.click()

    // Then
    expect(localStorage.clear).toHaveBeenCalled()
    expect(franceConnectLogout).toHaveBeenCalledWith('fake-id-token')
  })
})
