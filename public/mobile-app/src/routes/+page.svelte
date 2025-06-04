<script lang="ts">
	import type { PageProps } from './$types';

	import { PUBLIC_API_HOSTNAME, PUBLIC_API_PORT } from '$env/static/public';

	let subscriptionStatus = $state('');
	let isAuthenticatedForNotifications = $state(false);
	let isRegisteredWithAmi = $state(false);

	let pushSubURL = $state('pushSubURL');
	let pushSubAuth = $state('pushSubAuth');
	let pushSubP256DH = $state('pushSubP256DH');
	let registerEmailValue = $state('');
	let registrationStatus = $state('');
	let pushSubscription;

	const checkNotificationPermission = async () => {
		// Check if the browser supports notifications
		if (!('Notification' in window)) {
			alert('Add this website to your home screen!');
			return false;
		}
		const permission = await Notification.permission;
		console.log('permission:', permission);
		return permission == 'granted';
	};

	const subscribePush = async () => {
		const registration = await navigator.serviceWorker.ready;
		try {
			const applicationKeyResponse = await fetch(`//${PUBLIC_API_HOSTNAME}:${PUBLIC_API_PORT}/notification/key`);
			const applicationKey = await applicationKeyResponse.text();
			const options = { userVisibleOnly: true, applicationServerKey: applicationKey };
			pushSubscription = await registration.pushManager.subscribe(options);
			console.log('pushSubscription', pushSubscription);
			console.debug('auth key:', pushSubscription.toJSON().keys.auth);
			console.debug('p256dh:', pushSubscription.toJSON().keys.p256dh);
			// The push subscription details needed by the application
			// server are now available, and can be sent to it using,
			// for example, the fetch() API.
			console.log("Subscribed to the push manager");
			subscriptionStatus = "Subscribed to the push manager";
			return pushSubscription;
		} catch (error) {
			// During development it often helps to log errors to the
			// console. In a production environment it might make sense to
			// also report information about errors back to the
			// application server.
			console.error(error);
		}
	};

	const updateButtonsStates = async () => {
		const isGranted = await checkNotificationPermission();
		console.log('inside updateButtonsStates, isGranted:', isGranted);
		isAuthenticatedForNotifications = isGranted;
        isRegisteredWithAmi = !isGranted;

		if (isGranted) {
			const pushSubscription = await subscribePush();
			pushSubURL = pushSubscription.endpoint;
			pushSubAuth = pushSubscription.toJSON().keys.auth;
			pushSubP256DH = pushSubscription.toJSON().keys.p256dh;
		}
	};

	const askForNotificationPermission = async () => {
		const permissionGranted = await Notification.requestPermission();
		const registration = await navigator.serviceWorker.ready;
		if (!permissionGranted || !registration) {
			console.log('No notification: missing permission or missing service worker registration');
			return;
		}
		await updateButtonsStates();
	};

	const registerWithAmi = async () => {
		console.log('registerWithAmi');

		const payload = {
			subscription: {
				endpoint: pushSubURL,
				keys: {
					auth: pushSubAuth,
					p256dh: pushSubP256DH
				}
			},
			email: registerEmailValue
		};
		console.log('isRegistered with AMI:', payload);
        isRegisteredWithAmi = true;
        registrationStatus = 'Registering...';

		const response = await fetch(`//${PUBLIC_API_HOSTNAME}:${PUBLIC_API_PORT}/notification/register`, {
			method: 'POST',
			body: JSON.stringify(payload)
		});
		console.log('response from AMI:', response);
        isRegisteredWithAmi = false;
		if (response.status < 400) {
		  registrationStatus = 'Done!';
	    } else {
		  registrationStatus = `error ${response.status}: ${response.statusText}, ${response.body}`;
	    }
	};
</script>

<div>
	<h1>Welcome to the Mobile App</h1>

	<button
		type="button"
		onclick={askForNotificationPermission}
		disabled={isAuthenticatedForNotifications}
	>
		Ask notifications auth
	</button>
	<span id="subscription-status">{subscriptionStatus}</span>

	<p>
		<label>pushURL<input id="push-sub-url" bind:value={pushSubURL} disabled /></label>
		<label>auth<input id="push-sub-auth" bind:value={pushSubAuth} disabled /></label>
		<label>p256dh<input id="push-sub-p256dh" bind:value={pushSubP256DH} disabled /></label>
	</p>

	<div>
		<p>
			<label
				>Email for the registration
				<input
					bind:value={registerEmailValue}
					type="text"
					id="register-email"
					name="register-email"
				/>
			</label>
		</p>
		<p>
			<button
				type="button"
				id="register-with-ami"
				onclick={registerWithAmi}
				disabled={isRegisteredWithAmi}
			>
				Register with AMI
			</button>
			<span id="registration-status">{registrationStatus}</span>
		</p>
	</div>
</div>
