import { PUBLIC_API_URL } from '$env/static/public';
import { apiFetch } from '$lib/auth';
import type { Registration } from '$lib/registration';
import { registerDevice, unregisterDevice } from '$lib/registration';

export const PUBLIC_API_WS_URL = PUBLIC_API_URL.replace('https://', 'wss://').replace(
  'http://',
  'ws://'
);

export type AppNotification = {
  id: string;
  created_at: Date;
  user_id: string;
  content_title: string;
  content_body: string;
  content_icon?: string;
  sender: string;
  item_external_url: string;
  read: boolean;
};

export const retrieveNotifications = async (): Promise<AppNotification[]> => {
  let notifications = [] as AppNotification[];
  try {
    const response = await apiFetch('/api/v1/users/notifications', {
      credentials: 'include',
    });
    if (response.status === 200) {
      notifications = await response.json();
    }
  } catch (error) {
    console.error(error);
  }
  console.log('notifications', notifications);
  return notifications;
};

export const countUnreadNotifications = async (): Promise<number> => {
  let notifications = [] as AppNotification[];
  try {
    const response = await apiFetch('/api/v1/users/notifications?read=false', {
      credentials: 'include',
    });
    if (response.status === 200) {
      notifications = await response.json();
    }
  } catch (error) {
    console.error(error);
  }
  return notifications.length;
};

export const readNotification = async (
  notificationId: string
): Promise<AppNotification | undefined> => {
  try {
    const payload = {
      read: true,
    };
    const response = await apiFetch(
      `/api/v1/users/notification/${notificationId}/read`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
        credentials: 'include',
      }
    );
    if (response.status === 200) {
      const notification = (await response.json()) as AppNotification;
      return notification;
    }
  } catch (error) {
    console.error(error);
  }
  return undefined;
};

export const notificationEventsSocket = (onmessage: (event: MessageEvent) => void) => {
  const ws = new WebSocket(
    `${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`
  );
  ws.onmessage = onmessage;
};

export const enableNotificationsAndUpdateLocalStorage =
  async (): Promise<Registration | null> => {
    let registration: Registration | null;
    registration = await enableNotifications();
    if (registration) {
      localStorage.setItem('registration_id', registration.id);
      localStorage.setItem('notifications_enabled', 'true');
    }
    return registration;
  };

export const subscribePush = async () => {
  const registration = await getServiceWorkerRegistration();
  try {
    const applicationKeyResponse = await apiFetch('/notification-key');
    const applicationKey = await applicationKeyResponse.text();
    const options = { userVisibleOnly: true, applicationServerKey: applicationKey };
    const pushSubscription = await registration.pushManager.subscribe(options);
    console.log('pushSubscription:', pushSubscription);
    console.log('subscribed to the push manager');
    return pushSubscription;
  } catch (error) {
    console.error(error);
  }
};

export const enableNotifications = async (): Promise<Registration | null> => {
  if (typeof Notification === 'undefined') {
    console.error('Notification API is not available in this browser');
    return null;
  }
  const permissionGranted = await Notification.requestPermission();
  const registration = await getServiceWorkerRegistration();
  if (!permissionGranted || !registration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    );
  } else {
    const pushSubscription = await subscribePush();
    if (pushSubscription) {
      return await registerDevice(pushSubscription);
    }
  }
  return null;
};

export const unsubscribePush = async (pushSubscription: PushSubscription) => {
  try {
    const hasUnsubscribed = await pushSubscription.unsubscribe();
    if (hasUnsubscribed) {
      console.log('unsubscribed to the push manager');
    } else {
      console.log('failed to unsubscribe to the push manager');
    }
    return hasUnsubscribed;
  } catch (error) {
    console.error(error);
  }
};

export const disableNotifications = async (registrationId: string) => {
  if (typeof Notification === 'undefined') {
    console.error('Notification API is not available in this browser');
    return false;
  }
  const permissionGranted = await Notification.requestPermission();
  const registration = await getServiceWorkerRegistration();
  if (!permissionGranted || !registration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    );
    return false;
  } else {
    const pushSubscription = await registration.pushManager.getSubscription();
    if (pushSubscription) {
      console.log('unregisterDevice');
      await unregisterDevice(registrationId);
      await unsubscribePush(pushSubscription);
    }
    return pushSubscription;
  }
};

const getServiceWorkerRegistration = async () => {
  return await navigator.serviceWorker.ready;
};
