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

const notifyMe = async () => {
  const registration = await navigator.serviceWorker.ready;
  const permissionGranted = await checkNotificationPermission();
  if (!permissionGranted || !registration) {
    console.log("No notification: missing permission or missing service worker registration");
    return;
  }

  let notificationMsg = `LOCAL notification with the date: ${new Date()}`
  console.log("notifying local message:", notificationMsg);
  registration.showNotification("Local notification", {
    body: notificationMsg,
    //icon: "../images/touch/chrome-touch-icon-192x192.png",
    //vibrate: [200, 100, 200, 100, 200, 100, 200],
    //tag: "vibration-sample",
  });
  loadingText.innerHTML = "Displayed local notification";
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
    const pushSubscription = await registration.pushManager.subscribe(options);
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

const updateButtonsStates = async () => {
  const isGranted = await checkNotificationPermission();
  console.log("inside updateButtonsStates, isGranted:", isGranted);
  askNotificationsBtn.disabled = isGranted;
  notifyMeBtn.disabled = !isGranted;
  pushSubURL.disabled = !isGranted;

  if (isGranted) {
    const pushSubscription = await subscribePush();
    pushSubURL.innerText = pushSubscription.endpoint;
    pushSubAuth.value = pushSubscription.toJSON().keys.auth;
    pushSubP256DH.value = pushSubscription.toJSON().keys.p256dh;
  }
};

const loadingText = document.querySelector("#loading-text");
const askNotificationsBtn = document.querySelector("#ask-for-notifications");
askNotificationsBtn.addEventListener("click", askForNotificationPermission);
const notifyMeBtn = document.querySelector("#notify-me-btn");
notifyMeBtn.addEventListener("click", notifyMe);
const pushSubURL = document.querySelector("#push-sub-url");
const pushSubAuth = document.querySelector("#push-sub-auth");
const pushSubP256DH = document.querySelector("#push-sub-p256dh");

updateButtonsStates();

registerServiceWorker();
