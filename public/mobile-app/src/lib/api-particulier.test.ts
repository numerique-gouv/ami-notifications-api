import { afterEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { getQuotientData } from '$lib/api-particulier.ts'

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

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          ok: true,
          text: () => JSON.stringify(quotientData),
        })
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

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 400,
          ok: false,
          text: () => '',
        })
      )

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
