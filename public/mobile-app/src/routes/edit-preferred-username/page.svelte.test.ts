import { afterEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo, mockUserInfoWithPreferredUsername } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  afterEach(() => {
    vi.resetAllMocks()
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
