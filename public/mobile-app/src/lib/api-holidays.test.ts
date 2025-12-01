import { afterEach, describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { retrieveHolidays } from '$lib/api-holidays'

describe('/api-holidays', () => {
  describe('retrieveHolidays', () => {
    afterEach(() => {
      window.localStorage.clear()
    })
    test('should get holidays from API', async () => {
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
        new Response(
          JSON.stringify(holidaysData),
          { status: 200 }
        )
      )

      // When
      const result = await retrieveHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual(holidaysData)
      expect(window.localStorage.getItem('holidays_data')).toEqual(
        JSON.stringify(holidaysData)
      )
    })
    test('should get holidays from API with error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('',
          { status: 400 }
        )
      )

      // When
      const result = await retrieveHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual([])
      expect(window.localStorage.getItem('holidays_data')).toEqual(null)
    })
    test('should get holidays data from local storage', async () => {
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
      window.localStorage.setItem('holidays_data', JSON.stringify(holidaysData))

      // When
      const result = await retrieveHolidays(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual(holidaysData)
    })
  })
})
