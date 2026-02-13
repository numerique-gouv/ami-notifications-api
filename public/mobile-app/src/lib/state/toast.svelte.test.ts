import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { toastStore } from '$lib/state/toast.svelte.js';

describe('/lib/state/toast.svelte.ts', () => {
  describe('addToast', () => {
    test('should add toast to state', async () => {
      // Given
      toastStore.toasts = [];

      // When
      toastStore.addToast('Test 1', 'success');

      // Then
      expect(toastStore.toasts).toHaveLength(1);
      expect(toastStore.toasts[0].title).toBe('Test 1');
      expect(toastStore.toasts[0].level).toBe('success');
    });
  });

  describe('removeToast', () => {
    test('should remove toast by id from state', async () => {
      // Given
      const toast1 = { id: '1', title: 'Test 1', level: 'success' };
      const toast2 = { id: '2', title: 'Test 2', level: 'neutral' };
      toastStore.toasts = [toast1, toast2];

      // When
      toastStore.removeToast('1');

      // Then
      expect(toastStore.toasts).toEqual([toast2]);
    });
  });
});
