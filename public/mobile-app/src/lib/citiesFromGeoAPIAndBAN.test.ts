import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Address } from '$lib/address';
import { callGeoAPI, cityToBAN } from './citiesFromGeoAPIAndBAN';

describe('citiesFromGeoAPIAndBAN.ts', () => {
  describe('callGeoAPI', () => {
    test('should call GeoAPI endpoint', async () => {
      // Given
      const data = [
        {
          nom: 'Arpajon',
          code: '91021',
          departement: { code: '91', nom: 'Essonne' },
        },
        {
          nom: 'Arpavon',
          code: '26013',
          departement: { code: '26', nom: 'Drôme' },
        },
        {
          nom: 'Saint-Germain-lès-Arpajon',
          code: '91552',
          departement: { code: '91', nom: 'Essonne' },
        },
        {
          nom: 'Arpajon-sur-Cère',
          code: '15012',
          departement: { code: '15', nom: 'Cantal' },
        },
        {
          nom: 'Arpaillargues-et-Aureillac',
          code: '30014',
          departement: { code: '30', nom: 'Gard' },
        },
      ];
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify(data), { status: 200 }));

      // When
      const response = await callGeoAPI('arpa');

      // Then
      expect(response.results).toEqual(data);
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith(
        'https://geo.api.gouv.fr/communes?nom=arpa&fields=departement&boost=population&limit=10',
        {
          headers: {
            accept: 'application/json',
          },
        }
      );
    });

    test('should call Geo API endpoint and return specific errorCode when Geo API is unavailable - 500 error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 500 })
      );

      // When
      const response = await callGeoAPI('arpa');

      // Then
      expect(response.errorCode).toBe('geo-api-unavailable');
      expect(response.errorMessage).toBe('Geo API unavailable');
    });

    test('should call Geo API endpoint and return specific errorCode when Geo API is unavailable - 400 error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 400 })
      );

      // When
      const response = await callGeoAPI('arpa');

      // Then
      expect(response.errorCode).toBe('geo-api-unavailable');
      expect(response.errorMessage).toBe('Geo API unavailable');
    });
  });

  describe('cityToBAN', () => {
    test('should call BAN endpoint', async () => {
      // Given
      const city = {
        nom: 'Arpajon',
        code: '91021',
        departement: { code: '91', nom: 'Essonne' },
      };
      const expectedResult = new Address(
        'Arpajon',
        '91, Essonne, Île-de-France',
        '91021',
        'Arpajon',
        'Arpajon',
        '91290'
      );

      const responseFromBAN = {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [2.246279, 48.590746] },
            properties: {
              id: '91021',
              label: 'Arpajon',
              name: 'Arpajon',
              postcode: '91290',
              city: 'Arpajon',
              context: '91, Essonne, Île-de-France',
            },
          },
        ],
        query: 'Arpajon',
      };
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(responseFromBAN), { status: 200 })
      );

      // When
      const response = await cityToBAN(city);

      // Then
      expect(response.address).toEqual(expectedResult);
    });

    test('should call BAN endpoint and return specific errorCode when BAN is unavailable - 500 error', async () => {
      // Given
      const city = {
        nom: 'Arpajon',
        code: '91021',
        departement: { code: '91', nom: 'Essonne' },
      };
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 500 })
      );

      // When
      const response = await cityToBAN(city);

      // Then
      expect(response.errorCode).toBe('ban-unavailable');
      expect(response.errorMessage).toBe('BAN unavailable');
    });

    test('should call BAN endpoint and return specific errorCode when BAN is unavailable - 400 error', async () => {
      // Given
      const city = {
        nom: 'Arpajon',
        code: '91021',
        departement: { code: '91', nom: 'Essonne' },
      };
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('', { status: 400 })
      );

      // When
      const response = await cityToBAN(city);

      // Then
      expect(response.errorCode).toBe('ban-unavailable');
      expect(response.errorMessage).toBe('BAN unavailable');
    });
  });
});
