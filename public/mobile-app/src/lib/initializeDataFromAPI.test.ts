import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { waitFor } from '@testing-library/svelte'
import { initializeData, initializeLocalStorage } from '$lib/initializeDataFromAPI'
import { UserStore } from '$lib/state/User.svelte'

describe('/initializeDataFromAPI.ts', () => {
  describe('initializeLocalStorage', () => {
    test('should set items in localStorage from url search params', async () => {
      // Given
      window.localStorage.setItem('user_data', '')
      window.localStorage.setItem('user_id', '')
      window.localStorage.setItem('user_fc_hash', '')
      window.localStorage.setItem('user_api_particulier_encoded_address', '')

      const searchParams = new URLSearchParams({
        is_logged_in: 'true',
        id_token: 'fake-id-token',
        user_data: 'fake-user-data',
        user_fc_hash: 'fake-user-fc-hash',
        address: 'fake-address',
      })

      // When
      await initializeLocalStorage(searchParams)

      // Then
      await waitFor(async () => {
        expect(window.localStorage.getItem('is_logged_in')).toEqual('true')
        expect(window.localStorage.getItem('id_token')).toEqual('fake-id-token')
        expect(window.localStorage.getItem('user_data')).toEqual('fake-user-data')
        expect(window.localStorage.getItem('user_fc_hash')).toEqual('fake-user-fc-hash')
        expect(
          window.localStorage.getItem('user_api_particulier_encoded_address')
        ).toEqual('fake-address')
      })
    })
  })

  describe('initializeData', () => {
    test('should call dedicated methods to initialize data', async () => {
      // Given
      const searchParams = new URLSearchParams({})

      const userStore = new UserStore()
      const spy = vi.spyOn(userStore, 'checkLoggedIn')

      // When
      await initializeData(searchParams, userStore)

      // Then
      expect(spy).toHaveBeenCalledTimes(1)
    })
  })
})
