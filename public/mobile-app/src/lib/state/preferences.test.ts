import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Address } from '$lib/address';
import { Preferences } from '$lib/state/preferences';

describe('/preferences.ts', () => {
  describe('Preferences', () => {
    describe('fromJSON', () => {
      test('should init fields if empty', async () => {
        // Given
        const preferences_data = {};

        // When
        const preferences = Preferences.fromJSON(preferences_data);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual([]);
        expect(preferences.addresses).toEqual([]);
      });
      test('should init with values - empty values', async () => {
        // Given
        const preferences_data = { _zones: [], _addresses: [] };

        // When
        const preferences = Preferences.fromJSON(preferences_data);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual([]);
        expect(preferences.addresses).toEqual([]);
      });
      test('should init with values - not empty values', async () => {
        // Given
        const address1 = new Address('some random city');
        const address2 = new Address('some other random city');
        const preferences_data = {
          _zones: ['Zone A', 'Martinique'],
          _addresses: [address1, address2],
        };

        // When
        const preferences = Preferences.fromJSON(preferences_data);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Martinique']);
        expect(preferences.addresses).toEqual([address1, address2]);
      });
    });

    describe('getDefault', () => {
      test('no address: should init zones with A, B, C and Corse', async () => {
        // When
        const preferences = Preferences.getDefault(undefined);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Corse']);
        expect(preferences.addresses).toEqual([]);
      });
      test('with address in hexagone: should init zones with A, B, C and Corse', async () => {
        // Given
        const address = new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        );

        // When
        const preferences = Preferences.getDefault(address);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Corse']);
        expect(preferences.addresses).toEqual([]);
      });
      test('with address in Corse: should init zones with A, B, C and Corse', async () => {
        // Given
        const address = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );

        // When
        const preferences = Preferences.getDefault(address);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Corse']);
        expect(preferences.addresses).toEqual([]);
      });
      test('with address out of hexagone and Corse: should init zones with the corresponding zone', async () => {
        // Given
        const address = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00002',
          '2 Rue de Paris 97400 Saint-Denis',
          '2 Rue de Paris',
          '97400'
        );

        // When
        const preferences = Preferences.getDefault(address);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Réunion']);
        expect(preferences.addresses).toEqual([]);
      });
    });
  });
});
