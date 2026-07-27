import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import { AMIGoto, AMIUrl } from '$lib/ami-navigation';

describe('/ami-navigation', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_API_URL: 'https://localhost:8000',
        PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED: 'true',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'true';
    vi.resetAllMocks();
  });

  describe('AMIUrl', () => {
    test('without silent-login: should return url', async () => {
      // Given
      const url1 = '/';
      const url2 = 'http://external-url';
      const url3 = '';

      // When
      const result1 = AMIUrl(url1);
      const result2 = AMIUrl(url2);
      const result3 = AMIUrl(url3);

      // Then
      expect(result1).toEqual(url1);
      expect(result2).toEqual(url2);
      expect(result3).toEqual(url3);
    });
    test('with silent-login: should return url to silent-login with url in get param', async () => {
      // Given
      const url1 = '/';
      const url2 = 'http://external-url';
      const url3 = '';

      // When
      const result1 = AMIUrl(url1, true);
      const result2 = AMIUrl(url2, true);
      const result3 = AMIUrl(url3, true);

      // Then
      expect(result1).toEqual(
        'https://localhost:8000/silent-login-ami-fi?redirect_url=%2F'
      );
      expect(result2).toEqual(
        'https://localhost:8000/silent-login-ami-fi?redirect_url=http%3A%2F%2Fexternal-url'
      );
      expect(result3).toEqual(url3);
    });
    test('with silent-login but flag disabled: should return url', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
      const url1 = '/';
      const url2 = 'http://external-url';
      const url3 = '';

      // When
      const result1 = AMIUrl(url1, true);
      const result2 = AMIUrl(url2, true);
      const result3 = AMIUrl(url3, true);

      // Then
      expect(result1).toEqual(url1);
      expect(result2).toEqual(url2);
      expect(result3).toEqual(url3);
    });
  });

  describe('AMIGoto', () => {
    describe('without silent-login', () => {
      test('should redirect to url - internal url', async () => {
        // Given
        const url = '/';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url);

        // Then
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('/', undefined);
      });
      test('should redirect to url - external url', async () => {
        // Given
        const url = 'http://external-url';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url);

        // Then
        expect(window.location.href).toBe('http://external-url');
      });
    });

    describe('with silent-login', () => {
      test('should redirect to silent login page with url in param', async () => {
        // Given
        const url = 'http://external-url';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe(
          'https://localhost:8000/silent-login-ami-fi?redirect_url=http%3A%2F%2Fexternal-url'
        );
      });
    });

    describe('with silent-login - flag disabled', () => {
      test('should redirect to url - internal url', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = '/';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url, true);

        // Then
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('/', undefined);
      });
      test('should redirect to url - external url', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = 'http://external-url';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe('http://external-url');
      });
    });
  });
});
