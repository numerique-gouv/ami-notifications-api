import { describe, expect, test } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { Address } from '$lib/address'

describe('/address.ts', () => {
  describe('Address', () => {
    describe('fromJSON', () => {
      test('should return an Address', async () => {
        // Given
        const address = new Address('city', 'ctx', 'idban', 'label', 'name', 'postcode')

        // When
        const result = Address.fromJSON(JSON.parse(JSON.stringify(address)))

        // Then
        expect(result instanceof Address).toBe(true)
        expect(result.city).toEqual('city')
        expect(result.context).toEqual('ctx')
        expect(result.idBAN).toEqual('idban')
        expect(result.label).toEqual('label')
        expect(result.name).toEqual('name')
        expect(result.postcode).toEqual('postcode')
      })
    })

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

    describe('zone', () => {
      test('should return zone', async () => {
        // Given
        const address1 = new Address('', '', '', '', '', '')
        const address2 = new Address('', '', '', '', '', '1')
        const address3 = new Address('', '', '', '', '', '24')
        const address4 = new Address('', '', '', '', '', '301')
        const address5 = new Address('', '', '', '', '', 'ABC')

        // When
        const zone1 = address1.zone
        const zone2 = address2.zone
        const zone3 = address3.zone
        const zone4 = address4.zone
        const zone5 = address5.zone

        // Then
        expect(zone1).toEqual('')
        expect(zone2).toEqual('')
        expect(zone3).toEqual('A')
        expect(zone4).toEqual('C')
        expect(zone5).toEqual('')
      })
    })
  })
})
