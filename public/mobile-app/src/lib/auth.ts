import { PUBLIC_API_URL } from '$env/static/public'

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
