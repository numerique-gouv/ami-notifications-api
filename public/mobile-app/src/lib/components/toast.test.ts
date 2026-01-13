import { beforeEach, describe, expect, test } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { get } from 'svelte/store'
import { addToast, removeToast, toasts } from '$lib/components/toast'

describe('/toast', () => {
  beforeEach(() => {
    toasts.set([])
  })

  describe('addToast', () => {
    test('should add toast to store', async () => {
      // When
      addToast('Test 1', 'success')

      // Then
      const result = get(toasts)
      expect(result).toHaveLength(1)
      expect(result[0].title).toBe('Test 1')
      expect(result[0].level).toBe('success')
    })
  })

  describe('removeToast', () => {
    test('should remove toast by id from store', async () => {
      // Given
      const toast1 = { id: '1', title: 'Test 1', level: 'success' }
      const toast2 = { id: '2', title: 'Test 2', level: 'neutral' }
      toasts.set([toast1, toast2])

      // When
      removeToast('1')

      // Then
      const result = get(toasts)
      expect(result).toEqual([toast2])
    })
  })
})
