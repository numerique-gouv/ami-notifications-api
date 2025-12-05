import { goto } from '$app/navigation'
import { PUBLIC_API_URL } from '$env/static/public'
import { userStore } from '$lib/state/User.svelte'

export const logout = async (): Promise<boolean> => {
  // delete auth cookie
  const response = await fetch(`${PUBLIC_API_URL}/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  if (response.status >= 400) {
    console.log(
      `logout error ${response.status}: ${response.statusText}, ${response.body}`
    )
    return false
  }
  return true
}

export const checkAuth = async (): Promise<boolean> => {
  const response = await fetch(`${PUBLIC_API_URL}/check-auth`, {
    credentials: 'include',
  })
  if (response.status >= 300) {
    console.log(
      `check-auth error ${response.status}: ${response.statusText}, ${response.body}`
    )
    return false
  }
  return true
}

export const apiFetch = async (
  input: string,
  init?: RequestInit
): Promise<Response> => {
  const response = await fetch(`${PUBLIC_API_URL}${input}`, init)

  if (response.status === 401) {
    console.log(
      `apiFetch error ${response.status} for ${input} (init: ${init}): ${response.statusText}, ${response.body}`
    )
    await userStore.logout()
  }

  return response
}
