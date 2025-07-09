import { describe, test, expect, vi, beforeEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen, waitFor } from '@testing-library/svelte'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  beforeEach(() => {
    // TODO check how to reset mocks
    globalThis.Notification = {}
  })

  test('should render h1 without user email when email and pushSubscription are not set', () => {
    // When
    render(Page)

    // Then
    const title = screen.getByRole('heading', { level: 1 })
    expect(title).toHaveTextContent("Bienvenue sur l'application AMI")
  })

  test('should render h1 with user email when email and pushSubscription are set', () => {
    // Given
    window.localStorage.setItem('userIdLocalStorage', '11')
    window.localStorage.setItem('emailLocalStorage', 'test@email.fr')
    window.localStorage.setItem('pushSubscriptionLocalStorage', '{}')

    // When
    render(Page)

    // Then
    const title = screen.getByRole('heading', { level: 1 })
    expect(title).toHaveTextContent("Bienvenue test@email.fr sur l'application AMI")
  })

  test('should display authentication status message when user clicks on authentication button and authentication works', async () => {
    // Given
    globalThis.Notification = {
      requestPermission: () => true,
      permission: 'granted',
    }
    const registration = {
      pushManager: {
        subscribe: vi.fn(() => Promise.resolve('fake pushSubscription')),
      },
    }
    globalThis.navigator = {
      serviceWorker: {
        ready: new Promise((resolve) => {
          resolve(registration)
        }),
      },
    }

    const mockFetchResponse = {
      text: () => Promise.resolve('fake applicationKeyResponse'),
    }
    globalThis.fetch = vi.fn(() => Promise.resolve(mockFetchResponse))

    render(Page)
    const authenticationButton = screen.getByRole('button', {
      name: "S'authentifier pour recevoir des notifications",
    })

    // When
    await authenticationButton.click()

    // Then
    await waitFor(() => {
      const element = screen.getByTitle('authentication-status-title', {})

      expect(element).toBeInTheDocument()
      expect(element).toHaveTextContent(
        'Inscription réussie au serveur de notifications'
      )
    })
  })
})
