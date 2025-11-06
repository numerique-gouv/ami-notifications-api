import { PUBLIC_API_URL } from '$env/static/public'
import { registerDevice, unregisterDevice } from '$lib/registration.js'

export const PUBLIC_API_WS_URL = PUBLIC_API_URL.replace('https://', 'wss://').replace(
  'http://',
  'ws://'
)

export type Notification = {
  id: string
  created_at: Date
  user_id: string
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

export const readNotification = async (
  notificationId: Number
): Promise<Notification> => {
  const userId = localStorage.getItem('user_id')
  if (userId) {
    try {
      const payload = {
        read: true,
      }
      const response = await fetch(
        `${PUBLIC_API_URL}/api/v1/users/${userId}/notification/${notificationId}/read`,
        {
          method: 'PATCH',
          body: JSON.stringify(payload),
        }
      )
      if (response.status === 200) {
        let notification = (await response.json()) as Notification
        return notification
      }
    } catch (error) {
      console.error(error)
    }
  }
}

export const notificationEventsSocket = (onmessage) => {
  const userId = localStorage.getItem('user_id')
  if (userId) {
    const ws = new WebSocket(
      `${PUBLIC_API_WS_URL}/api/v1/users/${userId}/notification/events/stream`
    )
    ws.onmessage = onmessage
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
    const pushSubscription = await subscribePush()
    return await registerDevice(pushSubscription)
  }
}

export const unsubscribePush = async (pushSubscription) => {
  try {
    const hasUnsubscribed = await pushSubscription.unsubscribe()
    if (hasUnsubscribed) {
      console.log('unsubscribed to the push manager')
    } else {
      console.log('failed to unsubscribe to the push manager')
    }
    return hasUnsubscribed
  } catch (error) {
    console.error(error)
  }
}

export const disableNotifications = async (registrationId) => {
  const permissionGranted = await Notification.requestPermission()
  const registration = await getServiceWorkerRegistration()
  if (!permissionGranted || !registration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    )
    return false
  } else {
    const pushSubscription = await registration.pushManager.getSubscription()
    if (pushSubscription) {
      console.log('unregisterDevice')
      await unregisterDevice(registrationId)
      await unsubscribePush(pushSubscription)
    }
    return pushSubscription
  }
}

const getServiceWorkerRegistration = async () => {
  return await navigator.serviceWorker.ready
}
