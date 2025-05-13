// const notifyMessage = async () => {
//   const payload = {
//     message: notifyMessageInput.value,
//     email: registerEmailInput.value,
//   }
//   console.log("notifying a message");
//   notifyMessageBtn.disabled = true;
//   notifyMessageStatus.innerText = "Notifying...";
//   const response = await fetch(
//     "/notification/send",
//     {
//       method: "POST",
//       body: JSON.stringify(payload),
//     }
//   );
//   console.log("response from AMI:", response);
//   notifyMessageBtn.disabled = false;
//   if (response.status < 400) {
//     notifyMessageStatus.innerText = "Done!";
//   } else {
//     notifyMessageStatus.innerText = `error ${response.status}: ${response.statusText}, ${response.body}`;
//   }
// }

// const notifyMessageInput = document.querySelector("#notify-message-input");
// const notifyMessageBtn = document.querySelector("#notify-message");
// notifyMessageBtn.addEventListener("click", notifyMessage);
// const notifyMessageStatus = document.querySelector("#notify-message-status");


import * as db from '$lib/database.js';

export function load({ cookies }) {
	let id = cookies.get('userid');

	if (!id) {
		id = crypto.randomUUID();
		cookies.set('userid', id, { path: '/' });
	}

	return {
		todos: db.getTodos(id)
	};
}

export const actions = {
	create: async ({ cookies, request }) => {
		const data = await request.formData();
		db.createTodo(cookies.get('userid'), data.get('description'));
	},

	delete: async ({ cookies, request }) => {
		const data = await request.formData();
		db.deleteTodo(cookies.get('userid'), data.get('id'));
	}
};
