const notifyMessage = async () => {
  const payload = {
    title: notifyTitleInput.value,
    message: notifyMessageInput.value,
    sender: notifySenderInput.value,
    email: registerEmailInput.value,
  }
  console.log('notifying a message')
  notifyMessageBtn.disabled = true
  notifyMessageStatus.innerText = 'Notifying...'
  const response = await fetch('/notification/send', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  console.log('response from AMI:', response)
  notifyMessageBtn.disabled = false
  if (response.status < 400) {
    notifyMessageStatus.innerText = 'Done!'
  } else {
    notifyMessageStatus.innerText = `error ${response.status}: ${response.statusText}, ${response.body}`
  }
}

const registerEmailInput = document.querySelector('#register-email')
const notifyTitleInput = document.querySelector('#notify-title-input')
const notifyMessageInput = document.querySelector('#notify-message-input')
const notifySenderInput = document.querySelector('#notify-sender-input')
const notifyMessageBtn = document.querySelector('#notify-message')
notifyMessageBtn.addEventListener('click', notifyMessage)
const notifyMessageStatus = document.querySelector('#notify-message-status')
