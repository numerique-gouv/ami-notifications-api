import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { type AddressFromBAN, callBAN } from './addressesFromBAN'

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

      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(responseFromBAN), { status: 200 })
      )

      // When
      const response = await callBAN('23 rue des aubépines orl')

      // Then
      expect(response?.statusCode).toBe(200)
      if (response?.results) {
        response.results.forEach((result: AddressFromBAN, index) => {
          expect(result.city).toEqual(expectedResult[index].city)
          expect(result.context).toEqual(expectedResult[index].context)
          expect(result.id).toEqual(expectedResult[index].id)
          expect(result.label).toEqual(expectedResult[index].label)
          expect(result.name).toEqual(expectedResult[index].name)
          expect(result.postcode).toEqual(expectedResult[index].postcode)
        })
      }
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

      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(responseFromBAN), { status: 200 })
      )

      // When
      const response = await callBAN('23')

      // Then
      expect(response.statusCode).toBe(400)
    })
  })
})
