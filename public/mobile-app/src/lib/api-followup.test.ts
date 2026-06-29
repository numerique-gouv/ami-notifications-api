import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { archiveFollowUpItem, retrieveFollowUp } from '$lib/api-followup';

const followUpItemsData = {
  notifications: {
    status: 'success',
    items: [
      {
        external_id: 'psl:OperationTranquilliteVacances:42',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: new Date('2026-02-23T15:50:00Z'),
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        external_url: null,
        is_archived: true,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
      },
      {
        external_id: 'psl:OperationTranquilliteVacances:43',
        status_id: 'wip',
        status_label: 'En cours',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en cours de traitement.',
        external_url: 'http://otv.fr',
        is_archived: false,
        created_at: new Date('2026-01-22T14:50:00Z'),
        updated_at: new Date('2026-01-22T14:55:00Z'),
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
};

type APIFollowUpItemsKey = keyof typeof followUpItemsData;
type NullableAPIFollowUpItems = {
  [K in APIFollowUpItemsKey]: (typeof followUpItemsData)[K] | null;
};

describe('/api-followup', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  describe('retrieveFollowUp', () => {
    test('should get followup items from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(followUpItemsData), { status: 200 })
        );

      // When
      const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=notifications',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        notifications: followUpItemsData.notifications.items,
      });
      expect(window.localStorage.getItem('notifications_followup_items')).toEqual(
        JSON.stringify(followUpItemsData.notifications)
      );
    });

    test('should get followup items from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=notifications',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        notifications: [],
      });
      expect(window.localStorage.getItem('notifications_followup_items')).toEqual(null);
    });

    test('should get followup items from localstorage', async () => {
      // Given
      window.localStorage.setItem(
        'notifications_followup_items',
        JSON.stringify(followUpItemsData.notifications)
      );

      // When
      const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(result).toEqual({
        notifications: followUpItemsData.notifications.items,
      });
    });

    test('should get followup items from API - followup items entry is missing in localstorage', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            continue;
          }
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData[key2])
          );
        }
        const responseData: NullableAPIFollowUpItems = {
          notifications: null,
        };
        responseData[key] = followUpItemsData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: followUpItemsData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_followup_items`)).toEqual(
          JSON.stringify(followUpItemsData[key])
        );
      }
    });

    test('should get followup items from API - followup items entry is wrong in localstorage', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(`${key2}_followup_items`, 'wrong');
            continue;
          }
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData[key2])
          );
        }
        const responseData: NullableAPIFollowUpItems = {
          notifications: null,
        };
        responseData[key] = followUpItemsData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: followUpItemsData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_followup_items`)).toEqual(
          JSON.stringify(followUpItemsData[key])
        );
      }
    });

    test('should get followup items from API - followup items entry is in failed status in localstorage', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(
              `${key2}_followup_items`,
              JSON.stringify({ status: 'failed' })
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData[key2])
          );
        }
        const responseData: NullableAPIFollowUpItems = {
          notifications: null,
        };
        responseData[key] = followUpItemsData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: followUpItemsData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_followup_items`)).toEqual(
          JSON.stringify(followUpItemsData[key])
        );
      }
    });

    test('should get followup items from API - followup items entry has no expiration in localstorage', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...followUpItemsData[key2] }; // old entry, no expiration date
            window.localStorage.setItem(
              `${key2}_followup_items`,
              JSON.stringify(entry)
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData[key2])
          );
        }
        const responseData: NullableAPIFollowUpItems = {
          notifications: null,
        };
        responseData[key] = followUpItemsData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: followUpItemsData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_followup_items`)).toEqual(
          JSON.stringify(followUpItemsData[key])
        );
      }
    });

    test('should get followup items from API - followup items entry has no expiration in localstorage - with error', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        const followUpItemsData2: NullableAPIFollowUpItems = {
          notifications: null,
        };
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...followUpItemsData[key2] }; // old entry, no expiration date
            followUpItemsData2[key2] = entry as (typeof followUpItemsData)[typeof key2];
            window.localStorage.setItem(
              `${key2}_followup_items`,
              JSON.stringify(followUpItemsData2[key2])
            );
            continue;
          }
          followUpItemsData2[key2] = followUpItemsData[key2];
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData2[key2])
          );
        }
        const responseData: NullableAPIFollowUpItems = {
          notifications: null,
        };
        const { ...entry } = followUpItemsData[key];
        entry.status = 'failed';
        responseData[key] = entry;
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: followUpItemsData2.notifications?.items,
        });
        expect(window.localStorage.getItem(`${key}_followup_items`)).toEqual(
          JSON.stringify(followUpItemsData2[key])
        );
      }
    });

    test('should get followup items from API - followup items entry is expired in localstorage', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            const entry = { ...followUpItemsData[key2] };
            entry.expires_at = new Date('2025-11-01T11:59:59Z'); // expired
            window.localStorage.setItem(
              `${key2}_followup_items`,
              JSON.stringify(entry)
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData[key2])
          );
        }
        const responseData: NullableAPIFollowUpItems = {
          notifications: null,
        };
        responseData[key] = followUpItemsData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: followUpItemsData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_followup_items`)).toEqual(
          JSON.stringify(followUpItemsData[key])
        );
      }
    });

    test('should get followup items from API - followup items entry is not expired in localstorage', async () => {
      for (const key of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
        // Given
        window.localStorage.clear();
        for (const key2 of Object.keys(followUpItemsData) as APIFollowUpItemsKey[]) {
          if (key2 === key) {
            const entry = { ...followUpItemsData[key2] };
            entry.expires_at = new Date('2025-11-01T12:00:00Z'); // not yet expired
            window.localStorage.setItem(
              `${key2}_followup_items`,
              JSON.stringify(entry)
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_followup_items`,
            JSON.stringify(followUpItemsData[key2])
          );
        }

        // When
        const result = await retrieveFollowUp(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(result).toEqual({
          notifications: followUpItemsData.notifications.items,
        });
      }
    });
  });

  describe('archiveFollowUpItem', () => {
    test('should return true', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }));

      // When
      const result = await archiveFollowUpItem('notifications', 'id');

      // Then
      expect(result).toEqual(true);
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/follow-up/item/notifications/id/archive',
        {
          body: '{"is_archived":true}',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
    });
    test('should return false: 400 error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 400 }));

      // When
      const result = await archiveFollowUpItem('notifications', 'id');

      // Then
      expect(result).toEqual(false);
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/follow-up/item/notifications/id/archive',
        {
          body: '{"is_archived":true}',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
    });
    test('should return false: 500 error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response(JSON.stringify({}), { status: 500 }));

      // When
      const result = await archiveFollowUpItem('notifications', 'id');

      // Then
      expect(result).toEqual(false);
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/follow-up/item/notifications/id/archive',
        {
          body: '{"is_archived":true}',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
    });
  });
});
