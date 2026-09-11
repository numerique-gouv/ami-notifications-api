import { afterEach, describe, expect, test, vi } from 'vitest';
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
  afterEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

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
      expect(result[0].slug).toEqual(apiPartnersData.items[0].slug);
      expect(result[0].name).toEqual(apiPartnersData.items[0].name);
      expect(result[0].link).toEqual(apiPartnersData.items[0].link);
      expect(result[1].slug).toEqual(apiPartnersData.items[1].slug);
      expect(result[1].name).toEqual(apiPartnersData.items[1].name);
      expect(result[1].link).toEqual(apiPartnersData.items[1].link);
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
      expect(result.items[0].slug).toEqual(apiPartnersData.items[0].slug);
      expect(result.items[0].name).toEqual(apiPartnersData.items[0].name);
      expect(result.items[0].link).toEqual(apiPartnersData.items[0].link);
      expect(result.items[1].slug).toEqual(apiPartnersData.items[1].slug);
      expect(result.items[1].name).toEqual(apiPartnersData.items[1].name);
      expect(result.items[1].link).toEqual(apiPartnersData.items[1].link);
    });

    test('should get partners items from localStorage - when status code is not 200', async () => {
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
      expect(result[0].slug).toEqual(apiPartnersData.items[0].slug);
      expect(result[0].name).toEqual(apiPartnersData.items[0].name);
      expect(result[0].link).toEqual(apiPartnersData.items[0].link);
      expect(result[1].slug).toEqual(apiPartnersData.items[1].slug);
      expect(result[1].name).toEqual(apiPartnersData.items[1].name);
      expect(result[1].link).toEqual(apiPartnersData.items[1].link);
    });
    test('should get partners with no item when localStorage has no key - when status code is not 200', async () => {
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
      expect(result[0].slug).toEqual(apiPartnersData.items[0].slug);
      expect(result[0].name).toEqual(apiPartnersData.items[0].name);
      expect(result[0].link).toEqual(apiPartnersData.items[0].link);
      expect(result[1].slug).toEqual(apiPartnersData.items[1].slug);
      expect(result[1].name).toEqual(apiPartnersData.items[1].name);
      expect(result[1].link).toEqual(apiPartnersData.items[1].link);
    });
    test('should get partners with no item when localStorage has no key - when fetch fails', async () => {
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
  });
});
