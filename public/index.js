const checkNotificationPermission = async () => {
  // Check if the browser supports notifications
  if (!("Notification" in window)) {
    alert("This browser does not support notifications.");
    return false;
  }
  const permission = await Notification.permission;
  console.log("permission:", permission);
  return permission == "granted";
};

const askForNotificationPermission = async () => {
  const permissionGranted = await Notification.requestPermission();
  const registration = await navigator.serviceWorker.ready;
  if (!permissionGranted || !registration) {
    console.log("No notification: missing permission or missing service worker registration");
    return;
  }
  updateButtonsStates();
};

const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('sw.js');
      let status;
      if (registration.installing) {
        status = "Service worker installing";
      } else if (registration.waiting) {
        status = "Service worker installed";
      } else if (registration.active) {
        status = "Service worker active";
      }
      console.log(status);
      loadingText.innerHTML = status;
      registration.update();
      return registration;
    } catch (error) {
      console.error(`Registration failed with ${error}`);
    }
  } else {
    alert("Service workers are not supported");
  }
};

const subscribePush = async () => {
  const registration = await navigator.serviceWorker.ready;
  try {
    const applicationKeyResponse = await fetch("/notification/key");
    const applicationKey = await applicationKeyResponse.text();
    console.log("applicationKey:", applicationKey);
    const options = { userVisibleOnly: true, applicationServerKey: applicationKey };
    pushSubscription = await registration.pushManager.subscribe(options);
    console.log("pushSubscription", pushSubscription);
    console.debug("auth key:", pushSubscription.toJSON().keys.auth);
    console.debug("p256dh:", pushSubscription.toJSON().keys.p256dh);
    // The push subscription details needed by the application
    // server are now available, and can be sent to it using,
    // for example, the fetch() API.
    loadingText.innerHTML = "subcribed to the push manager";
    return pushSubscription;
  } catch (error) {
    // During development it often helps to log errors to the
    // console. In a production environment it might make sense to
    // also report information about errors back to the
    // application server.
    console.error(error);
  }
};

const registerWithAMI = async () => {
  const payload = {
    subscription: {
      endpoint: pushSubscription.endpoint,
      keys: {
        auth: pushSubscription.toJSON().keys.auth,
        p256dh: pushSubscription.toJSON().keys.p256dh,
      },
    },
    email: registerEmailInput.value,
  }
  console.log("registering with AMI:", payload);
  registerBtn.disabled = true;
  registrationStatus.innerText = "Registering...";
  const response = await fetch(
    "/notification/register",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
  console.log("response from AMI:", response);
  registerBtn.disabled = false;
  if (response.status < 400) {
    registrationStatus.innerText = "Done!";
  } else {
    registrationStatus.innerText = `error ${response.status}: ${response.statusText}, ${response.body}`;
  }
};

const notifyMessage = async () => {
  const payload = {
    message: notifyMessageInput.value,
    email: registerEmailInput.value,
  }
  console.log("notifying a message");
  notifyMessageBtn.disabled = true;
  notifyMessageStatus.innerText = "Notifying...";
  const response = await fetch(
    "/notification/send",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
  console.log("response from AMI:", response);
  notifyMessageBtn.disabled = false;
  if (response.status < 400) {
    notifyMessageStatus.innerText = "Done!";
  } else {
    notifyMessageStatus.innerText = `error ${response.status}: ${response.statusText}, ${response.body}`;
  }
}

const updateButtonsStates = async () => {
  const isGranted = await checkNotificationPermission();
  console.log("inside updateButtonsStates, isGranted:", isGranted);
  askNotificationsBtn.disabled = isGranted;
  registerBtn.disabled = !isGranted;

  if (isGranted) {
    const pushSubscription = await subscribePush();
    pushSubURL.innerText = pushSubscription.endpoint;
    pushSubAuth.value = pushSubscription.toJSON().keys.auth;
    pushSubP256DH.value = pushSubscription.toJSON().keys.p256dh;
  }
};

let pushSubscription;

const loadingText = document.querySelector("#loading-text");
const askNotificationsBtn = document.querySelector("#ask-for-notifications");
askNotificationsBtn.addEventListener("click", askForNotificationPermission);
const pushSubURL = document.querySelector("#push-sub-url");
const pushSubAuth = document.querySelector("#push-sub-auth");
const pushSubP256DH = document.querySelector("#push-sub-p256dh");
const registerEmailInput = document.querySelector("#register-email");
const registerBtn = document.querySelector("#register-with-ami");
registerBtn.addEventListener("click", registerWithAMI);
const registrationStatus = document.querySelector("#registration-status");
const notifyMessageInput = document.querySelector("#notify-message-input");
const notifyMessageBtn = document.querySelector("#notify-message");
notifyMessageBtn.addEventListener("click", notifyMessage);
const notifyMessageStatus = document.querySelector("#notify-message-status");

updateButtonsStates();

registerServiceWorker();
