import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import ConnectedHomepage from './ConnectedHomepage.svelte'
import { goto } from '$app/navigation'
import { PUBLIC_FC_BASE_URL, PUBLIC_FC_LOGOUT_ENDPOINT } from '$env/static/public'

// Mock the goto function
vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
}))

describe('/ConnectedHomepage.svelte', () => {
  test('should call logout endpoint when click on France Connect logout button', async () => {
    // Given
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
      `${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}?id_token_hint=null&state=not-implemented-yet-and-has-more-than-32-chars&post_logout_redirect_uri=https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out`
    )
  })
})
