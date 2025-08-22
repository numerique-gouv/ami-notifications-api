import { describe, test, expect } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  test('should render France Connect button', () => {
    // When
    render(Page)

    // Then
    const franceConnectButton = screen.getByRole('button', {
      name: 'S’identifier avec FranceConnect',
    })
    expect(franceConnectButton).toHaveTextContent('S’identifier avec FranceConnect')
  })

  test('should call authorize endpoint when click on France Connect button', async () => {
    // Given
    globalThis.Response = {
      redirect: () => true,
    }
    globalThis.window = {
      location: {
        href: 'fake-link',
      },
    }

    render(Page)
    const franceConnectButton = screen.getByRole('button', {
      name: 'S’identifier avec FranceConnect',
    })

    // When
    await franceConnectButton.click()

    // Then
    expect(globalThis.window.location.href).equal(
      'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize?scope=openid+given_name+family_name+preferred_username+birthdate+gender+birthplace+birthcountry+sub+email+given_name_array&redirect_uri=https%3A%2F%2Flocalhost%3A5173%2Fami-fs-test-login-callback&response_type=code&client_id=88d6fc32244b89e2617388fb111e668fec7b7383c841a08eefbd58fd11637eec&state=not-implemented-yet-and-has-more-than-32-chars&nonce=not-implemented-yet-and-has-more-than-32-chars&acr_values=eidas1&prompt=login'
    )
  })
})
