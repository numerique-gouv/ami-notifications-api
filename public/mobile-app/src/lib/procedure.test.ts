import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { waitFor } from '@testing-library/svelte'
import { retrieveProcedureUrl } from '$lib/procedure'

describe('/procedure.ts', () => {
  describe('retrieveProcedureUrl', () => {
    test('should retrieve procedure url', async () => {
      // Given
      const expectedProcedureUrl = 'fake-public-otv-url?caller=fake.jwt.token'
      const mockResponse = { partner_url: expectedProcedureUrl }
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(mockResponse), { status: 200 })
      )

      // When
      const response = await retrieveProcedureUrl(
        'Dupont',
        'some@email.com',
        'Paris',
        '75007',
        'Avenue de Ségur'
      )

      // Then
      await waitFor(() => {
        expect(response).toEqual(expectedProcedureUrl)
      })
    })

    test('should return empty string when response status is not 200', async () => {
      // Given
      const mockResponse = {}
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(mockResponse), { status: 400 })
      )

      // When
      const response = await retrieveProcedureUrl(
        'Dupont',
        'some@email.com',
        'Paris',
        '75007',
        'Avenue de Ségur'
      )

      // Then
      await waitFor(() => {
        expect(response).toEqual('')
      })
    })

    test('should return empty string when apiFetch has an error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Fetch failed'))

      // When
      const response = await retrieveProcedureUrl(
        'Dupont',
        'some@email.com',
        'Paris',
        '75007',
        'Avenue de Ségur'
      )

      // Then
      await waitFor(() => {
        expect(response).toEqual('')
      })
    })
  })
})
