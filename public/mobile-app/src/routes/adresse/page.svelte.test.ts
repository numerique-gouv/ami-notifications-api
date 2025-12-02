import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen } from '@testing-library/svelte'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.mock('./addressesFromBAN', () => {
      const addressesResultsFromBAN = [
        {
          city: 'Orléans',
          context: '45, Loiret, Centre-Val de Loire',
          idBAN: '45234_0420_00023',
          label: '23 Rue des Aubépines 45100 Orléans',
          name: '23 Rue des Aubépines',
          postcode: '45100',
        },
        {
          city: 'Orly',
          context: '94, Val-de-Marne, Île-de-France',
          idBAN: '94054_0070_00023',
          label: '23 Rue des Aubépines 94310 Orly',
          name: '23 Rue des Aubépines',
          postcode: '94310',
        },
        {
          city: 'Orléat',
          context: '63, Puy-de-Dôme, Auvergne-Rhône-Alpes',
          idBAN: '63265_0008',
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

    await new Promise((resolve) => setTimeout(resolve, 1000))
    await new Promise(setTimeout) // wait for async calls

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

  test('should enter address label in input when user selects a suggestion', async () => {
    // Given
    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    await new Promise((resolve) => setTimeout(resolve, 1000))
    await new Promise(setTimeout) // wait for async calls
    const autocompleteListItem1 = screen.getByTestId('autocomplete-item-1')
    expect(autocompleteListItem1).toHaveTextContent(
      '23 Rue des Aubépines Orly (94, Val-de-Marne, Île-de-France)'
    )

    // When
    const button = screen.getByTestId('autocomplete-item-button-1')
    await fireEvent.click(button)
    await new Promise(setTimeout) // wait for async calls

    // Then
    const updatedAddressInput = screen.getByTestId('address-input')
    expect(updatedAddressInput.value).equal('23 Rue des Aubépines 94310 Orly')
  })

  test('should display selected address in page when user clicks on Save button', async () => {
    // Given
    window.localStorage.setItem('user_address', '')

    render(Page)
    const addressInput = screen.getByTestId('address-input')
    await fireEvent.input(addressInput, {
      target: { value: '23 rue des aubépines orl' },
    })

    await new Promise((resolve) => setTimeout(resolve, 1000))
    await new Promise(setTimeout) // wait for async calls
    const autocompleteListItem1 = screen.getByTestId('autocomplete-item-1')
    expect(autocompleteListItem1).toHaveTextContent(
      '23 Rue des Aubépines Orly (94, Val-de-Marne, Île-de-France)'
    )

    const button = screen.getByTestId('autocomplete-item-button-1')
    await fireEvent.click(button)
    await new Promise(setTimeout) // wait for async calls
    const updatedAddressInput = screen.getByTestId('address-input')
    expect(updatedAddressInput.value).equal('23 Rue des Aubépines 94310 Orly')

    // When
    const submitButton = screen.getByTestId('submit-button')
    await fireEvent.click(submitButton)
    await new Promise(setTimeout) // wait for async calls

    // Then
    const adressWrapper = screen.getByTestId('selected-address-wrapper')
    expect(adressWrapper).toHaveTextContent(
      'Votre résidence principale 23 Rue des Aubépines 94310 Orly'
    )
    expect(window.localStorage.getItem('user_address')).toEqual(
      '{"city":"Orly","context":"94, Val-de-Marne, Île-de-France","label":"23 Rue des Aubépines 94310 Orly","name":"23 Rue des Aubépines","postcode":"94310"}'
    )
  })
})
