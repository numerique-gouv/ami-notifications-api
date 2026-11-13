import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { emit, isNative } from '$lib/bridges/nativeBridge';

describe('/nativeEvents.ts', () => {
  afterEach(() => {
    delete globalThis.window.NativeBridge;
  });

  describe('isNative', () => {
    test('should return true when there is a NativeBridge', async () => {
      // Given
      globalThis.window.NativeBridge = {
        onEvent: vi.fn(),
      };

      // When
      const result = isNative();

      // Then
      expect(result).toBeTruthy();
    });

    test('should return false when there is no NativeBridge', async () => {
      // Given
      expect(globalThis.window.NativeBridge).toBeUndefined();

      // When
      const result = isNative();

      // Then
      expect(result).not.toBeTruthy();
    });
  });

  describe('emit', () => {
    test('should emit an native event if isNative() == true', async () => {
      // Given
      const onEventSpy = vi.fn();
      globalThis.window.NativeBridge = { onEvent: onEventSpy };

      // When
      emit('some_event', 'some data');

      // Then
      expect(onEventSpy).toHaveBeenCalledWith('some_event', '"some data"');
    });
  });
});
