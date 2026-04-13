import { apiFetch } from '$lib/auth';

export type ScheduledNotification = {
  content_title: string;
  content_body: string;
  content_icon: string;
  reference: string;
  internal_url: string;
  scheduled_at: Date;
};

export const createScheduledNotification = async (
  scheduledNotification: ScheduledNotification
): Promise<boolean> => {
  try {
    const headers = {
      'Content-Type': 'application/json',
    };
    const response = await apiFetch(`/api/v1/users/scheduled-notifications`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(scheduledNotification),
      credentials: 'include',
    });
    if (response.status === 200) {
      return true;
    }
  } catch (error) {
    console.error(error);
  }
  return false;
};
