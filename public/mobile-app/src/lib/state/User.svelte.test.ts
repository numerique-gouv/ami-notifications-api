import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import '@testing-library/jest-dom/vitest'
import * as franceConnectHelpers from '$lib/france-connect'
import { User, userStore } from '$lib/state/User.svelte'
import * as authHelpers from '$lib/auth'

describe('/lib/state/User.svelte.ts', () => {
  test('should login a user', async () => {
    // Given
    const userinfo = {
      sub: 'fake sub',
      given_name: 'Angela Claire Louise',
      given_name_array: ['Angela', 'Claire', 'Louise'],
      family_name: 'DUBOIS',
      email: 'some@email.com',
      birthdate: '1962-08-24',
      birthcountry: '99100',
      birthplace: '75100',
      gender: 'female',
      aud: 'fake aud',
      exp: 1753877658,
      iat: 1753877598,
      iss: 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2',
    }
    const spyUpdateIdentity = vi
      .spyOn(User.prototype, 'updateIdentity')
      .mockResolvedValue()

    // When
    await userStore.login(userinfo)

    // Then
    expect(userStore.connected).not.toBeNull()
    expect(userStore.isConnected()).toEqual(true)
    expect(userStore.connected?.pivot?.given_name).toEqual(userinfo.given_name)
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
})
