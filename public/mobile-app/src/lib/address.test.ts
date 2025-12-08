import { describe, test, expect } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { Address } from '$lib/address'

describe('/address.ts', () => {
  describe('Address', () => {
    describe('departement', () => {
      test('should return departement code', async () => {
        // Given
        const address1 = new Address('', '', '', '', '', '')
        const address2 = new Address('', '', '', '', '', '1')
        const address3 = new Address('', '', '', '', '', '2B')
        const address4 = new Address('', '', '', '', '', '301')

        // When
        const departement1 = address1.departement
        const departement2 = address2.departement
        const departement3 = address3.departement
        const departement4 = address4.departement

        // Then
        expect(departement1).toEqual('')
        expect(departement2).toEqual('')
        expect(departement3).toEqual('2B')
        expect(departement4).toEqual('30')
      })
    })
  })
})
