import { describe, test, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/svelte'
import Page from './+page.svelte'

describe('/+page.svelte', () => {
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
