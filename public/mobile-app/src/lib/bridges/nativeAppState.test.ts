import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { isNative, isPushNotificationEnabled } from '$lib/bridges/nativeAppState';

describe('/nativeEvents.ts', () => {
  afterEach(() => {
    delete globalThis.window.NativeAppState;
  });

  describe('isNative', () => {
    test('should return true when there is a NativeAppState', async () => {
      // Given
      globalThis.window.NativeAppState = {
        isPushNotificationEnabled: vi.fn(),
      };

      // When
      const result = isNative();

      // Then
      expect(result).toBeTruthy();
    });

    test('should return false when there is no NativeAppState', async () => {
      // Given
      expect(globalThis.window.NativeAppState).toBeUndefined();

      // When
      const result = isNative();

      // Then
      expect(result).not.toBeTruthy();
    });
  });

  describe('isPushNotificationEnabled', () => {
    test('should return state if isNative() == true', async () => {
      // Given
      window.NativeAppState = {
        isPushNotificationEnabled: vi.fn().mockReturnValue(true),
      };

      // When
      const result = isPushNotificationEnabled();

      // Then
      expect(result).toEqual(true);
    });
    test('should return false if there is not NativeAppState', async () => {
      // Given
      expect(globalThis.window.NativeAppState).toBeUndefined();

      // When
      const result = isPushNotificationEnabled();

      // Then
      expect(result).toEqual(false);
    });
  });
});
