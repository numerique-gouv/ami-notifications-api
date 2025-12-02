import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { callBAN } from './addressesFromBAN.ts'

describe('addressesFromBAN.ts', () => {
  describe('callBAN', () => {
    test('should call BAN endpoint', async () => {
      // Given
      const expectedResult = [
        {
          city: 'Orléans',
          context: '45, Loiret, Centre-Val de Loire',
          id: '45234_0420_00023',
          label: '23 Rue des Aubépines 45100 Orléans',
          name: '23 Rue des Aubépines',
          postcode: '45100',
        },
        {
          city: 'Orly',
          context: '94, Val-de-Marne, Île-de-France',
          id: '94054_0070_00023',
          label: '23 Rue des Aubépines 94310 Orly',
          name: '23 Rue des Aubépines',
          postcode: '94310',
        },
        {
          city: 'Orléat',
          context: '63, Puy-de-Dôme, Auvergne-Rhône-Alpes',
          id: '63265_0008',
          label: 'Allée des Aubépines 63190 Orléat',
          name: 'Allée des Aubépines',
          postcode: '63190',
        },
      ]

      const responseFromBAN = {
        type: 'FeatureCollection',
        features: [
          {
            properties: {
              id: '45234_0420_00023',
              label: '23 Rue des Aubépines 45100 Orléans',
              name: '23 Rue des Aubépines',
              postcode: '45100',
              city: 'Orléans',
              context: '45, Loiret, Centre-Val de Loire',
            },
          },
          {
            properties: {
              id: '94054_0070_00023',
              label: '23 Rue des Aubépines 94310 Orly',
              name: '23 Rue des Aubépines',
              postcode: '94310',
              city: 'Orly',
              context: '94, Val-de-Marne, Île-de-France',
            },
          },
          {
            properties: {
              id: '63265_0008',
              label: 'Allée des Aubépines 63190 Orléat',
              name: 'Allée des Aubépines',
              postcode: '63190',
              city: 'Orléat',
              context: '63, Puy-de-Dôme, Auvergne-Rhône-Alpes',
            },
          },
        ],
        query: '23 rue des aubépines orl',
      }

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => responseFromBAN,
        })
      )

      // When
      const response = await callBAN('23 rue des aubépines orl')
      await new Promise(setTimeout) // wait for async calls

      // Then
      expect(response.statusCode).toBe(200)
      expect(response.results).toStrictEqual(expectedResult)
    })

    test('should call BAN endpoint and return error when query is not valid', async () => {
      // Given
      const responseFromBAN = {
        code: 400,
        detail: [
          'q: must contain between 3 and 200 chars and start with a number or a letter',
        ],
        message: 'Failed parsing query',
      }

      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => responseFromBAN,
        })
      )

      // When
      const response = await callBAN('23')
      await new Promise(setTimeout) // wait for async calls

      // Then
      expect(response.statusCode).toBe(400)
    })
  })
})
