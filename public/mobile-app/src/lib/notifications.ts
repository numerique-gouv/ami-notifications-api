import { PUBLIC_API_URL } from '$env/static/public';
import { apiFetch } from '$lib/auth';
import { isNative } from '$lib/nativeEvents';
import type { Registration } from '$lib/registration';
import {
  registerDevice,
  unregisterDesktopRegistration,
  unregisterDevice,
} from '$lib/registration';
import * as self from './notifications';

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
  url: string;
  read: boolean;
};

export const fetchAndStoreNotifications = async () => {
  let notifications = [] as AppNotification[];

  try {
    const response = await apiFetch('/api/v1/users/notifications', {
      credentials: 'include',
    });
    if (response.status === 200) {
      notifications = await response.json();
      localStorage.setItem('notifications', JSON.stringify(notifications));
    }
  } catch (error) {
    console.error(error);
  }
};

export const getNotificationsFromStore = async (): Promise<AppNotification[]> => {
  const notificationsString: string = localStorage.getItem('notifications') || '';
  return JSON.parse(notificationsString);
};

export const getNotifications = async (): Promise<AppNotification[]> => {
  await self.fetchAndStoreNotifications();
  return await self.getNotificationsFromStore();
};

export const retrieveNotifications = async (): Promise<AppNotification[]> => {
  return await self.getNotifications();
};

export const countUnreadNotifications = async (): Promise<number> => {
  const notifications: AppNotification[] = await self.getNotifications();
  const unreadNotifications: AppNotification[] = notifications.filter(
    (notification) => !notification.read
  );
  return unreadNotifications.length;
};

export const readNotification = async (
  notificationId: string
): Promise<AppNotification | undefined> => {
  try {
    const payload = {
      read: true,
    };
    const headers = {
      'Content-Type': 'application/json',
    };
    const response = await apiFetch(
      `/api/v1/users/notification/${notificationId}/read`,
      {
        method: 'PATCH',
        headers,
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

export const notificationEventsSocket = (
  onmessage: (event: MessageEvent) => void
): WebSocket => {
  const ws = new WebSocket(
    `${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`
  );
  console.log(
    'Opened the websocket on:',
    `${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`
  );
  ws.onmessage = onmessage;
  return ws;
};

export const enableNotificationsAndUpdateLocalStorage = async () => {
  await enableNotificationsForDesktop();
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

export const enableNotificationsForDesktop = async (): Promise<Registration | null> => {
  if (typeof Notification === 'undefined') {
    console.error('Notification API is not available in this browser');
    return null;
  }
  const permissionGranted = await Notification.requestPermission();
  const serviceWorkerRegistration = await getServiceWorkerRegistration();
  if (!permissionGranted || !serviceWorkerRegistration) {
    console.log(
      'No notification: missing permission or missing service worker registration'
    );
  } else {
    const pushSubscription = await subscribePush();
    if (pushSubscription) {
      let registration: Registration | null;
      registration = await registerDevice(pushSubscription);
      if (registration) {
        localStorage.setItem('registration_id', registration.id);
        localStorage.setItem('notifications_enabled', 'true');
      }
      return registration;
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

export const disableNotificationsAtLogout = async () => {
  // const deviceId = window.NativeInfos?.getInfos();
  const deviceId = null;
  if (isNative() && deviceId !== null) {
    console.log(
      'Disabling notifications on mobile app and unregistering device. deviceId when logging out:',
      deviceId
    );
    await disableNotificationsForNative(deviceId);
  } else {
    const registrationId = localStorage.getItem('registration_id');
    if (registrationId) {
      console.log(
        'Disabling notifications on desktop and unregistering device. registration_id when logging out:',
        registrationId
      );
      await disableNotificationsForDesktop(registrationId);
    }
  }
};

export const disableNotificationsForNative = async (deviceId: string) => {
  await unregisterDevice(deviceId);
};

export const disableNotificationsForDesktop = async (registrationId: string) => {
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
      await unregisterDesktopRegistration(registrationId);
      await unsubscribePush(pushSubscription);
    }
  }
};

const getServiceWorkerRegistration = async () => {
  return await navigator.serviceWorker.ready;
};
