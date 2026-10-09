import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import * as AMINavigationMethods from '$lib/ami-navigation';
import {
  AMIBack,
  AMIBackToLastKnownURL,
  AMIGoto,
  AMIGotoUntrustedUrl,
} from '$lib/ami-navigation';
import { toastStore } from '$lib/state/toast.svelte';
import * as telemetryModule from '$lib/telemetry';
import * as urlAliasesMethods from '$lib/urlAliases';

describe('/ami-navigation', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED: 'true',
      });
    });
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'true';
    vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(false);
  });

  describe('AMIGoto', () => {
    describe('without silent-login', () => {
      test('should redirect to url - internal url', async () => {
        // Given
        const url = '/';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url);
        AMIGoto(url, false, { replaceState: true });

        // Then
        expect(spy).toHaveBeenCalledTimes(2);
        expect(spy).toHaveBeenNthCalledWith(1, '/');
        expect(spy).toHaveBeenNthCalledWith(2, '/', { replaceState: true });
      });
      test('should redirect to url - promoted internal url', async () => {
        // Given
        vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(true);
        const url = '/';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url);

        // Then
        expect(window.location.href).toBe(url);
      });
      test('should redirect to url - external url without protocol', async () => {
        // Given
        const url = '//';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url);

        // Then
        expect(spy).not.toHaveBeenCalled();
      });
      test('should redirect to url - internal url with hash', async () => {
        // Given
        const url = '/#/page';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url);
        AMIGoto(url, false, { replaceState: true });

        // Then
        expect(spy).toHaveBeenCalledTimes(2);
        expect(spy).toHaveBeenNthCalledWith(1, '/#/page');
        expect(spy).toHaveBeenNthCalledWith(2, '/#/page', { replaceState: true });
      });
      test('should redirect to url - promoted internal url with hash', async () => {
        // Given
        vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(true);
        const url = '/#/page';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url);

        // Then
        expect(window.location.href).toBe('/#/page');
      });
      test('should redirect to url - internal url without hash (api urls)', async () => {
        // Given
        const url = '/page';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url);

        // Then
        expect(window.location.href).toBe('/page');
      });
      test('should redirect to url - external url', async () => {
        // Given
        const url = 'http://external-url';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url);

        // Then
        expect(window.location.href).toBe('http://external-url/');
      });
      test('should redirect to url - not external url', async () => {
        // Given
        const url = 'javascript:alert("foobar")';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url);

        // Then
        expect(window.location.href).toBe('fake-link');
      });
    });

    describe('with silent-login', () => {
      test('should redirect to silent login page with url and hash in param', async () => {
        // Given
        const url = 'http://external-url';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '#/page',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe(
          '/silent-login-ami-fi?redirect_url=http%3A%2F%2Fexternal-url&from_hash=/page'
        );
      });
    });

    describe('with silent-login - flag disabled', () => {
      test('should redirect to url - internal url', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = '/';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url, true);
        AMIGoto(url, true, { replaceState: true });

        // Then
        expect(spy).toHaveBeenCalledTimes(2);
        expect(spy).toHaveBeenNthCalledWith(1, '/');
        expect(spy).toHaveBeenNthCalledWith(2, '/', { replaceState: true });
      });
      test('should redirect to url - promoted internal url', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(true);
        const url = '/';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe('/');
      });
      test('should redirect to url - external url without protocol', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = '//';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url, true);

        // Then
        expect(spy).not.toHaveBeenCalled();
      });
      test('should redirect to url - internal url with hash', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = '/#/page';
        const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

        // When
        AMIGoto(url, true);
        AMIGoto(url, true, { replaceState: true });

        // Then
        expect(spy).toHaveBeenCalledTimes(2);
        expect(spy).toHaveBeenNthCalledWith(1, '/#/page');
        expect(spy).toHaveBeenNthCalledWith(2, '/#/page', { replaceState: true });
      });
      test('should redirect to url - promoted internal url with hash', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(true);
        const url = '/#/page';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe('/#/page');
      });
      test('should redirect to url - internal url without hash (api urls)', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = '/page';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe('/page');
      });
      test('should redirect to url - external url', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = 'http://external-url';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe('http://external-url/');
      });
      test('should redirect to url - not external url', async () => {
        // Given
        vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SILENT_FC_ENABLED = 'false';
        const url = 'javascript:alert("foobar")';
        vi.stubGlobal('location', {
          href: 'fake-link',
          hash: '',
          origin: 'http://localhost',
        });

        // When
        AMIGoto(url, true);

        // Then
        expect(window.location.href).toBe('fake-link');
      });
    });

    describe('history', () => {
      test('should register internal url in localstorage', async () => {
        // When
        AMIGoto('/#/page');

        // Then
        expect(localStorage.getItem('last_visited_internal_url')).toEqual('/#/page');
      });
      test('should register promoted internal url in localstorage', async () => {
        // Given
        vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(true);

        // When
        AMIGoto('/#/page');

        // Then
        expect(localStorage.getItem('last_visited_internal_url')).toEqual('/#/page');
      });
      test('should not register internal url in localstorage as url is excluded from history', async () => {
        // When
        AMIGoto('/#/login');

        // Then
        expect(localStorage.getItem('last_visited_internal_url')).toEqual(null);
      });
      test('should not register external url in localstorage', async () => {
        // When
        AMIGoto('http://external-url');

        // Then
        expect(localStorage.getItem('last_visited_internal_url')).toEqual(null);
      });
      test('should register last visited url as target in localstorage when redirecting to an external url', async () => {
        // Given
        localStorage.setItem('last_visited_internal_url', '/#/page');

        // When
        AMIGoto('http://external-url');

        // Then
        expect(localStorage.getItem('webview_back_target')).toEqual(
          JSON.stringify({ url: '/#/page', historyLength: 1 })
        );
      });
      test('should register / as target in localstorage when redirecting to an external url, as last visited url is unknown', async () => {
        // When
        AMIGoto('http://external-url');

        // Then
        expect(localStorage.getItem('webview_back_target')).toEqual(
          JSON.stringify({ url: '/', historyLength: 1 })
        );
      });
      test('should not register target in localstorage when redirecting to an internal url', async () => {
        // When
        AMIGoto('/#/page');

        // Then
        expect(localStorage.getItem('webview_back_target')).toEqual(null);
      });
      test('should not register target in localstorage when redirecting to a promoted internal url', async () => {
        // Given
        vi.spyOn(urlAliasesMethods, 'isPromotedUrl').mockReturnValue(true);

        // When
        AMIGoto('/#/page');

        // Then
        expect(localStorage.getItem('webview_back_target')).toEqual(null);
      });
    });
  });

  describe('AMIGotoUntrustedUrl', () => {
    test('should go to URL if no trusted URLs are defined', () => {
      // Given
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      vi.mocked(envModule).PUBLIC_TRUSTED_URLS = '';

      // When
      AMIGotoUntrustedUrl('https://www.example.net/test');

      // Then
      expect(spyAMIGoto).toHaveBeenCalledWith('https://www.example.net/test');
    });
    test('should go to URL if trusted URL', () => {
      // Given
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      vi.mocked(envModule).PUBLIC_TRUSTED_URLS =
        '.*\\.example\\.org\n.*\\.example\\.net';

      // When
      AMIGotoUntrustedUrl('https://www.example.net/test');

      // Then
      expect(spyAMIGoto).toHaveBeenCalledWith('https://www.example.net/test');
    });
    test('should go to URL if trusted URL even if defined with leading/trailing spaces', () => {
      // Given
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      vi.mocked(envModule).PUBLIC_TRUSTED_URLS =
        '.*\\.example\\.org\n  .*\\.example\\.net   ';

      // When
      AMIGotoUntrustedUrl('https://www.example.net/test');

      // Then
      expect(spyAMIGoto).toHaveBeenCalledWith('https://www.example.net/test');
    });
    test('should go to home with an error if not trusted URL', () => {
      // Given
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      const spyToast = vi.spyOn(toastStore, 'addToast');
      const spyTelemetryError = vi.spyOn(telemetryModule, 'error');
      vi.mocked(envModule).PUBLIC_TRUSTED_URLS =
        '.*\\.example\\.org\n.*\\.example\\.net';

      // When
      AMIGotoUntrustedUrl('https://www.example.com/test');

      // Then
      expect(spyAMIGoto).toHaveBeenCalledWith('/');
      expect(spyToast).toHaveBeenCalled();
      expect(spyTelemetryError).toHaveBeenCalled();
    });
    test('should go to home with an error if not trusted URL if there are blank lines', () => {
      // Given
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      const spyToast = vi.spyOn(toastStore, 'addToast');
      const spyTelemetryError = vi.spyOn(telemetryModule, 'error');
      vi.mocked(envModule).PUBLIC_TRUSTED_URLS =
        '.*\\.example\\.org\n\n.*\\.example\\.net';

      // When
      AMIGotoUntrustedUrl('https://www.example.com/test');

      // Then
      expect(spyAMIGoto).toHaveBeenCalledWith('/');
      expect(spyToast).toHaveBeenCalled();
      expect(spyTelemetryError).toHaveBeenCalled();
    });
  });

  describe('AMIBack', () => {
    test('Should call history.back if history', () => {
      // Given
      const spyBack = vi.spyOn(window.history, 'back').mockImplementation(() => {});
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      Object.defineProperty(window.history, 'length', { value: 2, configurable: true });

      // When
      AMIBack('/#/page');

      // Then
      expect(spyBack).toHaveBeenCalled();
      expect(spyAMIGoto).not.toHaveBeenCalled();
    });

    test('Should call AMIGoto if no history', () => {
      // Given
      const spyBack = vi.spyOn(window.history, 'back').mockImplementation(() => {});
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      Object.defineProperty(window.history, 'length', { value: 1, configurable: true });

      // When
      AMIBack('/#/page');

      // Then
      expect(spyBack).not.toHaveBeenCalled();
      expect(spyAMIGoto).toHaveBeenCalledWith('/#/page');
    });
  });

  describe('AMIBackToLastKnownURL', () => {
    test('Should go to home if not target in localstorage', () => {
      // Given
      const spyGo = vi.spyOn(window.history, 'back').mockImplementation(() => {});
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});

      // When
      AMIBackToLastKnownURL();

      // Then
      expect(spyGo).not.toHaveBeenCalled();
      expect(spyAMIGoto).toHaveBeenCalledWith('/', false, { replaceState: true });
    });
    test('Should go to home if target is invalid', () => {
      // Given
      localStorage.setItem('webview_back_target', 'invalid');
      const spyGo = vi.spyOn(window.history, 'back').mockImplementation(() => {});
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});

      // When
      AMIBackToLastKnownURL();

      // Then
      expect(spyGo).not.toHaveBeenCalled();
      expect(spyAMIGoto).toHaveBeenCalledWith('/', false, { replaceState: true });
      expect(localStorage.getItem('webview_back_target')).toEqual(null);
    });
    test('Should go to last visited url if history step is wrong', () => {
      // Given
      localStorage.setItem(
        'webview_back_target',
        JSON.stringify({ url: '/#/page', historyLength: 2 })
      );
      const spyGo = vi.spyOn(window.history, 'go').mockImplementation(() => {});
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      Object.defineProperty(window.history, 'length', { value: 2, configurable: true });

      // When
      AMIBackToLastKnownURL();

      // Then
      expect(spyGo).not.toHaveBeenCalled();
      expect(spyAMIGoto).toHaveBeenCalledWith('/#/page', false, { replaceState: true });
      expect(localStorage.getItem('webview_back_target')).toEqual(null);
    });
    test('Should call history.go', () => {
      // Given
      localStorage.setItem(
        'webview_back_target',
        JSON.stringify({ url: '/#/page', historyLength: 2 })
      );
      const spyGo = vi.spyOn(window.history, 'go').mockImplementation(() => {});
      const spyAMIGoto = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => {});
      Object.defineProperty(window.history, 'length', { value: 3, configurable: true });

      // When
      AMIBackToLastKnownURL();

      // Then
      expect(spyGo).toHaveBeenCalledWith(-1);
      expect(spyAMIGoto).not.toHaveBeenCalled();
      expect(localStorage.getItem('webview_back_target')).toEqual(null);
    });
  });
});
