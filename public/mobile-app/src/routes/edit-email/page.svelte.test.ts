import { afterEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  afterEach(() => {
    vi.resetAllMocks()
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
