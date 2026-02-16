import { apiFetch } from '$lib/auth'

export const retrieveProcedureUrl = async (
  preferredUsername: string,
  email: string,
  addressCity: string,
  addressPostcode: string,
  addressName: string
): Promise<string> => {
  try {
    const response = await apiFetch(
      `/api/v1/partner/otv/url?preferred_username=${preferredUsername}&email=${email}&address_city=${addressCity}&address_postcode=${addressPostcode}&address_name=${addressName}`,
      {
        credentials: 'include',
      }
    )
    if (response.status === 200) {
      const responseJson = await response.json()
      return responseJson.partner_url
    }
    return ''
  } catch (error) {
    console.error(error)
    return ''
  }
}
