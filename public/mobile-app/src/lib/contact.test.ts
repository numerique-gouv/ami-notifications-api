import { describe, expect, test, vi } from 'vitest';
import * as envModule from '$env/static/public';
import '@testing-library/jest-dom/vitest';
import { getContactEmail, getContactUrl } from '$lib/contact';
import * as nativeInfosMethods from '$lib/nativeInfos';

vi.mock('$env/static/public', async (importOriginal) => {
  const original = (await importOriginal()) as Record<string, unknown>;
  return Promise.resolve({
    ...original,
  });
});

describe('/contact.ts', () => {
  describe('getContactEmail', () => {
    test('simple', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_CONTACT_EMAIL = 'test@example.org';

      // When
      const email = getContactEmail();

      // Then
      expect(email).toEqual('test@example.org');
    });
  });

  describe('getContactUrl', () => {
    test('with no user', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_CONTACT_URL =
        'https://test@example.org/?h={fc_hash}&p={platform}&v={version}';

      // When
      const url = getContactUrl();

      // Then
      expect(url).toEqual('https://test@example.org/?h=%3Cabsent%3E&p=&v=');
    });

    test('with user hash', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_CONTACT_URL =
        'https://test@example.org/?h={fc_hash}&p={platform}&v={version}';

      // When
      const url = getContactUrl('fchash');

      // Then
      expect(url).toEqual('https://test@example.org/?h=fchash&p=&v=');
    });

    test('with native infos', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_CONTACT_URL =
        'https://test@example.org/?h={fc_hash}&p={platform}&v={version}';
      vi.spyOn(nativeInfosMethods, 'getPlatform').mockReturnValue('android');
      vi.spyOn(nativeInfosMethods, 'getVersion').mockReturnValue('0.5');

      // When
      const url = getContactUrl('fchash');

      // Then
      expect(url).toEqual('https://test@example.org/?h=fchash&p=android&v=0.5');
    });
  });
});
