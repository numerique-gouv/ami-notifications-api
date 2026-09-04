import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import { AMIGoto } from '$lib/ami-navigation';

describe('/ami-navigation', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED: 'true',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'true';
    vi.resetAllMocks();
  });

  describe('without silent-login', () => {
    test('should redirect to url - internal url', async () => {
      // Given
      const url = '/';
      const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

      // When
      AMIGoto(url);

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
    test('should redirect to url - external url without protocol', async () => {
      // Given
      const url = '//';
      const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

      // When
      AMIGoto(url);

      // Then
      expect(spy).not.toHaveBeenCalled();
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
      expect(window.location.href).toBe('http://external-url/');
    });
    test('should redirect to url - not external url', async () => {
      // Given
      const url = 'javascript:alert("foobar")';
      vi.stubGlobal('location', {
        href: 'fake-link',
        hash: '',
        origin: 'http://localhost',
      });

      // When
      AMIGoto(url);

      // Then
      expect(window.location.href).toBe('fake-link');
    });
  });

  describe('with silent-login', () => {
    test('should redirect to silent login page with url and hash in param', async () => {
      // Given
      const url = 'http://external-url';
      vi.stubGlobal('location', {
        href: 'fake-link',
        hash: '#/page',
        origin: 'http://localhost',
      });

      // When
      AMIGoto(url, true);

      // Then
      expect(window.location.href).toBe(
        '/silent-login-ami-fi?redirect_url=http%3A%2F%2Fexternal-url&from_hash=/page'
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
      expect(spy).toHaveBeenCalledWith('/');
    });
    test('should redirect to url - internal url without protocol', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
      const url = '//';
      const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

      // When
      AMIGoto(url, true);

      // Then
      expect(spy).not.toHaveBeenCalled();
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
      expect(window.location.href).toBe('http://external-url/');
    });
    test('should redirect to url - not external url', async () => {
      // Given
      vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
      const url = 'javascript:alert("foobar")';
      vi.stubGlobal('location', {
        href: 'fake-link',
        hash: '',
        origin: 'http://localhost',
      });

      // When
      AMIGoto(url, true);

      // Then
      expect(window.location.href).toBe('fake-link');
    });
  });
});
