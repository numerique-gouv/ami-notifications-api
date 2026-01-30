import { render, screen, waitFor } from '@testing-library/svelte'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import * as navigationMethods from '$app/navigation'
import * as procedureMethods from '$lib/procedure'
import { userStore } from '$lib/state/User.svelte'
import { expectBackButtonPresent, mockAddress, mockUserInfo } from '$tests/utils'
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
    userStore.connected!.setPreferredUsername('Dupont')
    userStore.connected!.setAddress(mockAddress)

    const expectedProcedureUrl = 'fake-public-otv-url?caller=fake.jwt.token'
    const spy = vi
      .spyOn(procedureMethods, 'retrieveProcedureUrl')
      .mockResolvedValue(expectedProcedureUrl)

    // When
    const { component } = render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith(
        'Dupont',
        'some@email.com',
        'Paris',
        '75007',
        'Avenue de Ségur'
      )
      expect(component.getProcedureUrlForTests()).toBe(expectedProcedureUrl)
    })
  })

  test('should disable button when procedure url is empty', async () => {
    // Given
    await userStore.login(mockUserInfo)

    const procedureUrl = ''
    const spy = vi
      .spyOn(procedureMethods, 'retrieveProcedureUrl')
      .mockResolvedValue(procedureUrl)

    // When
    render(Page)

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1)
      const procedureButton = screen.getByTestId('procedure-button')
      expect(procedureButton).toBeDisabled()
    })
  })

  test('should render a Back button', async () => {
    // When
    render(Page)

    // Then
    expectBackButtonPresent(screen)
  })
})
