import { beforeEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'
import { PUBLIC_FC_BASE_URL, PUBLIC_FC_LOGOUT_ENDPOINT } from '$env/static/public'

describe('/ConnectedHomepage.svelte', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  test('should call logout endpoint when click on France Connect logout button', async () => {
    // Given
    localStorage.setItem('id_token', 'fake-id-token')
    globalThis.window = {
      location: {
        href: 'fake-link',
      },
    }
    render(ConnectedHomepage)
    const franceConnectLogoutButton = await screen.getByRole('button', {
      name: 'Me déconnecter',
    })

    // When
    await franceConnectLogoutButton.click()

    // Then
    expect(globalThis.window.location).equal(
      `${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}?id_token_hint=fake-id-token&state=not-implemented-yet-and-has-more-than-32-chars&post_logout_redirect_uri=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out`
    )
  })
})
