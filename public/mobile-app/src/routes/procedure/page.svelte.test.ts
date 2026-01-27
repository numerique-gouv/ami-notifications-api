import { fireEvent, render, screen, waitFor } from '@testing-library/svelte'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import { userStore } from '$lib/state/User.svelte'
import { mockUserInfo } from '$tests/utils'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
  beforeEach(async () => {
    await userStore.login(mockUserInfo)
  })

  test('user has to be connected', async () => {
    // Given
    userStore.connected = null
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue()

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      expect(spy).toHaveBeenCalledWith('/')
    })
  })

  test('should display date from url param', async () => {
    // Given
    window.location.hash = '#/procedure?date=2025-12-05'

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(screen.getByTestId('item-date')).toHaveTextContent(
        'À partir du 5 décembre'
      )
    })
  })

  test('should display empty string if url param is empty', async () => {
    // Given
    window.location.hash = '#/procedure?date='

    // When
    render(Page)

    // Then
    expect(screen.getByTestId('item-date')).toHaveTextContent('À partir du')
  })

  test('should display empty string if url param is an invalid date', async () => {
    // Given
    window.location.hash = '#/procedure?date=coucou'

    // When
    render(Page)

    // Then
    expect(screen.getByTestId('item-date')).toHaveTextContent('À partir du')
  })

  test('should retrieve procedure url', async () => {
    // Given
    await userStore.login(mockUserInfo)

    const expectedProcedureUrl = 'fake-public-otv-url?caller=fake.jwt.token'
    const mockResponse = { partner_url: expectedProcedureUrl }
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockResponse), { status: 200 })
    )

    // When
    const { component } = render(Page)

    // Then
    await waitFor(() => {
      expect(component.getProcedureUrlForTests()).toBe(expectedProcedureUrl)
    })
  })

  test('should disable button when procedure url is empty', async () => {
    // Given
    await userStore.login(mockUserInfo)

    const procedureUrl = ''
    const mockResponse = { partner_url: procedureUrl }
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockResponse), { status: 200 })
    )

    // When
    render(Page)

    // Then
    await waitFor(() => {
      const procedureButton = screen.getByTestId('procedure-button')
      expect(procedureButton).toBeDisabled()
    })
  })

  test('should navigate to previous page when user clicks on Back button', async () => {
    // Given
    const backSpy = vi.spyOn(window.history, 'back').mockImplementation(() => {})

    // When
    render(Page)
    const backButton = screen.getByTestId('back-button')
    await fireEvent.click(backButton)

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1)
    backSpy.mockRestore()
  })
})
