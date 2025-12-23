import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { Address } from '$lib/address'
import * as authHelpers from '$lib/auth'
import * as franceConnectHelpers from '$lib/france-connect'
import { User, userStore } from '$lib/state/User.svelte'
import { mockUser, mockUserIdentity, mockUserInfo } from '$tests/utils'
import { fetchSpy } from '../../../vitest-setup-client'

describe('/lib/state/User.svelte.ts', () => {
  beforeEach(() => {
    userStore.connected = null
  })

  afterEach(() => {
    // Don't use restoreAllMocks - it would remove the fetchSpy from setup file
    // Instead, restore only the mocks created in individual tests
    vi.clearAllMocks()
  })

  test('should login a user', async () => {
    // Given
    const spyUpdateIdentity = vi
      .spyOn(User.prototype, 'updateIdentity')
      .mockResolvedValue()

    // When
    await userStore.login(mockUserInfo)

    // Then
    expect(userStore.connected).toBeTruthy()
    expect(userStore.connected?.pivot?.given_name).toEqual(mockUserInfo.given_name)

    // Cleanup
    spyUpdateIdentity.mockRestore()
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
    expect(localStorage.getItem('user_identity')).toBeNull()
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
    expect(userStore.connected).not.toBeTruthy()
    const isLoggedIn = userStore.checkLoggedIn()

    // Then
    expect(isLoggedIn).toBeTruthy()
    expect(spyParseJwt).toHaveBeenCalledWith('some data')
    expect(userStore.connected?.identity?.address).toBeUndefined() // No `user_identity` in the localStorage
  })

  test("should detect that we're not logged in", async () => {
    // Given
    localStorage.removeItem('user_data')

    // When
    userStore.checkLoggedIn()

    // Then
    expect(userStore.connected).not.toBeTruthy()
  })

  test('should reconstruct a user identity from localstorage', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

    // When
    await userStore.login(mockUserInfo)

    // Then
    expect(userStore.connected?.identity?.address).toEqual(mockUserIdentity.address)
    expect(userStore.connected?.identity?.address instanceof Address).toBe(true)
  })

  test('should properly set an email on the identity and save the identity to localStorage', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

    // When
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()
    userStore.connected!.setEmail('foo@bar.com')

    // Then
    expect(userStore.connected?.identity?.email).toEqual('foo@bar.com')
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
    expect(parsed?.email).toEqual('foo@bar.com')
  })

  test('should not allow setting an empty email on the identity', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

    // When
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()
    expect(userStore.connected?.identity?.email).toEqual('wossewodda-3728@yopmail.com')
    userStore.connected!.setEmail('')

    // Then
    expect(userStore.connected?.identity?.email).toEqual('wossewodda-3728@yopmail.com')
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
    expect(parsed?.email).toEqual('wossewodda-3728@yopmail.com')
  })

  test('should properly set a preferred username on the identity and save the identity to localStorage', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

    // When
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()
    userStore.connected!.setPreferredUsername('Dupont')

    // Then
    expect(userStore.connected?.identity?.preferred_username).toEqual('Dupont')
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
    expect(parsed?.preferred_username).toEqual('Dupont')
  })

  test('should properly set an empty preferred username on the identity and save the identity to localStorage', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

    // When
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()
    userStore.connected!.setPreferredUsername('Dupont')
    expect(userStore.connected?.identity?.preferred_username).toEqual('Dupont')
    userStore.connected!.setPreferredUsername('')

    // Then
    expect(userStore.connected?.identity?.preferred_username).toBeUndefined()
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
    expect(parsed?.preferred_username).toBeUndefined()
  })

  test('should properly set an address on the identity and save the identity to localStorage', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
    const otherAddress = new Address('some random city')

    // When
    await userStore.login(mockUserInfo)
    expect(userStore.connected).not.toBeNull()
    userStore.connected!.setAddress(otherAddress)

    // Then
    expect(userStore.connected?.identity?.address?.city).toEqual('some random city')
    const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
    expect(parsed?.address._city).toEqual('some random city')
  })

  test('should not query the geo API to update the identity if it was loaded from localStorage', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

    // When
    await userStore.login(mockUserInfo)

    // Then
    expect(fetchSpy).not.toHaveBeenCalled()
  })

  test("should query the geo API to update the identity if it didn't have the birthplace and birthcountry", async () => {
    // Given
    localStorage.removeItem('user_identity')

    // When
    await userStore.login(mockUserInfo)

    // Then
    const mockCalls = fetchSpy.mock.calls // An array of calls, each call being [url, options]
    expect(mockCalls[0][0]).toContain('geo.api.gouv.fr')
    expect(mockCalls[0][0]).toContain(mockUserInfo.birthplace)
    expect(mockCalls[1][0]).toContain('tabular-api.data.gouv.fr')
    expect(mockCalls[1][0]).toContain(mockUserInfo.birthcountry)
  })
  describe('User', () => {
    describe('getInitials', () => {
      test('should display initial of firt given name element only', async () => {
        // When
        const initials = mockUser.getInitials()

        // Then
        expect(initials).toEqual('A')
      })
    })
  })
})
