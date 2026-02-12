import { describe, expect, test } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render } from '@testing-library/svelte'
import { toastStore } from '$lib/state/toast.svelte'
import Toasts from './Toasts.svelte'

describe('/Toasts.svelte', () => {
  test('should display toasts on top or bottom', () => {
    // Given
    toastStore.toasts = []
    toastStore.addToast('Test 1', 'success')
    toastStore.addToast('Test 2', 'neutral', 'top')
    toastStore.addToast('Test 3', 'success', 'bottom')
    toastStore.addToast('Test 4', 'neutral', 'unknown')

    // When
    const { container } = render(Toasts)

    // Then
    const banners = container.querySelector('.banners')
    const toasts = container.querySelector('.toasts')
    expect(banners).not.toHaveTextContent('Test 1')
    expect(banners).toHaveTextContent('Test 2')
    expect(banners).not.toHaveTextContent('Test 3')
    expect(banners).not.toHaveTextContent('Test 4')
    expect(toasts).toHaveTextContent('Test 1')
    expect(toasts).not.toHaveTextContent('Test 2')
    expect(toasts).toHaveTextContent('Test 3')
    expect(toasts).toHaveTextContent('Test 4')
  })
})
