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
          label: '23 Rue des Aubépines 45100 Orléans',
          name: '23 Rue des Aubépines',
          postcode: '45100',
        },
        {
          city: 'Orly',
          context: '94, Val-de-Marne, Île-de-France',
          label: '23 Rue des Aubépines 94310 Orly',
          name: '23 Rue des Aubépines',
          postcode: '94310',
        },
        {
          city: 'Orléat',
          context: '63, Puy-de-Dôme, Auvergne-Rhône-Alpes',
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
              label: '23 Rue des Aubépines 45100 Orléans',
              name: '23 Rue des Aubépines',
              postcode: '45100',
              city: 'Orléans',
              context: '45, Loiret, Centre-Val de Loire',
            },
          },
          {
            properties: {
              label: '23 Rue des Aubépines 94310 Orly',
              name: '23 Rue des Aubépines',
              postcode: '94310',
              city: 'Orly',
              context: '94, Val-de-Marne, Île-de-France',
            },
          },
          {
            properties: {
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
      const result = await callBAN('23 rue des aubépines orl')

      await new Promise(setTimeout) // wait for async calls

      // Then
      expect(result).toStrictEqual(expectedResult)
    })
  })
})
