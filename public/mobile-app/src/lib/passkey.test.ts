import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import type {
  AuthenticationResponseJSON,
  RegistrationResponseJSON,
} from '@simplewebauthn/browser';
import * as simplewebauthnMethods from '@simplewebauthn/browser';
import {
  authenticateWithPasskey,
  getPasskeyStatus,
  PasskeyBreakingError,
  PasskeyError,
  PasskeyNetworkError,
  registerPasskey,
} from '$lib/passkey';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';

vi.mock('@simplewebauthn/browser', () => ({
  startRegistration: vi.fn(),
  startAuthentication: vi.fn(),
}));

describe('/passkey', () => {
  describe('registerPasskey', () => {
    test('user has to be connected', async () => {
      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).resolves.toBe(undefined);
    });
    test('should throw PasskeyError on options response error', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
        new Response(JSON.stringify({}), { status: 400 })
      );

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyNetworkError on options TypeError', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new TypeError());

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyNetworkError);
    });
    test('should throw PasskeyError on options error', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error());

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyError on startRegistration error', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
        new Response(JSON.stringify({ fake: 'option' }), { status: 200 })
      );

      vi.mocked(simplewebauthnMethods.startRegistration).mockRejectedValue(new Error());

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyError on verify response error', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ fake: 'option' }), { status: 200 })
        )
        .mockResolvedValueOnce(new Response(JSON.stringify({}), { status: 400 }));

      vi.mocked(simplewebauthnMethods.startRegistration).mockResolvedValue({
        id: 'fake-id',
      } as RegistrationResponseJSON);

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyNetworkError on verify TypeError', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ fake: 'option' }), { status: 200 })
        )
        .mockRejectedValueOnce(new TypeError());

      vi.mocked(simplewebauthnMethods.startRegistration).mockResolvedValue({
        id: 'fake-id',
      } as RegistrationResponseJSON);

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyNetworkError);
    });
    test('should throw PasskeyError on verify error', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ fake: 'option' }), { status: 200 })
        )
        .mockRejectedValueOnce(new Error());

      vi.mocked(simplewebauthnMethods.startRegistration).mockResolvedValue({
        id: 'fake-id',
      } as RegistrationResponseJSON);

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyError when user is not registered', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ fake: 'option' }), { status: 200 })
        )
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ verified: false }), { status: 200 })
        );

      vi.mocked(simplewebauthnMethods.startRegistration).mockResolvedValue({
        id: 'fake-id',
      } as RegistrationResponseJSON);

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should create a passkey', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const fetchSpy = vi
        .spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ fake: 'option' }), { status: 200 })
        )
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ verified: true }), { status: 200 })
        );

      vi.mocked(simplewebauthnMethods.startRegistration).mockResolvedValue({
        id: 'fake-id',
      } as RegistrationResponseJSON);

      // When
      const promise = registerPasskey();

      // Then
      await expect(promise).resolves.toBe(undefined);
      expect(fetchSpy).toHaveBeenCalledWith(
        '/api/v1/fi/passkey/generate-registration-options',
        {
          body: '{"displayName":"Angela Claire Louise DUBOIS"}',
          headers: { 'Content-Type': 'application/json' },
          method: 'POST',
        }
      );
      // check call is made with options returned by mocked startRegistration
      expect(fetchSpy).toHaveBeenCalledWith('/api/v1/fi/passkey/verify-registration', {
        body: '{"id":"fake-id"}',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
      });
    });
  });
  describe('authenticateWithPasskey', () => {
    test('should throw PasskeyError on options response error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{}', { status: 400 })
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyNetworkError on options TypeError', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new TypeError());

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyNetworkError);
    });
    test('should throw PasskeyError on options error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error());

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyError on startAuthentication error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{}', { status: 200 })
      );
      vi.mocked(simplewebauthnMethods.startAuthentication).mockRejectedValue(
        new Error()
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyError on verify response error with retry', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(new Response('{}', { status: 200 }))
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ retry: true }), { status: 400 })
        );
      vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
        {} as AuthenticationResponseJSON
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyBreakingError on verify response error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(new Response('{}', { status: 200 }))
        .mockResolvedValueOnce(new Response('{}', { status: 400 }));
      vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
        {} as AuthenticationResponseJSON
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyBreakingError);
    });
    test('should throw PasskeyNetworkError on verify Type', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(new Response('{}', { status: 200 }))
        .mockRejectedValueOnce(new TypeError());
      vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
        {} as AuthenticationResponseJSON
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyNetworkError);
    });
    test('should throw PasskeyError on verify error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(new Response('{}', { status: 200 }))
        .mockRejectedValueOnce(new Error());
      vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
        {} as AuthenticationResponseJSON
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should throw PasskeyError when user is not authenticated', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(new Response('{}', { status: 200 }))
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ verified: false }), { status: 200 })
        );
      vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
        {} as AuthenticationResponseJSON
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).rejects.toThrow(PasskeyError);
    });
    test('should return target url when user is authenticated', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch')
        .mockResolvedValueOnce(new Response('{}', { status: 200 }))
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({ verified: true, redirect_uri: 'fake-redirect-uri' }),
            { status: 200 }
          )
        );
      vi.mocked(simplewebauthnMethods.startAuthentication).mockResolvedValue(
        {} as AuthenticationResponseJSON
      );

      // When
      const promise = authenticateWithPasskey();

      // Then
      await expect(promise).resolves.toEqual('fake-redirect-uri');
    });
  });
  describe('getPasskeyStatus', () => {
    test('should return false on response error', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response('{}', { status: 400 })
      );

      // When
      const result = await getPasskeyStatus();

      // Then
      expect(result).toEqual({ has_passkey: false });
    });
    test('should return false', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify({ has_passkey: false }), { status: 200 })
      );

      // When
      const result = await getPasskeyStatus();

      // Then
      expect(result).toEqual({ has_passkey: false });
    });
    test('should return true', async () => {
      // Given
      vi.spyOn(globalThis, 'fetch').mockResolvedValue(
        new Response(JSON.stringify({ has_passkey: true }), { status: 200 })
      );

      // When
      const result = await getPasskeyStatus();

      // Then
      expect(result).toEqual({ has_passkey: true });
    });
  });
});
