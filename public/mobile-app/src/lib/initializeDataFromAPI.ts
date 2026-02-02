import { buildAgenda } from '$lib/agenda'
import type { AppNotification } from '$lib/notifications'
import { retrieveNotifications } from '$lib/notifications'
import type { UserStore } from '$lib/state/User.svelte'

export const initializeLocalStorage = async (searchParams: URLSearchParams) => {
  localStorage.setItem('is_logged_in', searchParams.get('is_logged_in') || '')
  localStorage.setItem('id_token', searchParams.get('id_token') || '')
  localStorage.setItem('user_data', searchParams.get('user_data') || '')
  localStorage.setItem('user_fc_hash', searchParams.get('user_fc_hash') || '')
  localStorage.setItem(
    'user_api_particulier_encoded_address',
    searchParams.get('address') || ''
  )
}

export const initializeData = async (
  searchParams: URLSearchParams,
  userStore: UserStore
) => {
  await initializeLocalStorage(searchParams)
  await userStore.checkLoggedIn()
  await buildAgenda()

  let notifications: AppNotification[] = []
  notifications = await retrieveNotifications()
  localStorage.setItem('notifications', notifications.toString())
  const unreadNotifications: AppNotification[] = notifications.filter(
    (notification) => !notification.read
  )
  localStorage.setItem(
    'unreadNotificationsCount',
    unreadNotifications.length.toString()
  )
}
