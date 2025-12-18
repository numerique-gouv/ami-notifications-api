import { PUBLIC_API_URL } from '$env/static/public'

export const getQuotientData = async () => {
  let quotientData = localStorage.getItem('quotient_data')
  if (!quotientData) {
    const access_token = localStorage.getItem('access_token')
    const token_type = localStorage.getItem('token_type')
    const quotient_endpoint_headers = {
      FC_Authorization: `${token_type} ${access_token}`,
    }
    const response = await fetch(`${PUBLIC_API_URL}/data/api-particulier/quotient`, {
      headers: quotient_endpoint_headers,
      credentials: 'include',
    })
    quotientData = await response.text()
    if (response.ok) {
      localStorage.setItem('quotient_data', quotientData)
    }
  }
  if (quotientData) {
    return JSON.parse(quotientData)
  }
}
