import { describe, test, expect } from 'vitest'
import '@testing-library/jest-dom/vitest'
import AgendaItem from './AgendaItem.svelte'
import { render, screen } from '@testing-library/svelte'
import { Item } from '$lib/agenda'

describe('/AgendaItem.svelte', () => {
  test('should add date to url params', async () => {
    // Given
    const item = new Item(
      'otv',
      'Opération Tranquillité Vacances 🏠',
      'Inscrivez-vous pour protéger votre domicile pendant votre absence',
      null,
      new Date('2025-12-05'),
      null
    )
    render(AgendaItem, { props: { item: item } })

    // When
    const link = screen.getByTestId('agenda-item-link')

    // Then
    expect(link.getAttribute('href')).toBe('/#/procedure?date=2025-12-05')
  })
})
