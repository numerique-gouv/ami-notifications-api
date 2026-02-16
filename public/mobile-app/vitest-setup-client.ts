import '@testing-library/jest-dom/vitest';
import { beforeEach, type Mock, vi } from 'vitest';
import {
  PUBLIC_API_GEO_CITY_QUERY_BASE_URL,
  PUBLIC_API_GEO_COUNTRY_QUERY_BASE_URL,
} from '$env/static/public';

const fetchSpy = (): Mock => {
  return vi
    .spyOn(globalThis, 'fetch')
    .mockImplementation((input: RequestInfo | URL) => {
      const url =
        typeof input === 'string'
          ? input
          : input instanceof URL
            ? input.href
            : input.url;

      // Mock geo.api.gouv.fr for birthplace
      if (url.includes(PUBLIC_API_GEO_CITY_QUERY_BASE_URL)) {
        return Promise.resolve(
          new Response(JSON.stringify({ nom: 'Paris' }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }

      // Mock tabular-api.data.gouv.fr for birthcountry
      if (url.includes(PUBLIC_API_GEO_COUNTRY_QUERY_BASE_URL)) {
        return Promise.resolve(
          new Response(JSON.stringify({ data: [{ LIBCOG: 'France' }] }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
          })
        );
      }

      // Default fallback
      return Promise.resolve(
        new Response(JSON.stringify({}), {
          status: 404,
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
};

beforeEach(() => {
  window.localStorage?.clear();

  globalThis.fetchSpy = fetchSpy();
});

// required for svelte5 + jsdom as jsdom does not support matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  enumerable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
