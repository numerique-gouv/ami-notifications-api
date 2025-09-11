import { describe, test, expect, vi, beforeEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import Page from './+page.svelte'
import {
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_AUTHORIZATION_ENDPOINT,
} from '$env/static/public'

describe('/+page.svelte', () => {
  let userinfo

  beforeEach(() => {
    userinfo = {
      sub: 'fake sub',
      given_name: 'Angela Claire Louise',
      given_name_array: ['Angela', 'Claire', 'Louise'],
      family_name: 'DUBOIS',
      birthdate: '1962-08-24',
      gender: 'female',
      aud: 'fake aud',
      exp: 1753877658,
      iat: 1753877598,
      iss: 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2',
    }
  })

  test('should render France Connect button', () => {
    // Given
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        status: 200,
        json: () => Promise.resolve(userinfo),
      })
    )

    // When
    render(Page)

    // Then
    const franceConnectButton = screen.getByRole('button', {
      name: 'S’identifier avec FranceConnect',
    })
    expect(franceConnectButton).toHaveTextContent('S’identifier avec FranceConnect')
  })

  test('should call authorize endpoint when click on France Connect login button', async () => {
    // Given
    globalThis.window = {
      location: {
        href: 'fake-link',
      },
    }

    render(Page)
    const franceConnectLoginButton = screen.getByRole('button', {
      name: 'S’identifier avec FranceConnect',
    })

    // When
    await franceConnectLoginButton.click()

    // Then
    expect(globalThis.window.location.href).toContain(PUBLIC_FC_BASE_URL)
    expect(globalThis.window.location.href).toContain(PUBLIC_FC_AUTHORIZATION_ENDPOINT)
  })
})
