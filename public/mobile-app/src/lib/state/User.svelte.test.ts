import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import * as franceConnectHelpers from '$lib/france-connect'
import { User, userStore } from '$lib/state/User.svelte'
import * as authHelpers from '$lib/auth'
import { mockUserInfo } from '../../../tests/utils'

describe('/lib/state/User.svelte.ts', () => {
  test('should login a user', async () => {
    // Given
    const spyUpdateIdentity = vi
      .spyOn(User.prototype, 'updateIdentity')
      .mockResolvedValue()

    // When
    await userStore.login(mockUserInfo)

    // Then
    expect(userStore.connected).not.toBeNull()
    expect(userStore.isConnected()).toEqual(true)
    expect(userStore.connected?.pivot?.given_name).toEqual(mockUserInfo.given_name)
  })

  test('should logout a user from AMI then from FC', async () => {
    // Given
    globalThis.localStorage.setItem('id_token', 'fake-id-token')
    const spyAuthLogout = vi.spyOn(authHelpers, 'logout').mockResolvedValue(true)
    const spyFranceConnectLogout = vi
      .spyOn(franceConnectHelpers, 'franceConnectLogout')
      .mockResolvedValue()

    // When
    await userStore.logout()

    // Then
    expect(localStorage.getItem('id_token')).toBeNull()
    expect(spyAuthLogout).toHaveBeenCalled()
    expect(spyFranceConnectLogout).toHaveBeenCalledWith('fake-id-token')
  })

  test("should detect that we're already logged in", async () => {
    // Given
    localStorage.setItem('user_data', 'some data')
    const spyParseJwt = vi
      .spyOn(franceConnectHelpers, 'parseJwt')
      .mockReturnValue(mockUserInfo)

    // When
    expect(userStore.isConnected()).not.toBeTruthy()
    const isLoggedIn = userStore.checkLoggedIn()

    // Then
    expect(isLoggedIn).toBeTruthy()
    expect(spyParseJwt).toHaveBeenCalledWith('some data')
  })

  test("should detect that we're not logged in", async () => {
    // Given
    localStorage.removeItem('user_data')

    // When
    userStore.checkLoggedIn()

    // Then
    expect(userStore.isConnected()).not.toBeTruthy()
  })
})
