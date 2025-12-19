import { render, screen, waitFor } from '@testing-library/svelte'
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
    expect(screen.getByTestId('item-date')).toHaveTextContent('À partir du 5 décembre')
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
})
