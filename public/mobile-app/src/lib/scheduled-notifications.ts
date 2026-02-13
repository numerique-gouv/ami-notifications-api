import { apiFetch } from '$lib/auth';

export type ScheduledNotification = {
  content_title: string;
  content_body: string;
  content_icon: string;
  reference: string;
  scheduled_at: Date;
};

export const createScheduledNotification = async (
  scheduledNotification: ScheduledNotification
): Promise<boolean> => {
  try {
    const response = await apiFetch(`/api/v1/users/scheduled-notifications`, {
      method: 'POST',
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
