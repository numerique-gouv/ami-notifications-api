import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'

describe('/ConnectedHomepage.svelte', () => {
  test('should call logout endpoint when click on France Connect logout button', async () => {
    const userinfo = {
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
    globalThis.fetch = vi.fn(() =>
      Promise.resolve({
        status: 200,
        json: () => Promise.resolve(userinfo),
      })
    )

    const fakeProps = {
      userinfo: userinfo,
      isLoggedOut: false,
      isFranceConnected: true,
    }
    render(ConnectedHomepage, fakeProps)
    const franceConnectLogoutButton = await screen.getByRole('button', {
      name: 'Se déconnecter de FranceConnect',
    })

    // When
    await franceConnectLogoutButton.click()

    // Then
    expect(fetch).toHaveBeenCalledTimes(1)
    expect(fetch).toHaveBeenCalledWith('https://localhost:5173/ami-fs-test-logout')
  })
})
