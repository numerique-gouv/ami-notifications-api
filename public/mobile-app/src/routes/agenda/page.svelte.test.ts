import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/svelte'
import Page from './+page.svelte'
import * as navigationMethods from '$app/navigation'
import * as holidayMethods from '$lib/api-holidays'

describe('/+page.svelte', () => {
  test('user has to be connected', () => {
    // Given
    expect(window.localStorage.getItem('access_token')).toEqual(null)
    const spy = vi.spyOn(navigationMethods, 'goto').mockImplementation(() => 'mocked')

    // When
    render(Page)

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith('/')
  })
  test('holiday display', async () => {
    // Given
    const oneday_in_ms = 24 * 60 * 60 * 1000
    const today = new Date()
    const in15days = new Date(today.getTime() + 15 * oneday_in_ms)
    const in30days = new Date(today.getTime() + 30 * oneday_in_ms)
    const in45days = new Date(today.getTime() + 45 * oneday_in_ms)
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [
            {
              description: 'Holiday 1',
              start_date: today,
              end_date: in15days,
              zones: '',
              emoji: '',
            },
          ],
          soon: [
            {
              description: 'Holiday 2',
              start_date: in30days,
              end_date: in45days,
              zones: '',
              emoji: '',
            },
          ],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('events-now')).toHaveTextContent('En ce moment')
    expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1')
    expect(screen.getByTestId('events-soon')).toHaveTextContent('Prochainement')
    expect(screen.getByTestId('events-soon')).toHaveTextContent('Holiday 2')
  })
})
