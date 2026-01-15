import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { toastStore } from '$lib/state/toast.svelte'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue()

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/')
    })
  })

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page)
    const backButton = screen.getByTestId('back-button')

    // Then
    expect(backButton).toBeInTheDocument()
    expect(screen.getByText('Nous contacter')).toBeInTheDocument()
  })

  test('should copy identification code when user clicks on copy button', async () => {
    // Given
    window.localStorage.setItem('user_fc_hash', 'fake-user-fc-hash')

    const spy = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal('navigator', {
      ...navigator,
      clipboard: {
        writeText: spy,
      },
    })

    render(Page)

    // When
    const copyButton = screen.getByTestId('copy-button')
    await fireEvent.click(copyButton)

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith('fake-user-fc-hash')
    })
  })

  test('should add toast when user clicks on copy button', async () => {
    // Given
    window.localStorage.setItem('user_fc_hash', 'fake-user-fc-hash')
    const spy = vi.spyOn(toastStore, 'addToast')

    render(Page)

    // When
    const copyButton = screen.getByTestId('copy-button')
    await fireEvent.click(copyButton)

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith("Code d'identification copié !", 'neutral')
    })
  })
})
