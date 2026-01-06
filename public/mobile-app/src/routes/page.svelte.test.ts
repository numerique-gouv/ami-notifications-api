import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import * as navigationMethods from '$app/navigation'
import { PUBLIC_API_URL } from '$env/static/public'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  let originalWindow: typeof globalThis.window

  beforeEach(() => {
    originalWindow = globalThis.window
  })

  afterEach(() => {
    globalThis.window = originalWindow
    vi.resetAllMocks()
  })

  test('should set localStorage when user is logged in', async () => {
    // Given
    window.localStorage.setItem('user_data', '')
    window.localStorage.setItem('user_id', '')
    window.localStorage.setItem('user_fc_hash', '')

    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams('is_logged_in=true')
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)
    const mockResponse = {
      user_id: 'fake-user-id',
      user_data: 'fake-user-data',
      user_first_login: true,
      user_fc_hash: 'fake-user-fc-hash',
    }
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockResponse), { status: 200 })
    )

    // When
    render(Page)

    // Then
    await waitFor(async () => {
      expect(window.localStorage.getItem('user_data')).toEqual('fake-user-data')
      expect(window.localStorage.getItem('user_id')).toEqual('fake-user-id')
      expect(window.localStorage.getItem('user_fc_hash')).toEqual('fake-user-fc-hash')
    })
  })

  test('should navigate to notifications welcome page when it is the first user login', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams('is_logged_in=true')
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)
    const mockResponse = {
      user_id: 'fake-user-id',
      user_data: 'fake-user-data',
      user_first_login: true,
      user_fc_hash: 'fake-user-fc-hash',
    }
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockResponse), { status: 200 })
    )
    vi.spyOn(userStore, 'checkLoggedIn').mockResolvedValue()
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/notifications-welcome-page')
    })
  })

  test('should navigate to homepage when user has already logged in', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams('is_logged_in=true')
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)
    const mockResponse = {
      user_id: 'fake-user-id',
      user_data: 'fake-user-data',
      user_first_login: false,
      user_fc_hash: 'fake-user-fc-hash',
    }
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockResponse), { status: 200 })
    )
    vi.spyOn(userStore, 'checkLoggedIn').mockResolvedValue()
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/')
    })
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

  test('should display notifications notice when user has enabled them', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams('has_enabled_notifications')
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)
    userStore.login(mockUserInfo)

    // When
    render(Page)

    // Then
    const notificationsNotice = await screen.findByText(
      'Les notifications ont été activées'
    )
    expect(notificationsNotice).toBeInTheDocument()
  })

  test('should remove notifications notice when user clicks on close button', async () => {
    // Given
    const { page } = await import('$app/state')
    const mockSearchParams = new URLSearchParams('has_enabled_notifications')
    vi.spyOn(page.url, 'searchParams', 'get').mockReturnValue(mockSearchParams)
    userStore.login(mockUserInfo)
    render(Page)

    // When
    const closeButton = screen.getByTestId('close-button')
    await fireEvent.click(closeButton)

    // Then
    expect(screen).not.toContain('Les notifications ont été activées')
  })
})
