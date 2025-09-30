import { beforeEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'

describe('/ConnectedHomepage.svelte', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  test("should display user's initials on menu", () => {
    // Given
    globalThis.Notification = {}

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
          given_name: 'Pierre',
          given_name_array: ['Pierre'],
          iat: 1758012216,
          iss: 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2',
          preferred_username: 'DUBOIS',
          sub: '328909e55774c7d7039d2c5716d2c93bf4e368f24fb42dc9e4e8009a82367157v1',
        }
      }),
      franceConnectLogout: vi.fn(),
    }))

    localStorage.setItem('user_data', 'fake-user-data')
    localStorage.setItem('emailLocalStorage', 'test@email.fr')
    localStorage.setItem('pushSubscriptionLocalStorage', '{}')

    // When
    const { container } = render(ConnectedHomepage)

    // Then
    const initials = container.querySelector('.user-profile')
    expect(initials).toHaveTextContent('P')
  })
})
