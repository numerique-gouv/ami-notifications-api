import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import { mockUser } from '$tests/utils'
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

  test('profile page displays the proper user info', async () => {
    // Given
    const spy = vi.spyOn(userStore, 'connected', 'get').mockReturnValue(mockUser)

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalled()
      expect(screen.getByText('Angela Claire Louise DUBOIS', { exact: false }))
      expect(screen.getByText('some@email.com', { exact: false }))
    })
  })

  test('should navigate to Address page when user clicks on "Définir une adresse" button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('address-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/#/address')
    })
  })
})
