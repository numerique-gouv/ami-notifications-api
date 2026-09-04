import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { waitFor } from '@testing-library/svelte';
import { retrievePartners } from '$lib/api-partners';

const apiPartnersData = {
  status: 'success',
  items: [
    {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'https://fake-link-1',
    },
    {
      slug: 'dinum-dn',
      name: 'Démarche Numérique',
      link: 'https://fake-link-2',
    },
  ],
  expires_at: '2026-02-14T11:16:00Z',
};

describe('/api-partners', () => {
  describe('retrievePartners', () => {
    test('should get partners from API', async () => {
      // Given
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiPartnersData), { status: 200 })
        );

      // When
      const result = await retrievePartners();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result.length).toEqual(2);
      expect(result[0]).toEqual(apiPartnersData.items[0]);
      expect(result[1]).toEqual(apiPartnersData.items[1]);
    });
    test('should store partners to localStorage', async () => {
      // Given
      localStorage.clear();
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify(apiPartnersData), { status: 200 })
      );

      // When
      await retrievePartners();

      // Then
      const result = JSON.parse(localStorage.getItem('partners') || '[]');
      expect(result.items.length).toEqual(2);
      expect(result.items[0]).toEqual(apiPartnersData.items[0]);
      expect(result.items[1]).toEqual(apiPartnersData.items[1]);
    });

    test('should get partners items from localStorage - when fetch status code is not 200', async () => {
      // Given
      localStorage.clear();
      localStorage.setItem('partners', JSON.stringify(apiPartnersData));
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrievePartners();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result.length).toEqual(2);
      expect(result[0]).toEqual(apiPartnersData.items[0]);
      expect(result[1]).toEqual(apiPartnersData.items[1]);
    });
    test('should get partners items from localStorage - with no item when fetch status code is not 200 and localStorage is empty', async () => {
      // Given
      localStorage.clear();
      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(new Response('error', { status: 400 }));

      // When
      const result = await retrievePartners();

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result.length).toEqual(0);
    });
    test('should get partners items from localStorage - when fetch fails', async () => {
      // Given
      localStorage.clear();
      localStorage.setItem('partners', JSON.stringify(apiPartnersData));
      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Fetch failed'));

      // When
      const result = await retrievePartners();

      // Then
      expect(result.length).toEqual(2);
      expect(result[0]).toEqual(apiPartnersData.items[0]);
      expect(result[1]).toEqual(apiPartnersData.items[1]);
    });
    test('should get partners items from localStorage - with no item when fetch fails and localStorage is empty', async () => {
      // Given
      localStorage.clear();
      vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Fetch failed'));

      // When
      const result = await retrievePartners();

      // Then
      await waitFor(() => {
        expect(result.length).toEqual(0);
      });
    });

    test('should get partners items from API - when partners items entry has no data in localstorage', async () => {
      // Given
      const apiPartnersDataNoData = undefined;
      window.localStorage.setItem('partners', JSON.stringify(apiPartnersDataNoData));

      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiPartnersData), { status: 200 })
        );

      // When
      const result = await retrievePartners(new Date('2026-09-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result).toEqual(apiPartnersData.items);
      const result_stringified =
        '{"status":"success","items":[{"slug":"dinum-ami","name":"AMI","link":"https://fake-link-1"},{"slug":"dinum-dn","name":"Démarche Numérique","link":"https://fake-link-2"}],"expires_at":"2026-02-14T11:16:00Z"}';
      expect(window.localStorage.getItem('partners')).toEqual(result_stringified);
    });

    test('should get partners items from API - when partners items entry has failed status in localstorage', async () => {
      // Given
      const apiPartnersDataFailedStatus = {
        status: 'failed',
        items: [
          {
            slug: 'dinum-ami',
            name: 'AMI',
            link: 'https://fake-link-1',
          },
          {
            slug: 'dinum-dn',
            name: 'Démarche Numérique',
            link: 'https://fake-link-2',
          },
        ],
        expires_at: '2026-02-14T11:16:00Z',
      };
      window.localStorage.setItem(
        'partners',
        JSON.stringify(apiPartnersDataFailedStatus)
      );

      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiPartnersData), { status: 200 })
        );

      // When
      const result = await retrievePartners(new Date('2026-09-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result).toEqual(apiPartnersData.items);
      const result_stringified =
        '{"status":"success","items":[{"slug":"dinum-ami","name":"AMI","link":"https://fake-link-1"},{"slug":"dinum-dn","name":"Démarche Numérique","link":"https://fake-link-2"}],"expires_at":"2026-02-14T11:16:00Z"}';
      expect(window.localStorage.getItem('partners')).toEqual(result_stringified);
    });

    test('should get partners items from API - when partners items entry has no expiration date in localstorage', async () => {
      // Given
      const apiPartnersDataNoExpiration = {
        status: 'success',
        items: [
          {
            slug: 'dinum-ami',
            name: 'AMI',
            link: 'https://fake-link-1',
          },
          {
            slug: 'dinum-dn',
            name: 'Démarche Numérique',
            link: 'https://fake-link-2',
          },
        ],
        expires_at: '',
      };
      window.localStorage.setItem(
        'partners',
        JSON.stringify(apiPartnersDataNoExpiration)
      );

      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiPartnersData), { status: 200 })
        );

      // When
      const result = await retrievePartners(new Date('2026-09-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result).toEqual(apiPartnersData.items);
      const result_stringified =
        '{"status":"success","items":[{"slug":"dinum-ami","name":"AMI","link":"https://fake-link-1"},{"slug":"dinum-dn","name":"Démarche Numérique","link":"https://fake-link-2"}],"expires_at":"2026-02-14T11:16:00Z"}';
      expect(window.localStorage.getItem('partners')).toEqual(result_stringified);
    });

    test('should get partners items from API - when partners items entry has expired date in localstorage', async () => {
      // Given
      const apiPartnersDataExpiredDate = {
        status: 'success',
        items: [
          {
            slug: 'dinum-ami',
            name: 'AMI',
            link: 'https://fake-link-1',
          },
          {
            slug: 'dinum-dn',
            name: 'Démarche Numérique',
            link: 'https://fake-link-2',
          },
        ],
        expires_at: '2025-11-01T12:00:00Z',
      };
      window.localStorage.setItem(
        'partners',
        JSON.stringify(apiPartnersDataExpiredDate)
      );

      const spy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValue(
          new Response(JSON.stringify(apiPartnersData), { status: 200 })
        );

      // When
      const result = await retrievePartners(new Date('2026-09-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledExactlyOnceWith('/api/v1/users/data/partners');
      expect(result).toEqual(apiPartnersData.items);
      const result_stringified =
        '{"status":"success","items":[{"slug":"dinum-ami","name":"AMI","link":"https://fake-link-1"},{"slug":"dinum-dn","name":"Démarche Numérique","link":"https://fake-link-2"}],"expires_at":"2026-02-14T11:16:00Z"}';
      expect(window.localStorage.getItem('partners')).toEqual(result_stringified);
    });
  });
});
