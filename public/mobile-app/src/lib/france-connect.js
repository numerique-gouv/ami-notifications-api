import {
  PUBLIC_APP_URL,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_LOGOUT_ENDPOINT,
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
  const params = new URLSearchParams({
    id_token_hint: localStorage.getItem('id_token') || '',
    state: 'not-implemented-yet-and-has-more-than-32-chars',
    post_logout_redirect_uri: `${PUBLIC_APP_URL}/?is_logged_out`,
  })
  const url = new URL(`${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}`)
  url.search = params.toString()
  window.location = url.toString()
}
