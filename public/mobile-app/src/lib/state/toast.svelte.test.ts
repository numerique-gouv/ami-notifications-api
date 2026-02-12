import { describe, expect, test } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { toastStore } from '$lib/state/toast.svelte.js'

describe('/lib/state/toast.svelte.ts', () => {
  describe('addToast', () => {
    test('should add toast to state', async () => {
      // Given
      toastStore.toasts = []

      // When
      toastStore.addToast('Test 1', 'success')
      toastStore.addToast('Test 2', 'neutral', true)
      toastStore.addToast('Test 3', 'neutral', false)

      // Then
      expect(toastStore.toasts).toHaveLength(3)
      expect(toastStore.toasts[0].title).toBe('Test 1')
      expect(toastStore.toasts[0].level).toBe('success')
      expect(toastStore.toasts[0].top).toBe(false)
      expect(toastStore.toasts[1].title).toBe('Test 2')
      expect(toastStore.toasts[1].level).toBe('neutral')
      expect(toastStore.toasts[1].top).toBe(true)
      expect(toastStore.toasts[2].title).toBe('Test 3')
      expect(toastStore.toasts[2].level).toBe('neutral')
      expect(toastStore.toasts[2].top).toBe(false)
    })
  })

  describe('removeToast', () => {
    test('should remove toast by id from state', async () => {
      // Given
      const toast1 = { id: '1', title: 'Test 1', level: 'success', top: true }
      const toast2 = { id: '2', title: 'Test 2', level: 'neutral', top: false }
      toastStore.toasts = [toast1, toast2]

      // When
      toastStore.removeToast('1')

      // Then
      expect(toastStore.toasts).toEqual([toast2])
    })
  })
})
