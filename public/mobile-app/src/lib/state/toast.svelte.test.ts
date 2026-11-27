import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Toast, toastStore } from '$lib/state/toast.svelte.js';

describe('/lib/state/toast.svelte.ts', () => {
  describe('addToast', () => {
    test('should add toast to state', async () => {
      // Given
      toastStore.toasts = [];

      // When
      toastStore.addToast('Code d’identification copié !', 'info', 5000, true);
      toastStore.addToast('Information bien enregistrée !', 'success', 5000, false);
      toastStore.addToast('Les notifications ont été activées', 'success', null, false);

      // Then
      expect(toastStore.toasts).toHaveLength(3);
      expect(toastStore.toasts[0].title).toBe('Code d’identification copié !');
      expect(toastStore.toasts[0].toastType).toBe('info');
      expect(toastStore.toasts[0].duration).toBe(5000);
      expect(toastStore.toasts[0].hasCloseLink).toBe(true);
      expect(toastStore.toasts[1].title).toBe('Information bien enregistrée !');
      expect(toastStore.toasts[1].toastType).toBe('success');
      expect(toastStore.toasts[1].duration).toBe(5000);
      expect(toastStore.toasts[1].hasCloseLink).toBe(false);
      expect(toastStore.toasts[2].title).toBe('Les notifications ont été activées');
      expect(toastStore.toasts[2].toastType).toBe('success');
      expect(toastStore.toasts[2].duration).toBe(null);
      expect(toastStore.toasts[2].hasCloseLink).toBe(false);
    });

    test('should add toasts titles to vocal messages', async () => {
      // Given
      toastStore.toasts = [];
      toastStore.vocalMessages = [];

      // When
      toastStore.addToast('Code d’identification copié !', 'info', 5000, true);
      toastStore.addToast('Information bien enregistrée !', 'success', 5000, false);
      toastStore.addToast('Les notifications ont été activées', 'success', null, false);

      // Then
      expect(toastStore.vocalMessages).toHaveLength(3);
      expect(toastStore.vocalMessages[0]).toBe('Code d’identification copié !');
      expect(toastStore.vocalMessages[1]).toBe('Information bien enregistrée !');
      expect(toastStore.vocalMessages[2]).toBe('Les notifications ont été activées');
    });

    test('should focus vocal messages container after 50ms', async () => {
      // Given
      vi.useFakeTimers({ shouldAdvanceTime: true });
      const focusMock = vi.fn();
      const toastsContainerA11yMock = { focus: focusMock };
      const getElementById = vi.fn(() => toastsContainerA11yMock);
      vi.stubGlobal('document', { getElementById });
      toastStore.toasts = [];

      // When
      toastStore.addToast('Code d’identification copié !', 'info', 5000, true);
      vi.advanceTimersByTime(50);

      // Then
      expect(focusMock).toHaveBeenCalled();

      // After
      vi.useRealTimers();
      vi.unstubAllGlobals();
    });
  });

  describe('removeToast', () => {
    test('should remove toast by id from state', async () => {
      // Given
      const toast1 = new Toast(
        '1',
        'Code d’identification copié !',
        'info',
        5000,
        true
      );
      const toast2 = new Toast(
        '2',
        'Information bien enregistrée !',
        'success',
        5000,
        false
      );
      toastStore.toasts = [toast1, toast2];

      // When
      toastStore.removeToast('1');

      // Then
      expect(toastStore.toasts).toEqual([toast2]);
    });
  });
});
