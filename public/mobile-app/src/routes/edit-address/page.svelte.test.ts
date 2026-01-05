import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { Address } from '$lib/address'
import * as addressesFromBANMethods from '$lib/addressesFromBAN'
import * as agendaMethods from '$lib/agenda'
import { Agenda } from '$lib/agenda'
import { userStore } from '$lib/state/User.svelte'
import { mockUserIdentity, mockUserInfo } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  beforeEach(async () => {
    await userStore.login(mockUserInfo)

    vi.mock('$lib/addressesFromBAN', () => {
      const addressesResultsFromBAN = [
        {
          city: 'Orléans',
          context: '45, Loiret, Centre-Val de Loire',
          id: '45234_0420_00023',
          label: '23 Rue des Aubépines 45100 Orléans',
          name: '23 Rue des Aubépines',
          postcode: '45100',
        },
        {
          city: 'Orly',
          context: '94, Val-de-Marne, Île-de-France',
          id: '94054_0070_00023',
          label: '23 Rue des Aubépines 94310 Orly',
          name: '23 Rue des Aubépines',
          postcode: '94310',
        },
        {
          city: 'Orléat',
          context: '63, Puy-de-Dôme, Auvergne-Rhône-Alpes',
          id: '63265_0008',
          label: 'Allée des Aubépines 63190 Orléat',
          name: 'Allée des Aubépines',
          postcode: '63190',
        },
      ]
      const response = {
        statusCode: 200,
        results: addressesResultsFromBAN,
      }
      return {
        callBAN: vi.fn(() => response),
      }
    })
    vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda([]))
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  test('should display results when user enters an address', async () => {
    // When
    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    await waitFor(() => {
      // Then
      const autocompleteListItem0 = screen.getByTestId('autocomplete-item-0')
      expect(autocompleteListItem0).toHaveTextContent(
        '23 Rue des Aubépines Orléans (45, Loiret, Centre-Val de Loire)'
      )
      const autocompleteListItem1 = screen.getByTestId('autocomplete-item-1')
      expect(autocompleteListItem1).toHaveTextContent(
        '23 Rue des Aubépines Orly (94, Val-de-Marne, Île-de-France)'
      )
      const autocompleteListItem2 = screen.getByTestId('autocomplete-item-2')
      expect(autocompleteListItem2).toHaveTextContent(
        'Allée des Aubépines Orléat (63, Puy-de-Dôme, Auvergne-Rhône-Alpes)'
      )
    })
  })

  test('should enter address label in input and display selected address in page when user selects a suggestion', async () => {
    // Given
    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    await waitFor(() => {
      const autocompleteListItem1 = screen.getByTestId('autocomplete-item-1')
      expect(autocompleteListItem1).toHaveTextContent(
        '23 Rue des Aubépines Orly (94, Val-de-Marne, Île-de-France)'
      )
    })

    // When
    const button = screen.getByTestId('autocomplete-item-button-1')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      const updatedAddressInput: HTMLInputElement = screen.getByTestId('address-input')
      expect(updatedAddressInput.value).equal('23 Rue des Aubépines 94310 Orly')

      const addressWrapper = screen.getByTestId('selected-address-wrapper')
      expect(addressWrapper).toHaveTextContent(
        'Votre résidence principale 23 Rue des Aubépines 94310 Orly'
      )
    })
  })

  test('should display selected address in page when user clicks on Save button, and remove it when clicking on the button', async () => {
    // Given
    expect(userStore.connected).not.toBeNull()
    delete userStore.connected?.identity?.address
    userStore.connected?.addScheduledNotificationCreatedKey('foo')
    const setAddressSpy = vi.spyOn(userStore.connected!, 'setAddress')
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda([]))

    // When
    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    await waitFor(() => {
      const autocompleteListItem1 = screen.getByTestId('autocomplete-item-1')
      expect(autocompleteListItem1).toHaveTextContent(
        '23 Rue des Aubépines Orly (94, Val-de-Marne, Île-de-France)'
      )
    })

    const button = screen.getByTestId('autocomplete-item-button-1')
    await fireEvent.click(button)

    // Then
    await waitFor(() => {
      const updatedAddressInput: HTMLInputElement = screen.getByTestId('address-input')
      expect(updatedAddressInput.value).equal('23 Rue des Aubépines 94310 Orly')
    })

    // When
    const submitButton = screen.getByTestId('submit-button')
    await fireEvent.click(submitButton)

    // Then
    await waitFor(() => {
      const addressWrapper = screen.getByTestId('selected-address-wrapper')
      expect(addressWrapper).toHaveTextContent(
        'Votre résidence principale 23 Rue des Aubépines 94310 Orly'
      )
      expect(setAddressSpy).toHaveBeenCalledWith(
        new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        )
      )
      const expectedAddress: Address = new Address(
        'Orly',
        '94, Val-de-Marne, Île-de-France',
        '94054_0070_00023',
        '23 Rue des Aubépines 94310 Orly',
        '23 Rue des Aubépines',
        '94310'
      )
      expect(userStore.connected?.identity?.address).toEqual(expectedAddress)
      expect(userStore.connected?.identity?.scheduledNotificationsCreatedKeys).toEqual(
        []
      )
      expect(spy).toHaveBeenCalledTimes(1)
    })

    // Given
    userStore.connected?.addScheduledNotificationCreatedKey('foo')

    // When - user clicks the remove button
    const removeButton = screen.getByRole('button', { name: /retirer l'adresse/i })
    await fireEvent.click(removeButton)

    // Then
    await waitFor(() => {
      // Address should no longer be visible
      expect(screen.queryByTestId('selected-address-wrapper')).not.toBeInTheDocument()
      // Address should be removed from userStore
      expect(userStore.connected?.identity?.address).toBeUndefined()
      expect(userStore.connected?.identity?.scheduledNotificationsCreatedKeys).toEqual(
        []
      )
      expect(spy).toHaveBeenCalledTimes(2)
    })
  })

  test('should display address in block when address is known', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
    await userStore.login(mockUserInfo) // Login again now that we updated the user identity
    expect(userStore.connected).not.toBeNull()

    // When
    render(Page)

    // Then
    await waitFor(() => {
      const addressBlock = screen.getByTestId('selected-address-wrapper')
      expect(addressBlock).toHaveTextContent('Votre résidence principale')
      expect(addressBlock).toHaveTextContent('Avenue de Ségur 75007 Paris')
    })
  })

  test('should display error message on input when input is invalid', async () => {
    // Given
    const spy = vi.spyOn(addressesFromBANMethods, 'callBAN').mockResolvedValue({
      errorCode: 'ban-failed-parsing-query',
      errorMessage: 'BAN Failed parsing query',
    })

    // When
    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      const addressError = screen.getByTestId('address-error')
      expect(addressError).toHaveTextContent(
        'Cette adresse est invalide. Conseil : saisissez entre 3 à 200 caractères et commencez par un nombre ou une lettre.'
      )
    })
  })

  test('should display warning block when BAN is unavailable', async () => {
    // Given
    const spy = vi.spyOn(addressesFromBANMethods, 'callBAN').mockResolvedValue({
      errorCode: 'ban-unavailable',
      errorMessage: 'BAN unavailable',
    })

    // When
    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      const addressWarning = screen.getByTestId('address-warning')
      expect(addressWarning).toHaveTextContent("Récupération de l'adresse indisponible")
      expect(addressWarning).toHaveTextContent(
        'Nous rencontrons des difficultés à trouver votre adresse dans notre répertoire. Merci de réessayer plus tard.'
      )
    })
  })

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page)
    const backButton = screen.getByTestId('back-button')

    // Then
    expect(backButton).toBeInTheDocument()
    expect(screen.getByText('Où habitez-vous ?')).toBeInTheDocument()
  })

  test('should navigate to previous page when user clicks on Cancel button', async () => {
    // Given
    const backSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {})

    // When
    render(Page)
    const cancelButton = screen.getByTestId('cancel-button')
    await fireEvent.click(cancelButton)

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1)
    backSpy.mockRestore()
  })
})
