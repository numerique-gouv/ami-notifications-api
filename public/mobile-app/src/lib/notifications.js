import { PUBLIC_API_URL } from '$env/static/public'

export const getSubscription = async () => {
  console.log("refreshing the push subscription, if it's there")
  const registration = await navigator.serviceWorker.ready
  if (registration) {
    const sub = await registration.pushManager.getSubscription()
    console.log('refreshed subscription:', sub)
    return sub
  }
}

export const retrieveNotifications = async () => {
  let messages = []
  const userId = localStorage.getItem('user_id')
  if (userId) {
    try {
      const response = await fetch(
        `${PUBLIC_API_URL}/api/v1/users/${userId}/notifications`
      )

      if (response.status == 200) {
        messages = await response.json()
        messages.forEach(
          (message) =>
            (message.formattedDate = new Date(message.date).toLocaleDateString('fr-FR'))
        )
        console.log('messages', messages)
        return messages
      }
    } catch (error) {
      console.error(error)
    }
  }
}

export const checkNotificationPermission = async () => {
  const permission = await Notification.permission
  console.log('permission:', permission)
  return permission == 'granted'
}

export const subscribePush = async () => {
  const registration = await navigator.serviceWorker.ready
  try {
    const applicationKeyResponse = await fetch(`${PUBLIC_API_URL}/notification-key`)
    const applicationKey = await applicationKeyResponse.text()
    const options = { userVisibleOnly: true, applicationServerKey: applicationKey }
    const pushSubscription = await registration.pushManager.subscribe(options)
    console.log('pushSubscription:', pushSubscription)
    console.log('Subscribed to the push manager')
    // The push subscription details needed by the application
    // server are now available, and can be sent to it using,
    // for example, the fetch() API.
    return pushSubscription
  } catch (error) {
    // During development it often helps to log errors to the
    // console. In a production environment it might make sense to
    // also report information about errors back to the
    // application server.
    console.error(error)
  }
}

export const updateButtonsStates = async (isGranted) => {
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

export const askForNotificationPermission = async (isGranted) => {
  const permissionGranted = await Notification.requestPermission()
  const registration = await navigator.serviceWorker.ready
  if (!permissionGranted || !registration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    )
    return
  }
  if (isGranted) {
    await updateButtonsStates(isGranted)
  }
}
