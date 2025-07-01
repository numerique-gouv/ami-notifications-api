<script lang="ts">
import { PUBLIC_API_URL } from '$env/static/public'
import { onMount } from 'svelte'

const isAppInstalled: boolean = 'Notification' in window

let isAuthenticatedForNotifications: boolean = $state(false)
let authenticationStatus: string = $state('')
let isRegisteredWithAmi: boolean = $state(false)
let registrationStatus: string = $state('')
let userEmailValidationStatus: string = $state('')

let pushSubscription
let registerEmailInputValue: string = $state('')

let userEmailState: string = $state('')
let userNotifications: [] = $state([])

onMount(async () => {
  const emailLocalStorage: string | null =
    window.localStorage.getItem('emailLocalStorage')
  const pushSubscriptionLocalStorage: Object | null = window.localStorage.getItem(
    'pushSubscriptionLocalStorage'
  )

  if (emailLocalStorage && pushSubscriptionLocalStorage) {
    userEmailState = emailLocalStorage
    registerEmailInputValue = emailLocalStorage
    pushSubscription = pushSubscriptionLocalStorage
    await retrieveNotifications()
  }

  checkNotificationPermission().then((isGranted) => {
    isAuthenticatedForNotifications = isGranted === true
  })

  if (navigator.permissions) {
    let permissionStatusPromise = navigator.permissions.query({ name: 'notifications' })
    permissionStatusPromise.then((permissionStatus) => {
      isAuthenticatedForNotifications = permissionStatus.state == 'granted'
      console.log(`notifications permission status is ${permissionStatus.state}`)

      permissionStatus.onchange = () => {
        if (permissionStatus.state == 'granted') {
          isAuthenticatedForNotifications = true
        } else {
          resetElements()
        }
        console.log(
          `notifications permission status has changed to ${permissionStatus.state}`
        )
      }
    })
  }
})

const retrieveNotifications = async () => {
  if (userEmailState !== '') {
    try {
      const response = await fetch(`${PUBLIC_API_URL}/notifications/${userEmailState}`)

      if (response.status == 200) {
        userNotifications = await response.json()
        userNotifications.forEach(
          (notification) =>
            (notification.formattedDate = new Date(
              notification.date
            ).toLocaleDateString('fr-FR'))
        )
        console.log('userNotifications', userNotifications)
      }
    } catch (error) {
      console.error(error)
    }
  }
}

const checkNotificationPermission = async () => {
  const permission = await Notification.permission
  console.log('permission:', permission)
  return permission == 'granted'
}

const resetElements = () => {
  isAuthenticatedForNotifications = false
  authenticationStatus = ''
  isRegisteredWithAmi = false
  registrationStatus = ''
  pushSubscription = null
  registerEmailInputValue = ''
  userEmailState = ''
  userNotifications = []
  window.localStorage.setItem('emailLocalStorage', '')
  window.localStorage.setItem('pushSubscriptionLocalStorage', '')
}

const subscribePush = async () => {
  const registration = await navigator.serviceWorker.ready
  try {
    const applicationKeyResponse = await fetch(`${PUBLIC_API_URL}/notification/key`)
    const applicationKey = await applicationKeyResponse.text()
    const options = { userVisibleOnly: true, applicationServerKey: applicationKey }
    const pushSubscription = await registration.pushManager.subscribe(options)
    console.log('pushSubscription:', pushSubscription)
    console.log('Subscribed to the push manager')
    // The push subscription details needed by the application
    // server are now available, and can be sent to it using,
    // for example, the fetch() API.
    authenticationStatus = 'Inscription réussie au serveur de notifications'
    return pushSubscription
  } catch (error) {
    // During development it often helps to log errors to the
    // console. In a production environment it might make sense to
    // also report information about errors back to the
    // application server.
    console.error(error)
  }
}

const updateButtonsStates = async () => {
  const isGranted = await checkNotificationPermission()
  isAuthenticatedForNotifications = isGranted
  isRegisteredWithAmi = !isGranted

  if (isGranted) {
    pushSubscription = await subscribePush()
  }
}

const askForNotificationPermission = async () => {
  const permissionGranted = await Notification.requestPermission()
  const registration = await navigator.serviceWorker.ready
  if (!permissionGranted || !registration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    )
    return
  }
  await updateButtonsStates()
}

const registerWithAmi = async () => {
  if (registerEmailInputValue !== '') {
    userEmailValidationStatus = ''

    const pushSubURL = pushSubscription.endpoint
    const pushSubAuth = pushSubscription.toJSON().keys.auth
    const pushSubP256DH = pushSubscription.toJSON().keys.p256dh

    const payload = {
      subscription: {
        endpoint: pushSubURL,
        keys: {
          auth: pushSubAuth,
          p256dh: pushSubP256DH,
        },
      },
      email: registerEmailInputValue,
    }
    console.log('payload:', payload)
    isRegisteredWithAmi = true
    registrationStatus = "En cours d'enregistrement..."

    const response = await fetch(`${PUBLIC_API_URL}/notification/register`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    console.log('response:', response)
    isRegisteredWithAmi = false
    if (response.status < 400) {
      registrationStatus = 'Enregistrement réussi !'
      userEmailState = registerEmailInputValue
      userNotifications = []
      window.localStorage.setItem('emailLocalStorage', userEmailState)
      window.localStorage.setItem('pushSubscriptionLocalStorage', pushSubscription)
    } else {
      registrationStatus = `error ${response.status}: ${response.statusText}, ${response.body}`
    }
  } else {
    userEmailValidationStatus = 'Veuillez remplir le champ Email'
  }
}
</script>

<div>
	{#if !isAppInstalled}
	<p>
		Veuillez ajouter cette application sur l'écran d'accueil de votre téléphone, puis cliquez sur cette nouvelle icône pour ouvrir l'application
	</p>
	{:else}

	<div>
		{#if userEmailState}
			<h1>Bienvenue {userEmailState} sur l'application AMI</h1>
		{:else}
			<h1>Bienvenue sur l'application AMI</h1>
		{/if}

		<button
				type="button"
				onclick={askForNotificationPermission}
				disabled={isAuthenticatedForNotifications}
		>
			S'authentifier pour recevoir des notifications
		</button>
		<span id="authentication-status" title="authentication-status-title">{authenticationStatus}</span>

		<div>
			<p>
				<label
				>Email
					<input
							bind:value={registerEmailInputValue}
							type="text"
							id="register-email"
							name="register-email"
					/>
				</label>
			</p>
			<p>
				<span id="email-validation-status">{userEmailValidationStatus}</span>
			</p>
			<p>
				<button
						type="button"
						id="register-with-ami"
						onclick={registerWithAmi}
						disabled={isRegisteredWithAmi}
				>
					S'enregistrer auprès d'AMI
				</button>
				<span id="registration-status">{registrationStatus}</span>
			</p>
		</div>

		<div>
			<h2>Historique des notifications</h2>
			<button
					type="button"
					onclick={retrieveNotifications}
			>
				Rafraîchir la liste des notifications reçues
			</button>
			{#if userNotifications.length === 0}
				<p>Vous n'avez pas reçu de notification pour l'instant</p>
			{:else}
				<ul>
					{#each userNotifications as notification}
						<li>
							<p>Notification reçue le {notification.formattedDate}</p>
							<p>Titre : {notification.title}</p>
							<p>Message : {notification.message}</p>
							<p>Expéditeur : {notification.sender}</p>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	</div>
  {/if}
</div>
