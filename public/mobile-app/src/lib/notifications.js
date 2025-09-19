import { PUBLIC_API_URL } from '$env/static/public'

export const retrieveNotifications = async () => {
  let messages = []
  const userId = localStorage.getItem('user_id')
  if (userId) {
    try {
      const response = await fetch(
        `${PUBLIC_API_URL}/api/v1/users/${userId}/notifications`
      )
      if (response.status === 200) {
        messages = await response.json()
        console.log('messages', messages)
        return messages
      }
    } catch (error) {
      console.error(error)
    }
  }
}

export const getSubscription = async () => {
  console.log("refreshing the push subscription, if it's there")
  const registration = await getServiceWorkerRegistration()
  if (registration) {
    const sub = await registration.pushManager.getSubscription()
    console.log('refreshed subscription:', sub)
    return sub
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

export const registerUser = async () => {
  const pushSubscription = await subscribePush()

  const pushSubURL = pushSubscription.endpoint
  const pushSubAuth = pushSubscription.toJSON().keys.auth
  const pushSubP256DH = pushSubscription.toJSON().keys.p256dh

  const payload = {
    subscription: {
      endpoint: pushSubURL,
      keys: {
        auth: pushSubAuth,
        p256dh: pushSubP256DH,
      },
    },
    user_id: localStorage.getItem('user_id'),
  }
  console.log('payload:', payload)

  const response = await fetch(`${PUBLIC_API_URL}/api/v1/registrations`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  console.log('response:', response)
  if (response.status < 400) {
    const registration = await response.json()
    console.log('registration', registration)
  } else {
    console.log(`error ${response.status}: ${response.statusText}, ${response.body}`)
  }
}

export const clickOnNotificationPermission = async () => {
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
