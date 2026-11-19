import { apiFetch } from '$lib/auth';

export type Registration = {
  id: string;
  user_id: string;
  device_id: string | null;
  subscription: PushSubscription;
  created_at: Date | string;
};

export const unregisterRegistrationsForNative = async (deviceId: string) => {
  const payload = {
    device_id: deviceId,
  };
  const headers = {
    'Content-Type': 'application/json',
  };
  const response = await apiFetch(
    '/api/v1/users/registrations?action=removeFromDeviceId',
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(payload),
    }
  );
  console.log('response:', response);
  if (response.status < 400) {
    console.log('The device has been deleted successfully');
  } else {
    console.log(`error ${response.status}: ${response.statusText}, ${response.body}`);
  }
  return response.status;
};
