import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as UrlAliasesMethods from '$lib/urlAliases';

describe('/webappBridge.ts', () => {
  describe('getUrlAliases', () => {
    test('should return url aliases', async () => {
      // Given
      const aliases = [
        { pattern: '/#/resources', alias: 'resource:list' },
        { pattern: '/#/resources/:id', alias: 'resource:detail' },
      ];
      vi.spyOn(UrlAliasesMethods, 'getUrlAliases').mockReturnValue(aliases);
      await import('$lib/bridges/webappBridge');

      // When
      const result = window.WebAppBridge.getUrlAliases();

      // Then
      expect(result).toBe(JSON.stringify(aliases));
    });
  });
  describe('getAuthenticationUrls', () => {
    test('should return the list of authentication urls', async () => {
      // When
      const result = window.WebAppBridge.getAuthenticationUrls();

      // Then
      expect(result).toEqual([
        'https://localhost:5173/login-france-connect',
        'https://localhost:5173/relogin-france-connect',
        'https://localhost:5173/silent-login-ami-fi',
        'https://localhost:5173/login-callback',
        'https://localhost:5173/goto-redirect-url',
        'https://localhost:5173/api/v1/fi/authorize/',
        'https://localhost:5173/#/relogin',
        'https://localhost:5173/#/silent-login',
        'https://localhost:5173/#/login-callback',
        'https://localhost:5173/#/passkey-authentication',
      ]);
    });
  });
});
