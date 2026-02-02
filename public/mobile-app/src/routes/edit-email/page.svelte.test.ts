import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import type { MockInstance } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import { expectBackButtonPresent, mockUserIdentity, mockUserInfo } from '$tests/utils'
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
    newMockUserIdentity.dataDetails.email.origin = 'user'
    newMockUserIdentity.dataDetails.email.lastUpdate = '2026-01-15'
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
    newMockUserIdentity.dataDetails.email.origin = 'user'
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
    newMockUserIdentity.dataDetails.email.origin = choices[random_index]
    newMockUserIdentity.dataDetails.email.lastUpdate = '2026-01-15'
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
    await userStore.login(mockUserInfo)

    // When
    render(Page)

    // Then
    const container = screen.getByTestId('container')
    expect(container).not.toHaveTextContent('Vous avez modifié cette information le')
  })

  test('should allow submitting a new email', async () => {
    // Given
    await userStore.login(mockUserInfo)
    render(Page)
    const input = screen.getByTestId('email-input')

    // When
    await fireEvent.input(input, { target: { value: 'foo@bar.com' } })
    const submit = screen.getByTestId('submit-button')
    expect(submit).toBeEnabled()
    await fireEvent.click(submit)

    // Then
    await waitFor(() => {
      const updatedInput: HTMLInputElement = screen.getByTestId('email-input')
      expect(updatedInput.value).equal('foo@bar.com')
      expect(userStore.connected?.identity?.email).toEqual('foo@bar.com')
      expect(userStore.connected?.identity?.dataDetails.email.origin).toEqual('user')
      expect(
        userStore.connected?.identity?.dataDetails.email.lastUpdate
      ).not.toBeUndefined()
    })
  })

  test('should not be allowed to submit an empty email', async () => {
    // Given
    await userStore.login(mockUserInfo)
    render(Page)
    const input = screen.getByTestId('email-input') as HTMLInputElement
    expect(input.value).equal('some@email.com')

    // When
    await fireEvent.input(input, { target: { value: '' } })
    const submit = screen.getByTestId('submit-button')
    expect(submit).toBeDisabled()
    await fireEvent.click(submit)

    // Then
    await waitFor(() => {
      const updatedInput: HTMLInputElement = screen.getByTestId('email-input')
      expect(updatedInput.value).equal('')
      expect(userStore.connected?.identity?.email).toEqual('some@email.com')
      expect(userStore.connected?.identity?.dataDetails.email.origin).toEqual(
        'france-connect'
      )
      expect(
        userStore.connected?.identity?.dataDetails.email.lastUpdate
      ).toBeUndefined()
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
