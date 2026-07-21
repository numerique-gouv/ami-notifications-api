import { apiFetch } from '$lib/auth';

export type APIFollowupItemEvent = {
  id: string;
  created_at: Date;
  description: string;
};

export type APIFollowupItem = {
  partner_id: string;
  item_type: string;
  item_external_id: string;
  status_id: string;
  status_label: string;
  milestone_start_date: Date | null;
  milestone_end_date: Date | null;
  events: APIFollowupItemEvent[];

  title: string;
  subheading: string;
  description: string;
  icon: string;
  external_url: string | null;
  is_archived: boolean;

  created_at: Date;
  updated_at: Date;
};

export type APIFollowup = {
  notifications: APIFollowupItem[];
};

export const retrieveFollowup = async (
  date: Date | null = null
): Promise<APIFollowup> => {
  const now = date || new Date();
  const filter_items = [];
  const apiFollowupData = {
    notifications: localStorage.getItem('notifications_followup_source') || '{}',
  };
  type APIFollowupKey = keyof typeof apiFollowupData;
  for (const key of Object.keys(apiFollowupData) as APIFollowupKey[]) {
    try {
      const data = JSON.parse(apiFollowupData[key]);
      if (!data || data.status !== 'success') {
        filter_items.push(key);
        continue;
      }
      if (!data.expires_at) {
        filter_items.push(key);
        continue;
      }
      const expires_at = new Date(data.expires_at);
      if (expires_at < now) {
        filter_items.push(key);
      }
    } catch {
      filter_items.push(key);
    }
  }
  if (filter_items.length) {
    const items = (filter_items || []).map((e) => `filter-items=${e}`).join('&');
    const response = await apiFetch(`/api/v1/users/data/followup?${items}`, {
      credentials: 'include',
    });
    if (response.ok) {
      const apiFollowup = await response.json();
      for (const key of Object.keys(apiFollowupData) as APIFollowupKey[]) {
        if (!filter_items.includes(key)) {
          continue;
        }
        // store result if status is 'success'
        if (apiFollowup[key].status === 'success') {
          const new_data = JSON.stringify(apiFollowup[key]);
          apiFollowupData[key] = new_data;
          localStorage.setItem(`${key}_followup_source`, new_data);
        }
      }
    }
  }
  const apiFollowup = {
    notifications:
      JSON.parse(apiFollowupData.notifications).items || ([] as APIFollowupItem[]),
  } as APIFollowup;
  for (const items of Object.values(apiFollowup)) {
    items.forEach((item) => {
      // convert dates
      item.created_at = new Date(item.created_at);
      item.updated_at = new Date(item.updated_at);
      item.milestone_start_date = item.milestone_start_date
        ? new Date(item.milestone_start_date)
        : null;
      item.milestone_end_date = item.milestone_end_date
        ? new Date(item.milestone_end_date)
        : null;
    });
  }
  return apiFollowup;
};

export const archiveFollowupItem = async (
  source: string,
  external_id: string
): Promise<boolean> => {
  try {
    const payload = {
      is_archived: true,
    };
    const headers = {
      'Content-Type': 'application/json',
    };
    const response = await apiFetch(
      `/api/v1/users/data/followup/item/${source}/${external_id}/archive`,
      {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        credentials: 'include',
      }
    );
    if (response.status === 200) {
      return true;
    }
  } catch (error) {
    console.error(error);
  }
  return false;
};
