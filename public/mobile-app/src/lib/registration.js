import { PUBLIC_API_URL } from '$env/static/public'
import { subscribePush } from '$lib/notifications.ts'

export const registerUser = async (pushSubscription) => {
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
    return registration
  } else {
    console.log(`error ${response.status}: ${response.statusText}, ${response.body}`)
  }
}
