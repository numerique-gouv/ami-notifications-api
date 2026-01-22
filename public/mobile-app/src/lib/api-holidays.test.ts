import { afterEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { retrievePublicHolidays, retrieveSchoolHolidays } from '$lib/api-holidays'

describe('/api-holidays', () => {
  afterEach(() => {
    window.localStorage.clear()
  })

  describe('retrieveSchoolHolidays', () => {
    test('should get school holidays from API', async () => {
      // Given
      const holidaysData = [
        {
          description: 'Holiday 1',
          start_date: new Date('2025-09-20T23:00:00Z'),
          end_date: new Date('2025-12-15T23:00:00Z'),
          zones: '',
          emoji: '',
        },
        {
          description: 'Holiday 2',
          start_date: new Date('2025-10-20T23:00:00Z'),
          end_date: new Date('2025-11-15T23:00:00Z'),
          zones: '',
          emoji: '',
        },
      ]
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(holidaysData), { status: 200 })
      )

      // When
      const result = await retrieveSchoolHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual(holidaysData)
      expect(window.localStorage.getItem('school_holidays_data')).toEqual(
        JSON.stringify(holidaysData)
      )
    })
    test('should get school holidays from API with error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('error', { status: 400 })
      )

      // When
      const result = await retrieveSchoolHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual([])
      expect(window.localStorage.getItem('school_holidays_data')).toEqual(null)
    })
    test('should get school holidays data from local storage', async () => {
      // Given
      const holidaysData = [
        {
          description: 'Holiday 1',
          start_date: new Date('2025-09-20T23:00:00Z'),
          end_date: new Date('2025-12-15T23:00:00Z'),
          zones: '',
          emoji: '',
        },
        {
          description: 'Holiday 2',
          start_date: new Date('2025-10-20T23:00:00Z'),
          end_date: new Date('2025-11-15T23:00:00Z'),
          zones: '',
          emoji: '',
        },
      ]
      window.localStorage.setItem('school_holidays_data', JSON.stringify(holidaysData))

      // When
      const result = await retrieveSchoolHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual(holidaysData)
    })
  })
  describe('retrievePublicHolidays', () => {
    test('should get public holidays from API', async () => {
      // Given
      const holidaysData = [
        {
          description: 'Day 1',
          date: new Date('2025-09-20T23:00:00Z'),
          emoji: '',
        },
        {
          description: 'Day 2',
          date: new Date('2025-10-20T23:00:00Z'),
          emoji: '',
        },
      ]
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(holidaysData), { status: 200 })
      )

      // When
      const result = await retrievePublicHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual(holidaysData)
      expect(window.localStorage.getItem('public_holidays_data')).toEqual(
        JSON.stringify(holidaysData)
      )
    })
    test('should get public holidays from API with error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('error', { status: 400 })
      )

      // When
      const result = await retrievePublicHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual([])
      expect(window.localStorage.getItem('public_holidays_data')).toEqual(null)
    })
    test('should get public holidays data from local storage', async () => {
      // Given
      const holidaysData = [
        {
          description: 'Day 1',
          date: new Date('2025-09-20T23:00:00Z'),
          emoji: '',
        },
        {
          description: 'Day 2',
          date: new Date('2025-10-20T23:00:00Z'),
          emoji: '',
        },
      ]
      window.localStorage.setItem('public_holidays_data', JSON.stringify(holidaysData))

      // When
      const result = await retrievePublicHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual(holidaysData)
    })
  })
})
