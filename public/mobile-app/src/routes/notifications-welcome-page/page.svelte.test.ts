import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/')
    })
  })

  test('should navigate to the Settings when user clicks on Activer button', async () => {
    // Given
    await userStore.login(mockUserInfo)
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('enable-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/#/settings')
    })
  })

  test('should navigate to the Homepage when user clicks on Skip button', async () => {
    // Given
    await userStore.login(mockUserInfo)
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('skip-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/')
    })
  })
})
