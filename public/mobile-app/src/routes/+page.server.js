import { fail } from '@sveltejs/kit';

export const actions = {
	notifyMessage: async ({ request }) => {
		const data = await request.formData();
		
		const userEmail = data.get('user-email');
		const notifyMessage = data.get('notify-message');

		let error = new Error('');
		if (userEmail === '') {
			error = new Error('user email must be filled');
			return fail(422, {
				userEmail: data.get('userEmail'),
				notifyMessage: data.get('notifyMessage'),
				error: error.message
			});
		}
		if (notifyMessage === '') {
			error = new Error('notify message must be filled');
			return fail(422, {
				userEmail: data.get('userEmail'),
				notifyMessage: data.get('notifyMessage'),
				error: error.message
			});
		}

		const payload = {
			message: notifyMessage,
			email: userEmail,
		}
		console.log("notifying a message");
		
		const response = await fetch(
			"http://localhost:8000/notification/send",
			{
				method: "POST",
				body: JSON.stringify(payload),
			}
		);
		console.log("response from AMI:", response);
		if (response.status >= 400) {
			return fail(422, {
				userEmail: data.get('userEmail'),
				notifyMessage: data.get('notifyMessage'),
				error: `error ${response.status}: ${response.statusText}, ${response.body}`
			});
		}
	}
};
