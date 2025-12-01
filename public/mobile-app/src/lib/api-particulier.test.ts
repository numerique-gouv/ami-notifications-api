import { afterEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { getQuotientData } from '$lib/api-particulier'

describe('/api-particulier.ts', () => {
  afterEach(() => {
    window.localStorage.clear()
  })
  describe('getQuotientData', () => {
    test('should get quotient data from API', async () => {
      // Given
      window.localStorage.setItem('access_token', 'fake-access-token')
      window.localStorage.setItem('token_type', 'Bearer')
      const quotientData = {
        data: { foo: 'bar' },
      }

      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(quotientData), { status: 200 })
      )

      // When
      const result = await getQuotientData()

      // Then
      expect(result).toEqual(quotientData)
      expect(window.localStorage.getItem('quotient_data')).toEqual(
        JSON.stringify(quotientData)
      )
    })

    test('should get quotient data from API with error', async () => {
      // Given
      window.localStorage.setItem('access_token', 'fake-access-token')
      window.localStorage.setItem('token_type', 'Bearer')

      vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 400 }))

      // When
      const result = await getQuotientData()

      // Then
      expect(result).toEqual(undefined)
      expect(window.localStorage.getItem('quotient_data')).toEqual(null)
    })

    test('should get quotient data from local storage', async () => {
      // Given
      const quotientData = {
        data: { foo: 'bar' },
      }
      window.localStorage.setItem('quotient_data', JSON.stringify(quotientData))

      // When
      const result = await getQuotientData()

      // Then
      expect(result).toEqual(quotientData)
    })
  })
})
