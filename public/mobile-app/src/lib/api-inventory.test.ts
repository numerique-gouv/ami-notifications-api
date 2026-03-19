import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveInventory } from '$lib/api-inventory';

const inventoryData = {
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
        created_at: new Date('2026-01-22T14:50:00Z'),
        updated_at: new Date('2026-01-22T14:55:00Z'),
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
};

type InventoryKey = keyof typeof inventoryData;

describe('/api-inventory', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  describe('retrieveInventory', () => {
    test('should get inventory from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(inventoryData), { status: 200 })
        );

      // When
      const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/data/follow-up/inventories?filter-items=notifications',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        notifications: inventoryData.notifications.items,
      });
      expect(window.localStorage.getItem('notifications_inventory')).toEqual(
        JSON.stringify(inventoryData.notifications)
      );
    });

    test('should get inventory from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/data/follow-up/inventories?filter-items=notifications',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        notifications: [],
      });
      expect(window.localStorage.getItem('notifications_inventory')).toEqual(null);
    });

    test('should get inventory from localstorage', async () => {
      // Given
      window.localStorage.setItem(
        'notifications_inventory',
        JSON.stringify(inventoryData.notifications)
      );

      // When
      const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(result).toEqual({
        notifications: inventoryData.notifications.items,
      });
    });

    test('should get inventory from API - inventory entry is missing in localstorage', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            continue;
          }
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData[key2])
          );
        }
        const responseData: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        responseData[key] = inventoryData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: inventoryData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_inventory`)).toEqual(
          JSON.stringify(inventoryData[key])
        );
      }
    });

    test('should get inventory from API - inventory entry is wrong in localstorage', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(`${key2}_inventory`, 'wrong');
            continue;
          }
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData[key2])
          );
        }
        const responseData: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        responseData[key] = inventoryData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: inventoryData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_inventory`)).toEqual(
          JSON.stringify(inventoryData[key])
        );
      }
    });

    test('should get inventory from API - inventory entry is in failed status in localstorage', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(
              `${key2}_inventory`,
              JSON.stringify({ status: 'failed' })
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData[key2])
          );
        }
        const responseData: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        responseData[key] = inventoryData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: inventoryData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_inventory`)).toEqual(
          JSON.stringify(inventoryData[key])
        );
      }
    });

    test('should get inventory from API - inventory entry has no expiration in localstorage', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...inventoryData[key2] }; // old entry, no expiration date
            window.localStorage.setItem(`${key2}_inventory`, JSON.stringify(entry));
            continue;
          }
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData[key2])
          );
        }
        const responseData: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        responseData[key] = inventoryData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: inventoryData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_inventory`)).toEqual(
          JSON.stringify(inventoryData[key])
        );
      }
    });

    test('should get inventory from API - inventory entry has no expiration in localstorage - with error', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        const inventoryData2: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...inventoryData[key2] }; // old entry, no expiration date
            inventoryData2[key2] = entry;
            window.localStorage.setItem(
              `${key2}_inventory`,
              JSON.stringify(inventoryData2[key2])
            );
            continue;
          }
          inventoryData2[key2] = inventoryData[key2];
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData2[key2])
          );
        }
        const responseData: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        const { ...entry } = inventoryData[key];
        entry.status = 'failed';
        responseData[key] = entry;
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: inventoryData2.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_inventory`)).toEqual(
          JSON.stringify(inventoryData2[key])
        );
      }
    });

    test('should get inventory from API - inventory entry is expired in localstorage', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            const entry = { ...inventoryData[key2] };
            entry.expires_at = new Date('2025-11-01T11:59:59Z'); // expired
            window.localStorage.setItem(`${key2}_inventory`, JSON.stringify(entry));
            continue;
          }
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData[key2])
          );
        }
        const responseData: { [K in InventoryKey]: any } = {
          notifications: null,
        };
        responseData[key] = inventoryData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/data/follow-up/inventories?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          notifications: inventoryData.notifications.items,
        });
        expect(window.localStorage.getItem(`${key}_inventory`)).toEqual(
          JSON.stringify(inventoryData[key])
        );
      }
    });

    test('should get inventory from API - inventory entry is not expired in localstorage', async () => {
      for (const key of Object.keys(inventoryData) as InventoryKey[]) {
        // Given
        window.localStorage.clear();
        for (const key2 of Object.keys(inventoryData) as InventoryKey[]) {
          if (key2 === key) {
            const entry = { ...inventoryData[key2] };
            entry.expires_at = new Date('2025-11-01T12:00:00Z'); // not yet expired
            window.localStorage.setItem(`${key2}_inventory`, JSON.stringify(entry));
            continue;
          }
          window.localStorage.setItem(
            `${key2}_inventory`,
            JSON.stringify(inventoryData[key2])
          );
        }

        // When
        const result = await retrieveInventory(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(result).toEqual({
          notifications: inventoryData.notifications.items,
        });
      }
    });
  });
});
