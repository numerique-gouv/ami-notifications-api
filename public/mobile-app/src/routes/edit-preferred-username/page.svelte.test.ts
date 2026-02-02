import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import type { MockInstance } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import {
  expectBackButtonPresent,
  mockUserIdentity,
  mockUserInfo,
  mockUserInfoWithPreferredUsername,
} from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  let backSpy: MockInstance<typeof navigationMethods.goto>

  beforeEach(() => {
    backSpy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
  })
  afterEach(() => {
    vi.resetAllMocks()
  })

  test('should display the last update date', async () => {
    // Given
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
    newMockUserIdentity.dataDetails.preferred_username.origin = 'user'
    newMockUserIdentity.dataDetails.preferred_username.lastUpdate = '2026-01-15'
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
    await userStore.login(mockUserInfo)

    // When
    render(Page)

    // Then
    const container = screen.getByTestId('container')
    expect(container).toHaveTextContent(
      'Vous avez modifié cette information le 15/01/2026.'
    )
  })

  test('should not display the last update date - date missing', async () => {
    // Given
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
    newMockUserIdentity.dataDetails.preferred_username.origin = 'user'
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
    await userStore.login(mockUserInfo)

    // When
    render(Page)

    // Then
    const container = screen.getByTestId('container')
    expect(container).not.toHaveTextContent('Vous avez modifié cette information le')
  })

  test('should not display the last update date - wrong origin', async () => {
    // Given
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
    const choices = ['france-connect', 'api-particulier', 'cleared', undefined]
    const random_index = Math.floor(Math.random() * choices.length)
    newMockUserIdentity.dataDetails.preferred_username.origin = choices[random_index]
    newMockUserIdentity.dataDetails.preferred_username.lastUpdate = '2026-01-15'
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
    await userStore.login(mockUserInfo)

    // When
    render(Page)

    // Then
    const container = screen.getByTestId('container')
    expect(container).not.toHaveTextContent('Vous avez modifié cette information le')
  })

  test('should allow submitting a new preferred username', async () => {
    // Given
    await userStore.login(mockUserInfo)
    render(Page)
    const input = screen.getByTestId('preferred-username-input')

    // When
    await fireEvent.input(input, { target: { value: 'Dupont' } })
    const submit = screen.getByTestId('submit-button')
    expect(submit).toBeEnabled()
    await fireEvent.click(submit)

    // Then
    await waitFor(() => {
      const updatedInput: HTMLInputElement = screen.getByTestId(
        'preferred-username-input'
      )
      expect(updatedInput.value).equal('Dupont')
      expect(userStore.connected?.identity?.preferred_username).toEqual('Dupont')
      expect(
        userStore.connected?.identity?.dataDetails.preferred_username.origin
      ).toEqual('user')
      expect(
        userStore.connected?.identity?.dataDetails.preferred_username.lastUpdate
      ).not.toBeUndefined()
    })
  })

  test('should allow submitting an empty preferred username', async () => {
    // Given
    await userStore.login(mockUserInfoWithPreferredUsername)
    render(Page)
    const input = screen.getByTestId('preferred-username-input') as HTMLInputElement
    expect(input.value).equal('DUBOIS')

    // When
    await fireEvent.input(input, { target: { value: '' } })
    const submit = screen.getByTestId('submit-button')
    expect(submit).toBeEnabled()
    await fireEvent.click(submit)

    // Then
    await waitFor(() => {
      const updatedInput: HTMLInputElement = screen.getByTestId(
        'preferred-username-input'
      )
      expect(updatedInput.value).equal('')
      expect(userStore.connected?.identity?.preferred_username).toBeUndefined()
      expect(
        userStore.connected?.identity?.dataDetails.preferred_username.origin
      ).toEqual('cleared')
      expect(
        userStore.connected?.identity?.dataDetails.preferred_username.lastUpdate
      ).not.toBeUndefined()
    })
  })

  test('should navigate to previous page when user clicks on Cancel button', async () => {
    // When
    render(Page)
    const cancelButton = screen.getByTestId('cancel-button')
    await fireEvent.click(cancelButton)

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1)
  })

  test('should render a Back button', async () => {
    // When
    render(Page)

    // Then
    expectBackButtonPresent(screen)
  })
})
