import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/svelte'
import Page from './+page.svelte'
import * as navigationMethods from '$app/navigation'
import * as holidayMethods from '$lib/api-holidays'
import { monthName } from '$lib/api-holidays'

const oneday_in_ms = 24 * 60 * 60 * 1000
const today = new Date()
const in15days = new Date(today.getTime() + 15 * oneday_in_ms)
const in32days = new Date(today.getTime() + 32 * oneday_in_ms) // 32 days, so we are sure that month is different than today's
const in45days = new Date(today.getTime() + 45 * oneday_in_ms)
const in60days = new Date(today.getTime() + 60 * oneday_in_ms)

describe('/+page.svelte', () => {
  test('user has to be connected', () => {
    // Given
    expect(window.localStorage.getItem('access_token')).toEqual(null)
    vi.spyOn(holidayMethods, 'retrieveHolidays').mockImplementation(async () => {
      return { now: [], next: [] }
    })
    const spy = vi.spyOn(navigationMethods, 'goto').mockImplementation(() => 'mocked')

    // When
    render(Page)

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith('/')
  })
  test('Should display holidays from API', async () => {
    // Given
    window.localStorage.setItem('access_token', 'fake-access-token')
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [
            {
              description: 'Holiday 1',
              start_date: today,
              end_date: in15days,
            },
          ],
          next: [
            {
              description: 'Holiday 2',
              start_date: in32days,
              end_date: in45days,
            },
          ],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('events-now')).toHaveTextContent("D'ici un mois")
    expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(today))
    expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1')
    expect(screen.getByTestId('events-next')).toHaveTextContent('Prochainement')
    expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days))
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2')
  })
  test('Should not display "next" section if empty', async () => {
    // Given
    window.localStorage.setItem('access_token', 'fake-access-token')
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [],
          next: [
            {
              description: 'Holiday 2',
              start_date: in32days,
              end_date: in45days,
            },
          ],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.queryByTestId('events-now')).toBeNull()
    expect(screen.getByTestId('events-next')).toHaveTextContent('Prochainement')
    expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days))
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2')
  })
  test('Should not display "next" section if empty', async () => {
    // Given
    window.localStorage.setItem('access_token', 'fake-access-token')
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [
            {
              description: 'Holiday 1',
              start_date: today,
              end_date: in15days,
            },
          ],
          next: [],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('events-now')).toHaveTextContent("D'ici un mois")
    expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(today))
    expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1')
    expect(screen.queryByTestId('events-next')).toBeNull()
  })
  test('Should not repeat month', async () => {
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [
            {
              description: 'Holiday 1',
              start_date: today,
              end_date: in15days,
            },
            {
              description: 'Holiday 2',
              start_date: today,
              end_date: in32days,
            },
          ],
          next: [
            {
              description: 'Holiday 3',
              start_date: in32days,
              end_date: in45days,
            },
            {
              description: 'Holiday 4',
              start_date: in32days,
              end_date: in60days,
            },
          ],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('events-now')).toHaveTextContent("D'ici un mois")
    expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(today))
    const today_month_occurrences = (
      screen
        .getByTestId('events-now')
        .textContent.match(new RegExp(monthName(today), 'g')) || []
    ).length
    expect(today_month_occurrences).toBe(1)
    expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1')
    expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 2')
    expect(screen.getByTestId('events-next')).toHaveTextContent('Prochainement')
    expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days))
    const in32days_month_occurrences = (
      screen
        .getByTestId('events-now')
        .textContent.match(new RegExp(monthName(today), 'g')) || []
    ).length
    expect(in32days_month_occurrences).toBe(1)
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 3')
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 4')
  })
  test('Should not repeat month (with "next" part empty)', async () => {
    // Given
    window.localStorage.setItem('access_token', 'fake-access-token')
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [],
          next: [
            {
              description: 'Holiday 1',
              start_date: in32days,
              end_date: in45days,
            },
            {
              description: 'Holiday 2',
              start_date: in32days,
              end_date: in60days,
            },
          ],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.queryByTestId('events-now')).toBeNull()
    expect(screen.getByTestId('events-next')).toHaveTextContent('Prochainement')
    expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days))
    const in32days_month_occurrences = (
      screen
        .getByTestId('events-next')
        .textContent.match(new RegExp(monthName(in32days), 'g')) || []
    ).length
    expect(in32days_month_occurrences).toBe(1)
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 1')
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2')
  })
  test('Should not repeat month (when last "next" event month is the same as first "next" event month)', async () => {
    // Given
    window.localStorage.setItem('access_token', 'fake-access-token')
    var start1 = today
    var start2 = new Date(today.getTime() + 1 * oneday_in_ms)
    if (start1.getMonth() != start2.getMonth()) {
      start1 = new Date(today.getTime() + 1 * oneday_in_ms)
      start2 = new Date(today.getTime() + 2 * oneday_in_ms)
    }
    const spy = vi
      .spyOn(holidayMethods, 'retrieveHolidays')
      .mockImplementation(async () => {
        return {
          now: [
            {
              description: 'Holiday 1',
              start_date: start1,
              end_date: start2,
            },
          ],
          next: [
            {
              description: 'Holiday 2',
              start_date: start2,
              end_date: in32days,
            },
          ],
        }
      })

    // When
    render(Page)
    await new Promise(setTimeout) // wait for async calls

    // Then
    expect(monthName(start1)).toEqual(monthName(start2))
    expect(spy).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('events-now')).toHaveTextContent("D'ici un mois")
    expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(start1))
    expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1')
    expect(screen.getByTestId('events-next')).toHaveTextContent('Prochainement')
    expect(screen.getByTestId('events-next')).not.toHaveTextContent(monthName(start2))
    expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2')
  })
})
