import { afterEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { retrieveCatalog } from '$lib/api-catalog'

const catalogData = {
  school_holidays: {
    status: 'success',
    items: [
      {
        kind: 'holiday',
        title: 'Holiday 1',
        description: '',
        date: null,
        start_date: new Date('2025-09-20T23:00:00Z'),
        end_date: new Date('2025-12-15T23:00:00Z'),
        zones: '',
        emoji: '',
      },
      {
        kind: 'holiday',
        title: 'Holiday 2',
        description: '',
        date: null,
        start_date: new Date('2025-10-20T23:00:00Z'),
        end_date: new Date('2025-11-15T23:00:00Z'),
        zones: '',
        emoji: '',
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
  public_holidays: {
    status: 'success',
    items: [
      {
        kind: 'holiday',
        title: 'Holiday 3',
        description: '',
        date: new Date('2025-09-20T23:00:00Z'),
        start_date: null,
        end_date: null,
        zones: '',
        emoji: '',
      },
      {
        kind: 'holiday',
        title: 'Holiday 4',
        description: '',
        date: new Date('2025-10-20T23:00:00Z'),
        start_date: null,
        end_date: null,
        zones: '',
        emoji: '',
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
  elections: {
    status: 'success',
    items: [
      {
        kind: 'election',
        title: 'Election 1',
        description: '',
        date: new Date('2025-09-20T23:00:00Z'),
        start_date: null,
        end_date: null,
        zones: '',
        emoji: '',
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
}

type CatalogKey = keyof typeof catalogData

describe('/api-catalog', () => {
  afterEach(() => {
    window.localStorage.clear()
    vi.clearAllMocks()
  })

  describe('retrieveCatalog', () => {
    test('should get catalog from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify(catalogData), { status: 200 }))

      // When
      const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=school_holidays&filter-items=public_holidays&filter-items=elections',
        { credentials: 'include' }
      )
      expect(result).toEqual({
        school_holidays: catalogData.school_holidays.items,
        public_holidays: catalogData.public_holidays.items,
        elections: catalogData.elections.items,
      })
      expect(window.localStorage.getItem('school_holidays_catalog')).toEqual(
        JSON.stringify(catalogData.school_holidays)
      )
      expect(window.localStorage.getItem('public_holidays_catalog')).toEqual(
        JSON.stringify(catalogData.public_holidays)
      )
      expect(window.localStorage.getItem('elections_catalog')).toEqual(
        JSON.stringify(catalogData.elections)
      )
    })

    test('should get catalog from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }))

      // When
      const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=school_holidays&filter-items=public_holidays&filter-items=elections',
        { credentials: 'include' }
      )
      expect(result).toEqual({
        school_holidays: [],
        public_holidays: [],
        elections: [],
      })
      expect(window.localStorage.getItem('school_holidays_catalog')).toEqual(null)
      expect(window.localStorage.getItem('public_holidays_catalog')).toEqual(null)
      expect(window.localStorage.getItem('elections_holidays_catalog')).toEqual(null)
    })

    test('should get catalog from localstorage', async () => {
      // Given
      window.localStorage.setItem(
        'school_holidays_catalog',
        JSON.stringify(catalogData.school_holidays)
      )
      window.localStorage.setItem(
        'public_holidays_catalog',
        JSON.stringify(catalogData.public_holidays)
      )
      window.localStorage.setItem(
        'elections_catalog',
        JSON.stringify(catalogData.elections)
      )

      // When
      const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(result).toEqual({
        school_holidays: catalogData.school_holidays.items,
        public_holidays: catalogData.public_holidays.items,
        elections: catalogData.elections.items,
      })
    })

    test('should get catalog from API - catalog entry is missing in localstorage', async () => {
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        // Given
        window.localStorage.clear()
        vi.clearAllMocks()
        for (const key2 of Object.keys(catalogData) as CatalogKey[]) {
          if (key2 === key) {
            continue
          }
          window.localStorage.setItem(
            `${key2}_catalog`,
            JSON.stringify(catalogData[key2])
          )
        }
        const responseData: { [K in CatalogKey]: any } = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        }
        responseData[key] = catalogData[key]
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          )

        // When
        const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        )
        expect(result).toEqual({
          school_holidays: catalogData.school_holidays.items,
          public_holidays: catalogData.public_holidays.items,
          elections: catalogData.elections.items,
        })
        expect(window.localStorage.getItem(`${key}_catalog`)).toEqual(
          JSON.stringify(catalogData[key])
        )
      }
    })

    test('should get catalog from API - catalog entry is wrong in localstorage', async () => {
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        // Given
        window.localStorage.clear()
        vi.clearAllMocks()
        for (const key2 of Object.keys(catalogData) as CatalogKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(`${key2}_catalog`, 'wrong')
            continue
          }
          window.localStorage.setItem(
            `${key2}_catalog`,
            JSON.stringify(catalogData[key2])
          )
        }
        const responseData: { [K in CatalogKey]: any } = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        }
        responseData[key] = catalogData[key]
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          )

        // When
        const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        )
        expect(result).toEqual({
          school_holidays: catalogData.school_holidays.items,
          public_holidays: catalogData.public_holidays.items,
          elections: catalogData.elections.items,
        })
        expect(window.localStorage.getItem(`${key}_catalog`)).toEqual(
          JSON.stringify(catalogData[key])
        )
      }
    })

    test('should get catalog from API - catalog entry is in failed status in localstorage', async () => {
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        // Given
        window.localStorage.clear()
        vi.clearAllMocks()
        for (const key2 of Object.keys(catalogData) as CatalogKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(
              `${key2}_catalog`,
              JSON.stringify({ status: 'failed' })
            )
            continue
          }
          window.localStorage.setItem(
            `${key2}_catalog`,
            JSON.stringify(catalogData[key2])
          )
        }
        const responseData: { [K in CatalogKey]: any } = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        }
        responseData[key] = catalogData[key]
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          )

        // When
        const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        )
        expect(result).toEqual({
          school_holidays: catalogData.school_holidays.items,
          public_holidays: catalogData.public_holidays.items,
          elections: catalogData.elections.items,
        })
        expect(window.localStorage.getItem(`${key}_catalog`)).toEqual(
          JSON.stringify(catalogData[key])
        )
      }
    })

    test('should get catalog from API - catalog entry has no expiration in localstorage', async () => {
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        // Given
        window.localStorage.clear()
        vi.clearAllMocks()
        for (const key2 of Object.keys(catalogData) as CatalogKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...catalogData[key2] } // old entry, no expiration date
            window.localStorage.setItem(`${key2}_catalog`, JSON.stringify(entry))
            continue
          }
          window.localStorage.setItem(
            `${key2}_catalog`,
            JSON.stringify(catalogData[key2])
          )
        }
        const responseData: { [K in CatalogKey]: any } = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        }
        responseData[key] = catalogData[key]
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          )

        // When
        const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        )
        expect(result).toEqual({
          school_holidays: catalogData.school_holidays.items,
          public_holidays: catalogData.public_holidays.items,
          elections: catalogData.elections.items,
        })
        expect(window.localStorage.getItem(`${key}_catalog`)).toEqual(
          JSON.stringify(catalogData[key])
        )
      }
    })

    test('should get catalog from API - catalog entry is expired in localstorage', async () => {
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        // Given
        window.localStorage.clear()
        vi.clearAllMocks()
        for (const key2 of Object.keys(catalogData) as CatalogKey[]) {
          if (key2 === key) {
            const entry = { ...catalogData[key2] }
            entry.expires_at = new Date('2025-11-01T11:59:59Z') // expired
            window.localStorage.setItem(`${key2}_catalog`, JSON.stringify(entry))
            continue
          }
          window.localStorage.setItem(
            `${key2}_catalog`,
            JSON.stringify(catalogData[key2])
          )
        }
        const responseData: { [K in CatalogKey]: any } = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        }
        responseData[key] = catalogData[key]
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          )

        // When
        const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/agenda/items?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        )
        expect(result).toEqual({
          school_holidays: catalogData.school_holidays.items,
          public_holidays: catalogData.public_holidays.items,
          elections: catalogData.elections.items,
        })
        expect(window.localStorage.getItem(`${key}_catalog`)).toEqual(
          JSON.stringify(catalogData[key])
        )
      }
    })

    test('should get catalog from API - catalog entry is not expired in localstorage', async () => {
      for (const key of Object.keys(catalogData) as CatalogKey[]) {
        // Given
        window.localStorage.clear()
        for (const key2 of Object.keys(catalogData) as CatalogKey[]) {
          if (key2 === key) {
            const entry = { ...catalogData[key2] }
            entry.expires_at = new Date('2025-11-01T12:00:00Z') // not yet expired
            window.localStorage.setItem(`${key2}_catalog`, JSON.stringify(entry))
            continue
          }
          window.localStorage.setItem(
            `${key2}_catalog`,
            JSON.stringify(catalogData[key2])
          )
        }

        // When
        const result = await retrieveCatalog(new Date('2025-11-01T12:00:00Z'))

        // Then
        expect(result).toEqual({
          school_holidays: catalogData.school_holidays.items,
          public_holidays: catalogData.public_holidays.items,
          elections: catalogData.elections.items,
        })
      }
    })
  })
})
