import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Address } from '$lib/address';

describe('/address.ts', () => {
  describe('Address', () => {
    describe('fromJSON', () => {
      test('should return an Address', async () => {
        // Given
        const address = new Address(
          'city',
          'ctx',
          'idban',
          'label',
          'name',
          'postcode'
        );

        // When
        const result = Address.fromJSON(JSON.parse(JSON.stringify(address)));

        // Then
        expect(result instanceof Address).toBe(true);
        expect(result.city).toEqual('city');
        expect(result.context).toEqual('ctx');
        expect(result.idBAN).toEqual('idban');
        expect(result.label).toEqual('label');
        expect(result.name).toEqual('name');
        expect(result.postcode).toEqual('postcode');
      });
    });

    describe('departement', () => {
      test('should return departement code', async () => {
        // Given
        const addresses = [
          new Address('', '', '', '', '', ''),
          new Address('', '', '', '', '', '1'),
          new Address('', '', '', '', '', '2B'),
          new Address('', '', '', '', '', '301'),
          new Address('', '', '', '', '', '975'),
          new Address('', '', '', '', '', '97'),
          new Address('', '', '', '', '', '986'),
          new Address('', '', '', '', '', '98'),
        ];
        const results = ['', '', '2B', '30', '975', '', '986', ''];

        for (let i = 0; i < addresses.length; i++) {
          // When
          const departement = addresses[i].departement;

          // Then
          expect(departement).toEqual(results[i]);
        }
      });
    });

    describe('zone', () => {
      test('should return zone', async () => {
        // Given
        const addresses = [
          new Address('', '', '', '', '', ''),
          new Address('', '', '', '', '', '1'),
          new Address('', '', '', '', '', '24'),
          new Address('', '', '', '', '', '301'),
          new Address('', '', '', '', '', 'ABC'),
          new Address('', '', '', '', '', '971'),
          new Address('', '', '', '', '', '972'),
          new Address('', '', '', '', '', '973'),
          new Address('', '', '', '', '', '974'),
          new Address('', '', '', '', '', '975'),
          new Address('', '', '', '', '', '976'),
          new Address('', '', '', '', '', '977'),
          new Address('', '', '', '', '', '978'),
          new Address('', '', '', '', '', '97'),
          new Address('', '', '', '', '', '986'),
          new Address('', '', '', '', '', '987'),
          new Address('', '', '', '', '', '988'),
          new Address('', '', '', '', '', '98'),
          new Address('', '', '', '', '', '20'),
        ];
        const results = [
          '',
          '',
          'Zone A',
          'Zone C',
          '',
          'Guadeloupe',
          'Martinique',
          'Guyane',
          'Réunion',
          'Saint Pierre et Miquelon',
          'Mayotte',
          'Guadeloupe',
          'Guadeloupe',
          '',
          'Wallis et Futuna',
          'Polynésie',
          'Nouvelle Calédonie',
          '',
          'Corse',
        ];

        for (let i = 0; i < addresses.length; i++) {
          // When
          const zone = addresses[i].zone;

          // Then
          expect(zone).toEqual(results[i]);
        }
      });
    });
  });
});
