import { describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { waitFor } from '@testing-library/svelte'
import * as agendaMethods from '$lib/agenda'
import { Agenda } from '$lib/agenda'
import { initializeData, initializeLocalStorage } from '$lib/initializeDataFromAPI'
import type { AppNotification } from '$lib/notifications'
import * as notificationsMethods from '$lib/notifications'
import { UserStore } from '$lib/state/User.svelte'

const buildNotifications = (): AppNotification[] => {
  return [
    {
      id: 'a2a57aea-0c3b-432f-9cff-818343af8116',
      created_at: new Date('2026-02-02T14:54:28'),
      user_id: '347f2d16-9f96-4cac-ab2e-0de04b470486',
      content_title: 'test titre 2',
      content_body: 'test message 2',
      content_icon: 'test icon 2',
      sender: 'test expéditeur 2',
      item_external_url: 'test external url 2',
      read: true,
    },
    {
      id: '3e5abfc6-79f7-4480-85e9-c364d24fdbb4',
      created_at: new Date('2026-02-02T14:54:09'),
      user_id: '347f2d16-9f96-4cac-ab2e-0de04b470486',
      content_title: 'test titre',
      content_body: 'test message',
      content_icon: 'test icon 2',
      sender: 'test expéditeur',
      item_external_url: 'test external url 2',
      read: false,
    },
  ]
}

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
      const checkLoggedInSpy = vi.spyOn(userStore, 'checkLoggedIn')
      const buildAgendaSpy = vi
        .spyOn(agendaMethods, 'buildAgenda')
        .mockResolvedValue(new Agenda())
      const notifications: AppNotification[] = buildNotifications()
      const retrieveNotificationsSpy = vi
        .spyOn(notificationsMethods, 'retrieveNotifications')
        .mockResolvedValue(notifications)

      // When
      await initializeData(searchParams, userStore)

      // Then
      expect(checkLoggedInSpy).toHaveBeenCalledTimes(1)
      expect(buildAgendaSpy).toHaveBeenCalledTimes(1)
      expect(retrieveNotificationsSpy).toHaveBeenCalledTimes(1)
    })
  })
})
