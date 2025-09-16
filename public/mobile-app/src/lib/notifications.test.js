import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import ConnectedHomepage from '$lib/ConnectedHomepage.svelte'
import { askForNotificationPermission } from '$lib/notifications.js'

describe('/notifications.js', () => {
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
    // Object.defineProperty(navigator, 'serviceworker', {
    //   ready: new Promise((resolve) => {
    //     resolve(registration)
    //   }),
    // })
    // Object.defineProperty(globalThis, 'navigator', {
    //   value: {
    //     serviceWorker: {
    //       ready: new Promise((resolve) => {
    //         resolve(registration)
    //       }),
    //     }
    //   }
    // })

    const mockFetchResponse = {
      text: () => Promise.resolve('fake applicationKeyResponse'),
    }
    globalThis.fetch = vi.fn(() => Promise.resolve(mockFetchResponse))

    // When
    const pushSubscription = await askForNotificationPermission()

    // Then
    expect(pushSubscription).toHaveTextContent('todo fix result')
  })
})
