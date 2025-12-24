import { fireEvent, render, screen } from '@testing-library/svelte'
import { describe, expect, test, vi } from 'vitest'
import Page from './NavWithBackButton.svelte'

describe('/+NavWithBackButton.svelte', () => {
  test('should navigate to previous page when user clicks on Back button', async () => {
    // Given
    const backSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {})

    // When
    render(Page)
    const backButton = screen.getByTestId('back-button')
    await fireEvent.click(backButton)

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1)
    backSpy.mockRestore()
  })
})
