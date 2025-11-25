import { afterEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { dayName, monthName, holidayPeriod, retrieveHolidays } from '$lib/api-holidays'

describe('/api-holidays', () => {
  describe('dayName', () => {
    test('should return short day name', async () => {
      // Given
      const date = new Date('2025-11-11')

      // When
      const name = dayName(date)

      // Then
      expect(name).equal('mar')
    })
  })
  describe('monthName', () => {
    test('should return long month name', async () => {
      // Given
      const date = new Date('2025-11-11')

      // When
      const name = monthName(date)

      // Then
      expect(name).equal('Novembre')
    })
  })
  describe('holidayPeriod', () => {
    test('should not mention start date year', async () => {
      // Given
      const startDate = new Date('2025-10-15')
      const endDate = new Date('2025-11-15')

      // When
      const period = holidayPeriod(startDate, endDate)

      // Then
      expect(period).equal('Du 15 octobre au 15 novembre 2025')
    })
    test('should not mention start date year and month', async () => {
      // Given
      const startDate = new Date('2025-10-15')
      const endDate = new Date('2025-10-20')

      // When
      const period = holidayPeriod(startDate, endDate)

      // Then
      expect(period).equal('Du 15 au 20 octobre 2025')
    })
    test('should mention start date year and month', async () => {
      // Given
      const startDate = new Date('2025-12-20')
      const endDate = new Date('2026-01-02')

      // When
      const period = holidayPeriod(startDate, endDate)

      // Then
      expect(period).equal('Du 20 décembre 2025 au 2 janvier 2026')
    })
  })
  describe('retrieveHolidays', () => {
    test('should get holidays from API', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris')
      const holiday1 = {
        description: 'Holiday 1',
        start_date: '2025-09-20T23:00:00Z',
        end_date: '2025-12-15T23:00:00Z',
        zones: '',
        emoji: '',
      }
      const holiday2 = {
        description: 'Holiday 2',
        start_date: '2025-10-20T23:00:00Z',
        end_date: '2025-11-15T23:00:00Z',
        zones: '',
        emoji: '',
      }
      const holiday3 = {
        description: 'Holiday 3',
        start_date: '2025-11-20T23:00:00Z',
        end_date: '2025-12-15T23:00:00Z',
        zones: '',
        emoji: '',
      }
      const holiday4 = {
        description: 'Holiday 4',
        start_date: '2025-11-30T23:00:00Z',
        end_date: '2025-12-16T23:00:00Z',
        zones: '',
        emoji: '',
      }
      const holiday5 = {
        description: 'Holiday 5',
        start_date: '2025-12-20T23:00:00Z',
        end_date: '2025-12-24T23:00:00Z',
        zones: '',
        emoji: '',
      }
      globalThis.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () =>
            Promise.resolve([holiday1, holiday2, holiday3, holiday4, holiday5]),
        })
      )

      // When
      const result = await retrieveHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual({
        now: [holiday1, holiday2, holiday3],
        next: [holiday4, holiday5],
      })
    })
  })
})
