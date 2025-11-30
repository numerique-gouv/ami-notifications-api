import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { logout } from '$lib/auth'

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
})
