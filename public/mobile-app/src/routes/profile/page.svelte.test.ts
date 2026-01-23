import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { afterEach, describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import {
  mockUser,
  mockUserIdentity,
  mockUserInfo,
  mockUserWithPreferredUsername,
} from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  afterEach(() => {
    vi.resetAllMocks()
  })

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
      expect(profileIdentity).toHaveTextContent('née le 24/08/1962')
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
      expect(profileIdentity).toHaveTextContent('né MERCIER le 17/03/1969')
      expect(screen.getByText('some-other@email.com', { exact: false }))
    })
  })

  test("profile page doesn't display user address", async () => {
    // Given
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()

    // Then
    render(Page)

    // When
    await waitFor(() => {
      const profile = screen.getByTestId('profile')
      const profileAddress = profile.querySelector('#profile-address')
      expect(profileAddress).toHaveTextContent('Définir une adresse')
    })
  })

  test('profile page displays user address - from user', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()

    // When
    render(Page)

    // Then
    await waitFor(() => {
      const profile = screen.getByTestId('profile')
      const profileAddress = profile.querySelector('#profile-address')
      expect(profileAddress).toHaveTextContent(
        'Votre résidence principale Avenue de Ségur 75007 Paris'
      )
      expect(profileAddress).not.toHaveTextContent('Informations fournies par la Caf')
    })
  })

  test('profile page displays user address - from api-particulier', async () => {
    // Given
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
    newMockUserIdentity.address_origin = 'api-particulier'
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()

    // When
    render(Page)

    // Then
    await waitFor(() => {
      const profile = screen.getByTestId('profile')
      const profileAddress = profile.querySelector('#profile-address')
      expect(profileAddress).toHaveTextContent(
        'Votre résidence principale Avenue de Ségur 75007 Paris'
      )
      expect(profileAddress).toHaveTextContent('Informations fournies par la Caf')
    })
  })

  test('should navigate to the preferred username page when user clicks on "Modifier" button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('preferred-username-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/#/edit-preferred-username')
    })
  })

  test('should navigate to the email page when user clicks on "Modifier" button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(Page)

    // When
    const button = screen.getByTestId('email-button')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenNthCalledWith(1, '/#/edit-email')
    })
  })

  test('should navigate to the Address page when user clicks on "Définir une adresse" button', async () => {
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
      expect(spy).toHaveBeenNthCalledWith(1, '/#/edit-address')
    })
  })

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page)
    const backButton = screen.getByTestId('back-button')

    // Then
    expect(backButton).toBeInTheDocument()
    expect(screen.getByText('Mon profil')).toBeInTheDocument()
  })
})
