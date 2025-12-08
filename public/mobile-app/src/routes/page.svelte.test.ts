import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen, waitFor } from '@testing-library/svelte'
import Page from './+page.svelte'
import { PUBLIC_API_URL } from '$env/static/public'
import * as authMethods from '$lib/auth'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import type { UserInfo } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'

describe('/+page.svelte', () => {
  let userinfo: UserInfo
  let originalWindow: typeof globalThis.window

  beforeEach(() => {
    originalWindow = globalThis.window
    vi.spyOn(authMethods, 'checkAuth').mockResolvedValue(false)
  })

  afterEach(() => {
    globalThis.window = originalWindow
  })

  test('should render FranceConnect button', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockUserInfo), { status: 200 })
    )

    // When
    render(Page)

    // Then
    await waitFor(() => {
      const franceConnectButton = screen.getByRole('button', {
        name: 'S’identifier avec FranceConnect',
      })
      expect(franceConnectButton).toHaveTextContent('S’identifier avec FranceConnect')
    })
  })

  test('should call authorize endpoint when click on FranceConnect login button', async () => {
    // Given
    vi.stubGlobal('location', { href: 'fake-link' })

    render(Page)
    await waitFor(() => {
      const franceConnectLoginButton = screen.getByRole('button', {
        name: 'S’identifier avec FranceConnect',
      })

      // When
      franceConnectLoginButton.click()

      // Then
      expect(globalThis.window.location.href).toContain(PUBLIC_API_URL)
      expect(globalThis.window.location.href).toContain('login-france-connect')
    })
  })

  test('should display an error message if login failed', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams(
      'error=some error message&error_description=some error description'
    )
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)

    render(Page)

    // Then
    const errorMessage = await screen.findByText('some error message')
    expect(errorMessage).toBeInTheDocument()
    const errorDescription = await screen.findByText('some error description')
    expect(errorDescription).toBeInTheDocument()
  })

  test('should not display any error message if the user aborted the connection', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams(
      'error=access_denied&error_description=User auth aborted'
    )
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)

    render(Page)

    // Then
    const errorMessage = await screen.queryByText('access_denied')
    expect(errorMessage).toBeNull()
    const errorDescription = await screen.queryByText('User auth aborted')
    expect(errorDescription).toBeNull()
  })

  test('should logout the app if an error is about FranceConnect', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams(
      'error=some error message&error_type=FranceConnect'
    )
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)

    render(Page)

    // Then
    const errorMessage = await screen.findByText('some error message')
    expect(errorMessage).toBeInTheDocument()
    expect(window.localStorage.getItem('access_token')).toEqual(null)
  })
})
