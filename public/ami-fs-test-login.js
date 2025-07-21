const franceConnect = async () => {
  const FC_AUTHORIZATION_URL =
    'https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize'

  console.log('clickOnFCButton')
  const response = await fetch(`${FC_AUTHORIZATION_URL}`, {
    method: 'POST',
  })
  console.log('response:', response)
}

const franceConnectBtn = document.querySelector('#fr-connect-button')
franceConnectBtn.addEventListener('click', franceConnect)
