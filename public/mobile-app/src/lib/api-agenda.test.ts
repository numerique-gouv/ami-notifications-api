import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveAgenda } from '$lib/api-agenda';

const apiAgendaData = {
  school_holidays: {
    status: 'success',
    items: [
      {
        kind: 'holiday',
        title: 'Holiday 1',
        description: '',
        date: null as Date | null,
        start_date: new Date('2025-09-20T23:00:00Z') as Date | null,
        end_date: new Date('2025-12-15T23:00:00Z') as Date | null,
        zones: [] as string[] | string,
        emoji: '',
      },
      {
        kind: 'holiday',
        title: 'Holiday 2',
        description: '',
        date: null as Date | null,
        start_date: new Date('2025-10-20T23:00:00Z') as Date | null,
        end_date: new Date('2025-11-15T23:00:00Z') as Date | null,
        zones: [] as string[] | string,
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
        date: new Date('2025-09-20T23:00:00Z') as Date | null,
        start_date: null as Date | null,
        end_date: null as Date | null,
        zones: [] as string[] | string,
        emoji: '',
      },
      {
        kind: 'holiday',
        title: 'Holiday 4',
        description: '',
        date: new Date('2025-10-20T23:00:00Z') as Date | null,
        start_date: null as Date | null,
        end_date: null as Date | null,
        zones: [] as string[] | string,
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
        date: new Date('2025-09-20T23:00:00Z') as Date | null,
        start_date: null as Date | null,
        end_date: null as Date | null,
        zones: [] as string[] | string,
        emoji: '',
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
};

type AgendaSourceKey = keyof typeof apiAgendaData;
type NullableAgendaSource = {
  [K in AgendaSourceKey]: (typeof apiAgendaData)[K] | null;
};

describe('/api-agenda', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  describe('retrieveAgenda', () => {
    test('should get agenda items from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiAgendaData), { status: 200 })
        );

      // When
      const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=school_holidays&filter-items=public_holidays&filter-items=elections',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        school_holidays: apiAgendaData.school_holidays.items,
        public_holidays: apiAgendaData.public_holidays.items,
        elections: apiAgendaData.elections.items,
      });
      expect(window.localStorage.getItem('school_holidays_agenda_source')).toEqual(
        JSON.stringify(apiAgendaData.school_holidays)
      );
      expect(window.localStorage.getItem('public_holidays_agenda_source')).toEqual(
        JSON.stringify(apiAgendaData.public_holidays)
      );
      expect(window.localStorage.getItem('elections_agenda_source')).toEqual(
        JSON.stringify(apiAgendaData.elections)
      );
    });

    test('should get agenda items from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=school_holidays&filter-items=public_holidays&filter-items=elections',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        school_holidays: [],
        public_holidays: [],
        elections: [],
      });
      expect(window.localStorage.getItem('school_holidays_agenda_source')).toEqual(
        null
      );
      expect(window.localStorage.getItem('public_holidays_agenda_source')).toEqual(
        null
      );
      expect(window.localStorage.getItem('elections_agenda_source')).toEqual(null);
    });

    test('should get agenda items from localstorage', async () => {
      // Given
      window.localStorage.setItem(
        'school_holidays_agenda_source',
        JSON.stringify(apiAgendaData.school_holidays)
      );
      window.localStorage.setItem(
        'public_holidays_agenda_source',
        JSON.stringify(apiAgendaData.public_holidays)
      );
      window.localStorage.setItem(
        'elections_agenda_source',
        JSON.stringify(apiAgendaData.elections)
      );

      // When
      const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(result).toEqual({
        school_holidays: apiAgendaData.school_holidays.items,
        public_holidays: apiAgendaData.public_holidays.items,
        elections: apiAgendaData.elections.items,
      });
    });

    test('should get agenda items from API - agenda items entry is missing in localstorage', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            continue;
          }
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData[key2])
          );
        }
        const responseData: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        responseData[key] = apiAgendaData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          school_holidays: apiAgendaData.school_holidays.items,
          public_holidays: apiAgendaData.public_holidays.items,
          elections: apiAgendaData.elections.items,
        });
        expect(window.localStorage.getItem(`${key}_agenda_source`)).toEqual(
          JSON.stringify(apiAgendaData[key])
        );
      }
    });

    test('should get agenda items from API - agenda items entry is wrong in localstorage', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(`${key2}_agenda_source`, 'wrong');
            continue;
          }
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData[key2])
          );
        }
        const responseData: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        responseData[key] = apiAgendaData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          school_holidays: apiAgendaData.school_holidays.items,
          public_holidays: apiAgendaData.public_holidays.items,
          elections: apiAgendaData.elections.items,
        });
        expect(window.localStorage.getItem(`${key}_agenda_source`)).toEqual(
          JSON.stringify(apiAgendaData[key])
        );
      }
    });

    test('should get agenda items from API - agenda items entry is in failed status in localstorage', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(
              `${key2}_agenda_source`,
              JSON.stringify({ status: 'failed' })
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData[key2])
          );
        }
        const responseData: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        responseData[key] = apiAgendaData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          school_holidays: apiAgendaData.school_holidays.items,
          public_holidays: apiAgendaData.public_holidays.items,
          elections: apiAgendaData.elections.items,
        });
        expect(window.localStorage.getItem(`${key}_agenda_source`)).toEqual(
          JSON.stringify(apiAgendaData[key])
        );
      }
    });

    test('should get agenda items from API - agenda items entry has no expiration in localstorage', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...apiAgendaData[key2] }; // old entry, no expiration date
            window.localStorage.setItem(`${key2}_agenda_source`, JSON.stringify(entry));
            continue;
          }
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData[key2])
          );
        }
        const responseData: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        responseData[key] = apiAgendaData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          school_holidays: apiAgendaData.school_holidays.items,
          public_holidays: apiAgendaData.public_holidays.items,
          elections: apiAgendaData.elections.items,
        });
        expect(window.localStorage.getItem(`${key}_agenda_source`)).toEqual(
          JSON.stringify(apiAgendaData[key])
        );
      }
    });

    test('should get agenda items from API - agenda items entry has no expiration in localstorage - with error', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        const apiAgendaData2: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...apiAgendaData[key2] }; // old entry, no expiration date
            apiAgendaData2[key2] = entry as (typeof apiAgendaData)[typeof key2];
            window.localStorage.setItem(
              `${key2}_agenda_source`,
              JSON.stringify(apiAgendaData2[key2])
            );
            continue;
          }
          apiAgendaData2[key2] = apiAgendaData[key2];
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData2[key2])
          );
        }
        const responseData: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        const { ...entry } = apiAgendaData[key];
        entry.status = 'failed';
        responseData[key] = entry;
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          school_holidays: apiAgendaData2.school_holidays?.items,
          public_holidays: apiAgendaData2.public_holidays?.items,
          elections: apiAgendaData2.elections?.items,
        });
        expect(window.localStorage.getItem(`${key}_agenda_source`)).toEqual(
          JSON.stringify(apiAgendaData2[key])
        );
      }
    });

    test('should get agenda items from API - agenda items entry is expired in localstorage', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            const entry = { ...apiAgendaData[key2] };
            entry.expires_at = new Date('2025-11-01T11:59:59Z'); // expired
            window.localStorage.setItem(`${key2}_agenda_source`, JSON.stringify(entry));
            continue;
          }
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData[key2])
          );
        }
        const responseData: NullableAgendaSource = {
          school_holidays: null,
          public_holidays: null,
          elections: null,
        };
        responseData[key] = apiAgendaData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/agenda?current_date=2025-11-01&filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          school_holidays: apiAgendaData.school_holidays.items,
          public_holidays: apiAgendaData.public_holidays.items,
          elections: apiAgendaData.elections.items,
        });
        expect(window.localStorage.getItem(`${key}_agenda_source`)).toEqual(
          JSON.stringify(apiAgendaData[key])
        );
      }
    });

    test('should get agenda items from API - agenda items entry is not expired in localstorage', async () => {
      for (const key of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
        // Given
        window.localStorage.clear();
        for (const key2 of Object.keys(apiAgendaData) as AgendaSourceKey[]) {
          if (key2 === key) {
            const entry = { ...apiAgendaData[key2] };
            entry.expires_at = new Date('2025-11-01T12:00:00Z'); // not yet expired
            window.localStorage.setItem(`${key2}_agenda_source`, JSON.stringify(entry));
            continue;
          }
          window.localStorage.setItem(
            `${key2}_agenda_source`,
            JSON.stringify(apiAgendaData[key2])
          );
        }

        // When
        const result = await retrieveAgenda(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(result).toEqual({
          school_holidays: apiAgendaData.school_holidays.items,
          public_holidays: apiAgendaData.public_holidays.items,
          elections: apiAgendaData.elections.items,
        });
      }
    });
  });
});
