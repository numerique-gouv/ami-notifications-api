import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { dateToISO, formatDate } from '$lib/utils';

describe('/lib/utils.ts', () => {
  describe('formatDate', () => {
    test('should format date str to DD/MM/YYYY format', async () => {
      // Given
      const date = '1962-08-24';

      // When
      const formattedDate = formatDate(date);

      // Then
      expect(formattedDate).toEqual('24/08/1962');
    });
    test('should format date object to DD/MM/YYYY format', async () => {
      // Given
      const date = new Date(1962, 7, 24);

      // When
      const formattedDate = formatDate(date);

      // Then
      expect(formattedDate).toEqual('24/08/1962');
    });
  });

  describe('dateToISO', () => {
    test('should format date object to YYYY-MM-DD format', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const date1 = new Date(1962, 7, 24);
      const date2 = new Date('1962-08-23T23:07:40.162Z');

      // When
      const result1 = dateToISO(date1);
      const result2 = dateToISO(date2);

      // Then
      expect(result1).toEqual('1962-08-24');
      expect(result2).toEqual('1962-08-24');
    });
    test('should format null to empty string', async () => {
      // When
      const result = dateToISO(null);

      // Then
      expect(result).toEqual('');
    });
  });
});
