import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { apiFetch, logout } from '$lib/auth'
import { userStore } from '$lib/state/User.svelte'

describe('/auth', () => {
  describe('logout', () => {
    test('should call logout endpoint from API', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify({}), { status: 200 })
      )

      // When
      const responseStatus = await logout()

      // Then
      expect(responseStatus).toEqual(true)
    })
    test('should call logout endpoint from API and return false when logout failed', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify({}), { status: 401 })
      )

      // When
      const responseStatus = await logout()

      // Then
      expect(responseStatus).toEqual(false)
    })
  })

  describe('apiFetch', () => {
    test('should call automatically logout if apiFetch received a 401 from the API', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify({}), { status: 401 })
      )
      const spyLogout = vi.spyOn(userStore, 'logout').mockResolvedValue()

      // When
      await apiFetch('some url on the API')

      // Then
      expect(spyLogout).toHaveBeenCalled()
    })
  })
})
