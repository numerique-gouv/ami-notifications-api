import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { toastStore } from '$lib/state/toast.svelte'
import Toast from './Toast.svelte'

describe('/Toast.svelte', () => {
  test('should remove toast from store when user clicks on close button', async () => {
    // Given
    const spy = vi.spyOn(toastStore, 'removeToast')
    render(Toast, { id: 'id1', title: 'Title 1', level: 'neutral' })

    // When
    const closeButton = screen.getByTestId('close-button')
    await fireEvent.click(closeButton)

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('id1')
    })
  })
})
