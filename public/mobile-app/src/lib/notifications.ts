import { PUBLIC_APP_URL } from '$env/static/public';
import { apiFetch } from '$lib/auth';
import { getDeviceId } from '$lib/bridges/nativeInfos';
import { unregisterRegistrationsForNative } from '$lib/registration';
import * as telemetry from '$lib/telemetry';
import * as self from './notifications';

export const PUBLIC_APP_WS_URL = PUBLIC_APP_URL.replace('https://', 'wss://').replace(
  'http://',
  'ws://'
);

export type AppNotification = {
  id: string;
  created_at: Date;
  content_title: string;
  content_body: string;
  content_icon: string;
  partner_id: string;
  item_type: string | null;
  item_id: string | null;
  item_parent_partner_id: string | null;
  item_parent_type: string | null;
  item_parent_id: string | null;
  url: string;
  read: boolean;
};

export const fetchAndStoreNotifications = async () => {
  let notifications = [] as AppNotification[];

  try {
    const response = await apiFetch('/api/v1/users/notifications');
    if (response.status === 200) {
      notifications = await response.json();
      localStorage.setItem('notifications', JSON.stringify(notifications));
    }
  } catch (error) {
    console.error(error);
  }
};

export const getNotificationsFromStore = (): AppNotification[] => {
  const notificationsString: string = localStorage.getItem('notifications') || '[]';
  return JSON.parse(notificationsString);
};

export const getNotifications = async (): Promise<AppNotification[]> => {
  await self.fetchAndStoreNotifications();
  return self.getNotificationsFromStore();
};

export const retrieveNotifications = async (): Promise<AppNotification[]> => {
  return await self.getNotifications();
};

export const countUnreadNotificationsFromStore = (): number => {
  const notifications: AppNotification[] = self.getNotificationsFromStore();
  const unreadNotifications: AppNotification[] = notifications.filter(
    (notification) => !notification.read
  );
  return unreadNotifications.length;
};

export const countUnreadNotifications = async (): Promise<number> => {
  await self.fetchAndStoreNotifications();
  return self.countUnreadNotificationsFromStore();
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
  telemetry.trace('notificationEventsSocket');
  const ws = new WebSocket(
    `${PUBLIC_APP_WS_URL}/api/v1/users/notification/events/stream`
  );
  console.log(
    'Opened the websocket on:',
    `${PUBLIC_APP_WS_URL}/api/v1/users/notification/events/stream`
  );
  ws.onmessage = onmessage;
  return ws;
};

export const disableNotificationsAtLogout = async () => {
  const deviceId = getDeviceId();
  if (deviceId !== '') {
    console.log(
      'Disabling notifications on mobile app and unregistering device. deviceId when logging out:',
      deviceId
    );
    await unregisterRegistrationsForNative(deviceId);
  }
};
