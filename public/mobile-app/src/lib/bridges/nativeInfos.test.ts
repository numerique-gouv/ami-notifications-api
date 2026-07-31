import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import {
  getDeviceId,
  getPromotedUrlAliases,
  getVersion,
  isNative,
} from '$lib/bridges/nativeInfos';

describe('/nativeEvents.ts', () => {
  afterEach(() => {
    delete globalThis.window.NativeInfos;
    vi.resetAllMocks();
  });

  describe('isNative', () => {
    test('should return true when there is a NativeInfos', async () => {
      // Given
      globalThis.window.NativeInfos = {
        getInfos: vi.fn(),
      };

      // When
      const result = isNative();

      // Then
      expect(result).toBeTruthy();
    });

    test('should return false when there is no NativeInfos', async () => {
      // Given
      expect(globalThis.window.NativeInfos).toBeUndefined();

      // When
      const result = isNative();

      // Then
      expect(result).not.toBeTruthy();
    });
  });

  describe('getDeviceId', () => {
    test('should return device id if isNative() == true', async () => {
      // Given
      window.NativeInfos = {
        getInfos: vi.fn().mockReturnValue({ device_id: 'fake-device-id' }),
      };

      // When
      const result = getDeviceId();

      // Then
      expect(result).toEqual('fake-device-id');
    });
    test('should return empty string if there is not NativeInfos', async () => {
      // Given
      expect(globalThis.window.NativeInfos).toBeUndefined();

      // When
      const result = getDeviceId();

      // Then
      expect(result).toEqual('');
    });
    test('should return empty string if device id is missing', async () => {
      // Given
      globalThis.window.NativeInfos = {
        getInfos: vi.fn(),
      };

      // When
      const result = getDeviceId();

      // Then
      expect(result).toEqual('');
    });
  });

  describe('getVersion', () => {
    test('should return version if isNative() == true', async () => {
      // Given
      window.NativeInfos = {
        getInfos: vi.fn().mockReturnValue({ version: 'fake-version' }),
      };

      // When
      const result = getVersion();

      // Then
      expect(result).toEqual('fake-version');
    });
    test('should return empty string if there is not NativeInfos', async () => {
      // Given
      expect(globalThis.window.NativeInfos).toBeUndefined();

      // When
      const result = getVersion();

      // Then
      expect(result).toEqual('');
    });
    test('should return empty string if version is missing', async () => {
      // Given
      globalThis.window.NativeInfos = {
        getInfos: vi.fn(),
      };

      // When
      const result = getVersion();

      // Then
      expect(result).toEqual('');
    });
  });

  describe('getPromotedUrlAliases', () => {
    test('should return aliases if isNative() == true', async () => {
      // Given
      window.NativeInfos = {
        getInfos: vi.fn().mockReturnValue({
          promoted_url_aliases: JSON.stringify(['alias1', 'alias2']),
        }),
      };

      // When
      const result = getPromotedUrlAliases();

      // Then
      expect(result).toEqual(['alias1', 'alias2']);
    });
    test('should return empty list if there is not NativeInfos', async () => {
      // Given
      expect(globalThis.window.NativeInfos).toBeUndefined();

      // When
      const result = getPromotedUrlAliases();

      // Then
      expect(result).toEqual([]);
    });
    test('should return empty list if promoted_url_aliases is missing', async () => {
      // Given
      globalThis.window.NativeInfos = {
        getInfos: vi.fn(),
      };

      // When
      const result = getPromotedUrlAliases();

      // Then
      expect(result).toEqual([]);
    });
    test('should return empty list if promoted_url_aliases is empty list', async () => {
      // Given
      globalThis.window.NativeInfos = {
        getInfos: vi.fn().mockReturnValue({ promoted_url_aliases: JSON.stringify([]) }),
      };

      // When
      const result = getPromotedUrlAliases();

      // Then
      expect(result).toEqual([]);
    });
  });
});
