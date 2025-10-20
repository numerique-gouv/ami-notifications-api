import { PUBLIC_API_URL } from '$env/static/public'
import { registerUser } from '$lib/registration.js'

export type Notification = {
  id: number
  date: Date
  user_id: number
  message: string
  sender?: string
  title?: string
  unread: boolean
}

export const retrieveNotifications = async (): Promise<Notification[]> => {
  let notifications = [] as Notification[]
  const userId = localStorage.getItem('user_id')
  if (userId) {
    try {
      const response = await fetch(
        `${PUBLIC_API_URL}/api/v1/users/${userId}/notifications`
      )
      if (response.status === 200) {
        notifications = await response.json()
      }
    } catch (error) {
      console.error(error)
    }
  }
  console.log('notifications', notifications)
  return notifications
}

export const countUnreadNotifications = async (): Number => {
  let notifications = [] as Notification[]
  const userId = localStorage.getItem('user_id')
  if (userId) {
    try {
      const response = await fetch(
        `${PUBLIC_API_URL}/api/v1/users/${userId}/notifications?unread=true`
      )
      if (response.status === 200) {
        notifications = await response.json()
      }
    } catch (error) {
      console.error(error)
    }
  }
  return notifications.length
}

export const getSubscription = async () => {
  console.log("refreshing the push subscription, if it's there")
  const registration = await getServiceWorkerRegistration()
  if (registration) {
    const pushSubscription = await registration.pushManager.getSubscription()
    console.log('refreshed subscription:', pushSubscription)
    return pushSubscription
  }
}

export const subscribePush = async () => {
  const registration = await getServiceWorkerRegistration()
  try {
    const applicationKeyResponse = await fetch(`${PUBLIC_API_URL}/notification-key`)
    const applicationKey = await applicationKeyResponse.text()
    const options = { userVisibleOnly: true, applicationServerKey: applicationKey }
    const pushSubscription = await registration.pushManager.subscribe(options)
    console.log('pushSubscription:', pushSubscription)
    console.log('subscribed to the push manager')
    return pushSubscription
  } catch (error) {
    console.error(error)
  }
}

export const enableNotifications = async () => {
  const permissionGranted = await Notification.requestPermission()
  const registration = await getServiceWorkerRegistration()
  if (!permissionGranted || !registration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    )
  } else {
    await registerUser()
  }
}

const getServiceWorkerRegistration = async () => {
  return await navigator.serviceWorker.ready
}
