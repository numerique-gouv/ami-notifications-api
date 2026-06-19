import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { getDSFRIcon } from '$lib/dsfr-icon';

describe('/dsfr-ison.ts', () => {
  test('icon is absent, should display default icon', async () => {
    // When
    const result = getDSFRIcon('', 'default-icon');

    // Then
    expect(result).toEqual('default-icon');
  });
  test('icon is empty, should display default icon', async () => {
    // When
    const result = getDSFRIcon('', 'default-icon');

    // Then
    expect(result).toEqual('default-icon');
  });
  test('icon is unknown, should display default icon', async () => {
    // When
    const result = getDSFRIcon('unknown', 'default-icon');

    // Then
    expect(result).toEqual('default-icon');
  });
  test('icon is known (dsfr), should display icon', async () => {
    // When
    const result = getDSFRIcon('fr-icon-mail-star-line', 'default-icon');

    // Then
    expect(result).toEqual('fr-icon-mail-star-line');
  });
  test('icon is known (custom), should display icon', async () => {
    // When
    const result = getDSFRIcon('fr-icon-infinity-line', 'default-icon');

    // Then
    expect(result).toEqual('fr-icon-infinity-line');
  });
});
