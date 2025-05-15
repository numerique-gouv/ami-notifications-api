<script lang="ts">
	import { enhance } from '$app/forms';

	let { form } = $props();

	let creating = $state(false);

	let pushSubURL = $state('pushSubURL');
	let pushSubAuth = $state('pushSubAuth');
	let pushSubP256DH = $state('pushSubP256DH');
	let pushSubscription;

	const checkNotificationPermission = async () => {
		console.log('checkNotificationPermission');
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
		console.log('subscribePush 1');
		// const registration = await navigator.serviceWorker.ready;
		// console.log("subscribePush 2");
		try {
			// const applicationKeyResponse = await fetch("/notification/key");
			// const applicationKey = await applicationKeyResponse.text();
			// $ uv run vapid-gen
			const applicationKey =
				'BNMNg_hRPF8toxsUCa7qx7iq-BAALLM5W9tG6ETSsXC2IKEkD9wgSAdhaleQAEELdZdmYoXdxY6KtURYgJLBpBo';
			console.log('applicationKey:', applicationKey);
			const options = { userVisibleOnly: true, applicationServerKey: applicationKey };
			pushSubscription = await registration.pushManager.subscribe(options);
			console.log('pushSubscription', pushSubscription);
			console.debug('auth key:', pushSubscription.toJSON().keys.auth);
			console.debug('p256dh:', pushSubscription.toJSON().keys.p256dh);
			// The push subscription details needed by the application
			// server are now available, and can be sent to it using,
			// for example, the fetch() API.
			// loadingText.innerHTML = "subcribed to the push manager";
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
		console.log('updateButtonsStates');
		const isGranted = await checkNotificationPermission();
		console.log('inside updateButtonsStates, isGranted:', isGranted);
		// askNotificationsBtn.disabled = isGranted;
		// registerBtn.disabled = !isGranted;

		if (isGranted) {
			const pushSubscription = await subscribePush();
			pushSubURL = pushSubscription.endpoint;
			pushSubAuth = pushSubscription.toJSON().keys.auth;
			pushSubP256DH = pushSubscription.toJSON().keys.p256dh;
		}
	};

	const askForNotificationPermission = async () => {
		console.log('askForNotificationPermission 1');
		const permissionGranted = await Notification.requestPermission();
		console.log('askForNotificationPermission 2');
		// const registration = await navigator.serviceWorker.ready;
		// console.log("askForNotificationPermission 3");
		// if (!permissionGranted || !registration) {
		//   console.log("No notification: missing permission or missing service worker registration");
		//   return;
		// }
		if (!permissionGranted) {
			console.log('No notification: missing permission');
			return;
		}
		updateButtonsStates();
	};
</script>

<div>
	<h1>Welcome to the Mobile App</h1>

	{#if form?.error}
		<p class="error">{form.error}</p>
	{/if}

	<button type="button" onclick={askForNotificationPermission}> Ask notifications auth </button>

	<p>
		<label>pushURL<input id="push-sub-url" value={pushSubURL} disabled /></label>
		<label>auth<input id="push-sub-auth" value={pushSubAuth} disabled /></label>
		<label>p256dh<input id="push-sub-p256dh" value={pushSubP256DH} disabled /></label>
	</p>

	<form
		method="POST"
		action="?/registerWithAmi"
		use:enhance={() => {
			creating = true;

			return async ({ update }) => {
				await update();
				creating = false;
			};
		}}
	>
		<p>
			<label
				>Email for the registration
				<input
					type="text"
					id="register-email"
					name="register-email"
					value={form?.registerEmail ?? ''}
					disabled={creating}
				/>
			</label>
		</p>
		<p class="hidden">
			<label>pushURL<input id="push-sub-url" value={pushSubURL} disabled /></label>
			<label>auth<input id="push-sub-auth" value={pushSubAuth} disabled /></label>
			<label>p256dh<input id="push-sub-p256dh" value={pushSubP256DH} disabled /></label>
		</p>
		<p>
			<button type="button" id="register-with-ami">Register with AMI</button>
			<span id="registration-status"></span>
		</p>
	</form>

	{#if creating}
		<span class="saving">Registering...</span>
	{/if}
</div>

<style>
	.hidden {
		display: none;
	}
</style>
