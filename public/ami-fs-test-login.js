const franceConnect = async () => {
  const FS_URL = 'https://localhost:8000'
  const DATA_CALLBACK_FS_PATH = '/ami-fs-test-login-callback'
  const DATA_CLIENT_ID =
    '88d6fc32244b89e2617388fb111e668fec7b7383c841a08eefbd58fd11637eec'
  const STATE = 'stateazertyuiopqsdfghjklmwxcvbn012345'
  const NONCE = 'nonceazertyuiopqsdfghjklmwxcvbn012345'
  const FC_URL = 'https://fcp-low.sbx.dev-franceconnect.fr'
  const AUTHORIZATION_FC_PATH = '/api/v2/authorize'

  const query = {
    scope:
      'openid given_name family_name preferred_username birthdate gender birthplace birthcountry sub email given_name_array',
    redirect_uri: `${FS_URL}${DATA_CALLBACK_FS_PATH}`,
    response_type: 'code',
    client_id: DATA_CLIENT_ID,
    state: STATE,
    nonce: NONCE,
    acr_values: 'eidas1',
    prompt: 'login',
  }

  const url = `${FC_URL}${AUTHORIZATION_FC_PATH}`
  const params = new URLSearchParams(query).toString()

  window.location.href = `${url}?${params}`

  return Response.redirect(`${url}?${params}`)
}

const franceConnectBtn = document.querySelector('#fr-connect-button')
// FC - Step 3
franceConnectBtn.addEventListener('click', franceConnect)
