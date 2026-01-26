import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { Address } from '$lib/address'
import * as addressesFromBANMethods from '$lib/addressesFromBAN'
import { AddressFromBAN } from '$lib/addressesFromBAN'
import * as authHelpers from '$lib/auth'
import * as franceConnectHelpers from '$lib/france-connect'
import { User, userStore } from '$lib/state/User.svelte'
import { mockUser, mockUserIdentity, mockUserInfo } from '$tests/utils'

describe('/lib/state/User.svelte.ts', () => {
  beforeEach(() => {
    userStore.connected = null
  })

  afterEach(() => {
    // Don't use restoreAllMocks - it would remove the fetchSpy from setup file
    // Instead, restore only the mocks created in individual tests
    vi.clearAllMocks()
  })

  describe('UserStore', () => {
    describe('login', () => {
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
      test('should reconstruct a user identity from localstorage', async () => {
        // Given
        const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
        newMockUserIdentity.preferred_username = 'CUSTOM'
        newMockUserIdentity.email = 'custom@email.com'
        localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))

        // When
        await userStore.login(mockUserInfo)

        // Then
        expect(userStore.connected?.identity?.preferred_username).toEqual('CUSTOM')
        expect(userStore.connected?.identity?.email).toEqual('custom@email.com')
      })
      test('should reconstruct a user identity from localstorage - with user address', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        const spySetAddressFromAPIParticulier = vi
          .spyOn(User.prototype, 'setAddressFromAPIParticulier')
          .mockResolvedValue()

        // When
        await userStore.login(mockUserInfo)

        // Then
        expect(spySetAddressFromAPIParticulier).not.toHaveBeenCalled()
        expect(userStore.connected?.identity?.address).toEqual(mockUserIdentity.address)
        expect(userStore.connected?.identity?.address instanceof Address).toBe(true)

        // Cleanup
        spySetAddressFromAPIParticulier.mockRestore()
      })
      test('should reconstruct a user identity from localstorage - with api-particulier address', async () => {
        // Given
        const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
        newMockUserIdentity.dataDetails.address.origin = 'api-particulier'
        localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
        const spySetAddressFromAPIParticulier = vi
          .spyOn(User.prototype, 'setAddressFromAPIParticulier')
          .mockResolvedValue()

        // When
        await userStore.login(mockUserInfo)

        // Then
        expect(spySetAddressFromAPIParticulier).not.toHaveBeenCalled()

        // Cleanup
        spySetAddressFromAPIParticulier.mockRestore()
      })
      test('should reconstruct a user identity from localstorage - with cleared address', async () => {
        // Given
        const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
        newMockUserIdentity.dataDetails.address.origin = 'cleared'
        localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
        const spySetAddressFromAPIParticulier = vi
          .spyOn(User.prototype, 'setAddressFromAPIParticulier')
          .mockResolvedValue()

        // When
        await userStore.login(mockUserInfo)

        // Then
        expect(spySetAddressFromAPIParticulier).not.toHaveBeenCalled()

        // Cleanup
        spySetAddressFromAPIParticulier.mockRestore()
      })
      test('should reconstruct a user identity from localstorage - with empty address', async () => {
        // Given
        const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity))
        newMockUserIdentity.dataDetails.address.origin = undefined
        localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity))
        const spySetAddressFromAPIParticulier = vi
          .spyOn(User.prototype, 'setAddressFromAPIParticulier')
          .mockResolvedValue()

        // When
        await userStore.login(mockUserInfo)

        // Then
        expect(spySetAddressFromAPIParticulier).toHaveBeenCalled()

        // Cleanup
        spySetAddressFromAPIParticulier.mockRestore()
      })
      test('should not query the geo API to update the identity if it was loaded from localStorage', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

        // When
        await userStore.login(mockUserInfo)

        // Then
        // @ts-expect-error
        expect(globalThis.fetchSpy).not.toHaveBeenCalled()
      })
      test("should query the geo API to update the identity if it didn't have the birthplace and birthcountry", async () => {
        // Given
        localStorage.removeItem('user_identity')

        // When
        await userStore.login(mockUserInfo)

        // Then
        // @ts-expect-error
        expect(globalThis.fetchSpy).toHaveBeenCalledTimes(2)
        // @ts-expect-error
        expect(globalThis.fetchSpy).toHaveBeenNthCalledWith(
          1,
          'https://geo.api.gouv.fr/communes/75100?fields=nom&format=json'
        )
        // @ts-expect-error
        expect(globalThis.fetchSpy).toHaveBeenNthCalledWith(
          2,
          'https://tabular-api.data.gouv.fr/api/resources/3580bf65-1d11-4574-a2ca-903d64ad41bd/data/?page=1&page_size=20&COG__exact=99100'
        )
      })
    })

    describe('logout', () => {
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
    })

    describe('checkLoggedIn', () => {
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
        expect(
          userStore.connected?.identity?.dataDetails.address.origin
        ).toBeUndefined() // No `user_identity` in the localStorage
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined() // No `user_identity` in the localStorage
        expect(
          userStore.connected?.identity?.dataDetails.preferred_username.origin
        ).toBeUndefined() // No `user_identity` in the localStorage
        expect(
          userStore.connected?.identity?.dataDetails.preferred_username.lastUpdate
        ).toBeUndefined() // No `user_identity` in the localStorage
        expect(userStore.connected?.identity?.dataDetails.email.origin).toBeUndefined() // No `user_identity` in the localStorage
        expect(
          userStore.connected?.identity?.dataDetails.email.lastUpdate
        ).toBeUndefined() // No `user_identity` in the localStorage
      })
      test("should detect that we're not logged in", async () => {
        // Given
        localStorage.removeItem('user_data')

        // When
        userStore.checkLoggedIn()

        // Then
        expect(userStore.connected).not.toBeTruthy()
      })
    })
  })

  describe('User', () => {
    describe('setEmail', () => {
      test('should properly set an email on the identity and save the identity to localStorage', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        userStore.connected!.setEmail('foo@bar.com')

        // Then
        expect(userStore.connected?.identity?.email).toEqual('foo@bar.com')
        expect(userStore.connected?.identity?.dataDetails.email.origin).toEqual('user')
        expect(
          userStore.connected?.identity?.dataDetails.email.lastUpdate
        ).not.toBeUndefined()
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
        expect(parsed?.email).toEqual('foo@bar.com')
        expect(parsed?.dataDetails.email.origin).toEqual('user')
        expect(parsed?.dataDetails.email.lastUpdate).not.toBeUndefined()
      })
      test('should not allow setting an empty email on the identity', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        expect(userStore.connected?.identity?.email).toEqual(
          'wossewodda-3728@yopmail.com'
        )
        userStore.connected!.setEmail('')

        // Then
        expect(userStore.connected?.identity?.email).toEqual(
          'wossewodda-3728@yopmail.com'
        )
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
        expect(parsed?.email).toEqual('wossewodda-3728@yopmail.com')
        expect(parsed?.dataDetails.email.origin).toEqual('user')
        expect(parsed?.dataDetails.email.lastUpdate).toBeUndefined()
      })
    })

    describe('setPreferredUsername', () => {
      test('should properly set a preferred username on the identity and save the identity to localStorage', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        userStore.connected!.setPreferredUsername('Dupont')

        // Then
        expect(userStore.connected?.identity?.preferred_username).toEqual('Dupont')
        expect(
          userStore.connected?.identity?.dataDetails.preferred_username.origin
        ).toEqual('user')
        expect(
          userStore.connected?.identity?.dataDetails.preferred_username.lastUpdate
        ).not.toBeUndefined()
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
        expect(parsed?.preferred_username).toEqual('Dupont')
        expect(parsed?.dataDetails.preferred_username.origin).toEqual('user')
        expect(parsed?.dataDetails.preferred_username.lastUpdate).not.toBeUndefined()
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
        expect(parsed?.dataDetails.preferred_username.origin).toEqual('cleared')
        expect(parsed?.dataDetails.preferred_username.lastUpdate).not.toBeUndefined()
      })
    })

    describe('setAddress', () => {
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
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).not.toBeUndefined()
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}')
        expect(parsed?.address._city).toEqual('some random city')
        expect(parsed?.dataDetails.address.origin).toEqual('user')
        expect(parsed?.dataDetails.address.lastUpdate).not.toBeUndefined()
      })
    })

    describe('setAddressFromAPIParticulier', () => {
      test('should not call BAN if address from api-particulier is not set', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem('user_api_particulier_encoded_address', '')

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        // @ts-expect-error
        expect(globalThis.fetchSpy).not.toHaveBeenCalled()
        expect(userStore.connected?.identity?.address?.city).toEqual('Paris')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined()
      })
      test('should not call BAN if address from api-particulier is not base64 encoded', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem('user_api_particulier_encoded_address', 'wrong')

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        // @ts-expect-error
        expect(globalThis.fetchSpy).not.toHaveBeenCalled()
        expect(userStore.connected?.identity?.address?.city).toEqual('Paris')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined()
      })
      test('should not call BAN if address from api-particulier is not a json base64 encoded', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem('user_api_particulier_encoded_address', btoa('wrong'))

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        // @ts-expect-error
        expect(globalThis.fetchSpy).not.toHaveBeenCalled()
        expect(userStore.connected?.identity?.address?.city).toEqual('Paris')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined()
      })
      test('should not call BAN if address from api-particulier is an empty json base64 encoded', async () => {
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem('user_api_particulier_encoded_address', btoa('{}'))

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        // @ts-expect-error
        expect(globalThis.fetchSpy).not.toHaveBeenCalled()
        expect(userStore.connected?.identity?.address?.city).toEqual('Paris')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined()
      })
      test('should not set address if BAN returns an error', async () => {
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem(
          'user_api_particulier_encoded_address',
          btoa(JSON.stringify({ code_postal_ville: '31000 TOULOUSE' }))
        )
        const spy = vi.spyOn(addressesFromBANMethods, 'callBAN').mockResolvedValue({
          errorCode: 'code',
          errorMessage: 'message',
        })

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        expect(spy).toHaveBeenCalledTimes(1)
        expect(userStore.connected?.identity?.address?.city).toEqual('Paris')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined()
      })
      test('should not set address if BAN returns an empty list', async () => {
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem(
          'user_api_particulier_encoded_address',
          btoa(JSON.stringify({ code_postal_ville: '31000 TOULOUSE' }))
        )
        const spy = vi.spyOn(addressesFromBANMethods, 'callBAN').mockResolvedValue({
          results: [],
        })

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        expect(spy).toHaveBeenCalledTimes(1)
        expect(userStore.connected?.identity?.address?.city).toEqual('Paris')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'user'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).toBeUndefined()
      })
      test('should set address if BAN returns results', async () => {
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
        localStorage.setItem(
          'user_api_particulier_encoded_address',
          btoa(
            JSON.stringify({
              numero_libelle_voie: '23 Rue des Aubépines',
              code_postal_ville: '45100 ORLÉANS',
            })
          )
        )
        const spy = vi.spyOn(addressesFromBANMethods, 'callBAN').mockResolvedValue({
          results: [
            new AddressFromBAN(
              'Orléans',
              '45, Loiret, Centre-Val de Loire',
              '45234_0420_00023',
              '23 Rue des Aubépines 45100 Orléans',
              '23 Rue des Aubépines',
              '45100'
            ),
            new AddressFromBAN(
              'Orly',
              '94, Val-de-Marne, Île-de-France',
              '94054_0070_00023',
              '23 Rue des Aubépines 94310 Orly',
              '23 Rue des Aubépines',
              '94310'
            ),
            new AddressFromBAN(
              'Orléat',
              '63, Puy-de-Dôme, Auvergne-Rhône-Alpes',
              '63265_0008',
              'Allée des Aubépines 63190 Orléat',
              'Allée des Aubépines',
              '63190'
            ),
          ],
        })

        // When
        await userStore.login(mockUserInfo)
        expect(userStore.connected).not.toBeNull()
        await userStore.connected!.setAddressFromAPIParticulier()

        // Then
        expect(spy).toHaveBeenCalledTimes(1)
        expect(userStore.connected?.identity?.address?.city).toEqual('Orléans')
        expect(userStore.connected?.identity?.dataDetails.address.origin).toEqual(
          'api-particulier'
        )
        expect(
          userStore.connected?.identity?.dataDetails.address.lastUpdate
        ).not.toBeUndefined()
      })
    })

    describe('formatBirthdate', () => {
      test('should format birthdate to MM/DD/YYYY format', async () => {
        // Given
        const birthdateFromUserinfo = '1962-08-24'

        // When
        const formattedBirthdate = mockUser.formatBirthdate(birthdateFromUserinfo)

        // Then
        expect(formattedBirthdate).toEqual('24/08/1962')
      })
    })

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
