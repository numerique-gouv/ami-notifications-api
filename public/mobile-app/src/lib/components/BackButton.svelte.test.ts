import { fireEvent, render, screen } from '@testing-library/svelte'
import { describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import Page from './BackButton.svelte'

describe('/BackButton.svelte', () => {
  test('should navigate to previous page when user clicks on Back button', async () => {
    // Given
    const backSpy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())

    // When
    render(Page, { backUrl: '/foobar' })
    const backButton = screen.getByTestId('back-button')
    await fireEvent.click(backButton)

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1)
    expect(backSpy).toHaveBeenCalledWith('/foobar')
    backSpy.mockRestore()
  })
})
