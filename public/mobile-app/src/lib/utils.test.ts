import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { formatDate } from '$lib/utils';

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
});
