import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { retrieveServices } from '$lib/api-services';

const apiServicesData = {
  internal: {
    status: 'success',
    items: [
      {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        title: 'Opération Tranquillité Vacances',
        short_description:
          'Inscrivez-vous pour protéger votre domicile pendant votre absence',
        description:
          "Pendant toute absence prolongée de votre domicile, vous pouvez vous inscrire à l'**opération tranquillité vacances**.",
        url: 'https://localhost:8000/mademarche/demarcheGenerique/?codeDemarche=OperationTranquilliteVacances&caller={back_param_token_jwt}',
        with_silent_login: true,
        created_at: '2026-02-23T17:24:00Z',
        updated_at: '2026-02-24T17:24:00Z',
      },
      {
        partner_id: 'dinum-dn',
        item_type: 'ContacterAMI',
        title: "Contacter l'équipe AMI",
        short_description: 'Faites-nous votre retour',
        description:
          "Pour tout retour sur l'application AMI, vous pouvez nous contacter par le biais de ce formulaire",
        url: 'https://localhost:8000/commencer/todo?id_hash_fc={fc_hash}&id_version={app_version_id}',
        with_silent_login: false,
        created_at: '2026-01-26T17:24:00Z',
        updated_at: '2026-01-27T17:24:00Z',
      },
    ],
    expires_at: new Date('2025-11-02T12:00:00Z'),
  },
};

type APIServicesItemsKey = keyof typeof apiServicesData;
type NullableAPIServicesItems = {
  [K in APIServicesItemsKey]: (typeof apiServicesData)[K] | null;
};

describe('/api-services', () => {
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  describe('retrieveServices', () => {
    test('should get services items from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiServicesData), { status: 200 })
        );

      // When
      const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/data/services?filter-items=internal',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        internal: apiServicesData.internal.items,
      });
      expect(window.localStorage.getItem('internal_services_source')).toEqual(
        JSON.stringify(apiServicesData.internal)
      );
    });

    test('should get services items from API - with error', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith(
        'https://localhost:8000/api/v1/users/data/services?filter-items=internal',
        { credentials: 'include' }
      );
      expect(result).toEqual({
        internal: [],
      });
      expect(window.localStorage.getItem('internal_services_source')).toEqual(null);
    });

    test('should get services items from localstorage', async () => {
      // Given
      window.localStorage.setItem(
        'internal_services_source',
        JSON.stringify(apiServicesData.internal)
      );

      // When
      const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(result).toEqual({
        internal: apiServicesData.internal.items,
      });
    });

    test('should get services items from API - services items entry is missing in localstorage', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            continue;
          }
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData[key2])
          );
        }
        const responseData: NullableAPIServicesItems = {
          internal: null,
        };
        responseData[key] = apiServicesData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/services?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          internal: apiServicesData.internal.items,
        });
        expect(window.localStorage.getItem(`${key}_services_source`)).toEqual(
          JSON.stringify(apiServicesData[key])
        );
      }
    });

    test('should get services items from API - services items entry is wrong in localstorage', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(`${key2}_services_source`, 'wrong');
            continue;
          }
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData[key2])
          );
        }
        const responseData: NullableAPIServicesItems = {
          internal: null,
        };
        responseData[key] = apiServicesData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/services?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          internal: apiServicesData.internal.items,
        });
        expect(window.localStorage.getItem(`${key}_services_source`)).toEqual(
          JSON.stringify(apiServicesData[key])
        );
      }
    });

    test('should get services items from API - services items entry is in failed status in localstorage', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            window.localStorage.setItem(
              `${key2}_services_source`,
              JSON.stringify({ status: 'failed' })
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData[key2])
          );
        }
        const responseData: NullableAPIServicesItems = {
          internal: null,
        };
        responseData[key] = apiServicesData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/services?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          internal: apiServicesData.internal.items,
        });
        expect(window.localStorage.getItem(`${key}_services_source`)).toEqual(
          JSON.stringify(apiServicesData[key])
        );
      }
    });

    test('should get services items from API - services items entry has no expiration in localstorage', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...apiServicesData[key2] }; // old entry, no expiration date
            window.localStorage.setItem(
              `${key2}_services_source`,
              JSON.stringify(entry)
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData[key2])
          );
        }
        const responseData: NullableAPIServicesItems = {
          internal: null,
        };
        responseData[key] = apiServicesData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/services?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          internal: apiServicesData.internal.items,
        });
        expect(window.localStorage.getItem(`${key}_services_source`)).toEqual(
          JSON.stringify(apiServicesData[key])
        );
      }
    });

    test('should get services items from API - services items entry has no expiration in localstorage - with error', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        const apiServicesData2: NullableAPIServicesItems = {
          internal: null,
        };
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            const { expires_at, ...entry } = { ...apiServicesData[key2] }; // old entry, no expiration date
            apiServicesData2[key2] = entry as (typeof apiServicesData)[typeof key2];
            window.localStorage.setItem(
              `${key2}_services_source`,
              JSON.stringify(apiServicesData2[key2])
            );
            continue;
          }
          apiServicesData2[key2] = apiServicesData[key2];
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData2[key2])
          );
        }
        const responseData: NullableAPIServicesItems = {
          internal: null,
        };
        const { ...entry } = apiServicesData[key];
        entry.status = 'failed';
        responseData[key] = entry;
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/services?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          internal: apiServicesData2.internal?.items,
        });
        expect(window.localStorage.getItem(`${key}_services_source`)).toEqual(
          JSON.stringify(apiServicesData2[key])
        );
      }
    });

    test('should get services items from API - services items entry is expired in localstorage', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        vi.clearAllMocks();
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            const entry = { ...apiServicesData[key2] };
            entry.expires_at = new Date('2025-11-01T11:59:59Z'); // expired
            window.localStorage.setItem(
              `${key2}_services_source`,
              JSON.stringify(entry)
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData[key2])
          );
        }
        const responseData: NullableAPIServicesItems = {
          internal: null,
        };
        responseData[key] = apiServicesData[key];
        const spy = vi
          .spyOn(globalThis, 'fetch')
          .mockResolvedValue(
            new Response(JSON.stringify(responseData), { status: 200 })
          );

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(spy).toHaveBeenCalledExactlyOnceWith(
          `https://localhost:8000/api/v1/users/data/services?filter-items=${key}`,
          { credentials: 'include' }
        );
        expect(result).toEqual({
          internal: apiServicesData.internal.items,
        });
        expect(window.localStorage.getItem(`${key}_services_source`)).toEqual(
          JSON.stringify(apiServicesData[key])
        );
      }
    });

    test('should get services items from API - services items entry is not expired in localstorage', async () => {
      for (const key of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
        // Given
        window.localStorage.clear();
        for (const key2 of Object.keys(apiServicesData) as APIServicesItemsKey[]) {
          if (key2 === key) {
            const entry = { ...apiServicesData[key2] };
            entry.expires_at = new Date('2025-11-01T12:00:00Z'); // not yet expired
            window.localStorage.setItem(
              `${key2}_services_source`,
              JSON.stringify(entry)
            );
            continue;
          }
          window.localStorage.setItem(
            `${key2}_services_source`,
            JSON.stringify(apiServicesData[key2])
          );
        }

        // When
        const result = await retrieveServices(new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(result).toEqual({
          internal: apiServicesData.internal.items,
        });
      }
    });
  });
});
