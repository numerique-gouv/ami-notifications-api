import {
  PUBLIC_APP_URL,
  PUBLIC_FC_BASE_URL,
  PUBLIC_FC_LOGOUT_ENDPOINT,
  PUBLIC_FC_PROXY,
} from '$env/static/public'

export type UserInfo = {
  sub: string
  gender: string
  birthdate: string
  birthcountry: string
  birthplace: string
  given_name: string
  given_name_array: string[]
  family_name: string
  email: string
  aud: string
  exp: number
  iat: number
  iss: string
}

export function parseJwt(token: string): UserInfo {
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

export const franceConnectLogout = async (id_token_hint: string) => {
  const redirect_url = `${PUBLIC_APP_URL}/?is_logged_out`
  const params = new URLSearchParams({
    id_token_hint,
    state: redirect_url,
    post_logout_redirect_uri: PUBLIC_FC_PROXY || redirect_url,
  })
  const url = new URL(`${PUBLIC_FC_BASE_URL}${PUBLIC_FC_LOGOUT_ENDPOINT}`)
  url.search = params.toString()

  // Now logout from FC.
  window.location.href = url.toString()
}
