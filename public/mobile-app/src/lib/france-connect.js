import {
  PUBLIC_APP_URL,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_LOGOUT_ENDPOINT,
  PUBLIC_FC_PROXY,
} from '$env/static/public'

export function parseJwt(token) {
  const base64Url = token.split('.')[1]
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
  const jsonPayload = decodeURIComponent(
    window
      .atob(base64)
      .split('')
      .map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      })
      .join('')
  )

  return JSON.parse(jsonPayload)
}

export const franceConnectLogout = async () => {
  const redirect_url = `${PUBLIC_APP_URL}/?is_logged_out`
  const params = new URLSearchParams({
    id_token_hint: localStorage.getItem('id_token') || '',
    state: redirect_url,
    post_logout_redirect_uri: PUBLIC_FC_PROXY || redirect_url,
  })
  const url = new URL(`${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}`)
  url.search = params.toString()

  // Logout from AMI first: https://github.com/numerique-gouv/ami-notifications-api/issues/132
  localStorage.clear()

  // Now logout from FC.
  window.location = url.toString()
}
