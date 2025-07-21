const franceConnect = async () => {
  const FC_AUTHORIZATION_URL =
    'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize'

  console.log('clickOnFCButton')

  const params =
    'response_type=code&' +
    'prompt=login&' +
    'client_id=88d6fc32244b89e2617388fb111e668fec7b7383c841a08eefbd58fd11637eec&' +
    'redirect_uri=' +
    encodeURIComponent('https://localhost:8000/ami-fs-test-login-callback') +
    '&' +
    'acr_values=eidas1&' +
    'scope=openid&' +
    'state=stateazertyuiopqsdfghjklmwxcvbn012345&' +
    'nonce=nonceazertyuiopqsdfghjklmwxcvbn012345'
  // https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize?response_type=code&prompt=login&client_id=88d6fc32244b89e2617388fb111e668fec7b7383c841a08eefbd58fd11637eec&redirect_uri=https%3A%2F%2Flocalhost%3A8000%2Fami-fs-test-login-callback&acr_values=eidas1&scope=openid&state=stateazertyuiopqsdfghjklmwxcvbn012345&nonce=nonceazertyuiopqsdfghjklmwxcvbn012345

  const response = await fetch(`${FC_AUTHORIZATION_URL}?${params}`, {
    method: 'GET',
    // headers: {
    //   "Content-Type": "application/x-www-form-urlencoded",
    //   "Access-Control-Allow-Origin": "*",
    // },
  })
  console.log('response:', response)
}

const franceConnectBtn = document.querySelector('#fr-connect-button')
// Step 3
franceConnectBtn.addEventListener('click', franceConnect)
