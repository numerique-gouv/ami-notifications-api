import { fail } from '@sveltejs/kit';

export const actions = {
	registerWithAmi: async ({ request }) => {
		console.log("registerWithAmi");
		const data = await request.formData();
		
		const registerEmail = data.get('register-email');

		let error = new Error('');
		if (registerEmail === '') {
			error = new Error('register email must be filled');
			return fail(422, {
				registerEmail: '',
				error: error.message
			});
		}

    // const payload = {
		// 	subscription: {
		// 		endpoint: pushSubscription.endpoint,
		// 		keys: {
		// 			auth: pushSubscription.toJSON().keys.auth,
		// 			p256dh: pushSubscription.toJSON().keys.p256dh,
		// 		},
		// 	},
		// 	email: registerEmail,
		// }
		const payload = {
			subscription: {
				endpoint: data.get('push-sub-url'),
				keys: {
					auth: data.get('push-sub-auth'),
					p256dh: data.get('push-sub-p256dh'),
				},
			},
			email: registerEmail,
		}
		console.log("registering with AMI:", payload);
		
		const response = await fetch(
			"http://localhost:8000/notification/register",
			{
				method: "POST",
				body: JSON.stringify(payload),
			}
		);
		console.log("response from AMI:", response);
		if (response.status >= 400) {
			return fail(422, {
				registerEmail: data.get('register-email'),
				error: `error ${response.status}: ${response.statusText}, ${response.body}`
			});
		}
	},

	// notifyMessage: async ({ request }) => {
	// 	const data = await request.formData();
		
	// 	const userEmail = data.get('user-email');
	// 	const notifyMessage = data.get('notify-message');

	// 	let error = new Error('');
	// 	if (userEmail === '') {
	// 		error = new Error('user email must be filled');
	// 		return fail(422, {
	// 			userEmail: data.get('userEmail'),
	// 			notifyMessage: data.get('notifyMessage'),
	// 			error: error.message
	// 		});
	// 	}
	// 	if (notifyMessage === '') {
	// 		error = new Error('notify message must be filled');
	// 		return fail(422, {
	// 			userEmail: data.get('userEmail'),
	// 			notifyMessage: data.get('notifyMessage'),
	// 			error: error.message
	// 		});
	// 	}

	// 	const payload = {
	// 		message: notifyMessage,
	// 		email: userEmail,
	// 	}
	// 	console.log("notifying a message");
		
	// 	const response = await fetch(
	// 		"http://localhost:8000/notification/send",
	// 		{
	// 			method: "POST",
	// 			body: JSON.stringify(payload),
	// 		}
	// 	);
	// 	console.log("response from AMI:", response);
	// 	if (response.status >= 400) {
	// 		return fail(422, {
	// 			userEmail: data.get('userEmail'),
	// 			notifyMessage: data.get('notifyMessage'),
	// 			error: `error ${response.status}: ${response.statusText}, ${response.body}`
	// 		});
	// 	}
	// }
};
