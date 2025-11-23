import { PUBLIC_API_URL } from '$env/static/public'
import { subscribePush } from '$lib/notifications'

export const registerDevice = async (pushSubscription) => {
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

  const response = await fetch(`${PUBLIC_API_URL}/api/v1/users/registrations`, {
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

export const unregisterDevice = async (registrationId) => {
  const headers = {
    'Content-Type': 'application/json',
  }
  const response = await fetch(
    `${PUBLIC_API_URL}/api/v1/users/registrations/${registrationId}`,
    {
      method: 'DELETE',
      headers: headers,
    }
  )
  console.log('response:', response)
  if (response.status === 204) {
    console.log('The device has been deleted successfully')
  } else {
    console.log(`error ${response.status}: ${response.statusText}, ${response.body}`)
  }
  return response.status
}
