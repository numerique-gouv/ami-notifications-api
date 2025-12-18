import { render, screen, waitFor } from '@testing-library/svelte'
import { describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import { mockUser, mockUserWithPreferredUsername } from '$tests/utils'
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
      const profile = screen.getByTestId('profile')
      const profileIdentity = profile.querySelector('#profile-identity')
      expect(profileIdentity).toHaveTextContent('Angela Claire Louise DUBOIS,')
      expect(profileIdentity).toHaveTextContent('née le 1962-08-24')
      expect(screen.getByText('some@email.com', { exact: false }))
    })
  })

  test('profile page displays the proper user info - with preferred username', async () => {
    // Given
    const spy = vi
      .spyOn(userStore, 'connected', 'get')
      .mockReturnValue(mockUserWithPreferredUsername)

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalled()
      const profile = screen.getByTestId('profile')
      const profileIdentity = profile.querySelector('#profile-identity')
      expect(profileIdentity).toHaveTextContent('Pierre DUBOIS,')
      expect(profileIdentity).toHaveTextContent('né MERCIER le 1969-03-17')
      expect(screen.getByText('some-other@email.com', { exact: false }))
    })
  })
})
