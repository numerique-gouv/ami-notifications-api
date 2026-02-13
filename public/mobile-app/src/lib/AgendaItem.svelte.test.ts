import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/svelte'
import * as navigationMethods from '$app/navigation'
import { Item } from '$lib/agenda'
import AgendaItem from './AgendaItem.svelte'

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
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve())
    render(AgendaItem, { props: { item: item } })

    // When
    const link = screen.getByTestId('agenda-item-link')
    link.click()

    // Then
    expect(spy).toHaveBeenCalledWith('/#/procedure?date=2025-12-05')
  })
})
