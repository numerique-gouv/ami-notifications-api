import { apiFetch } from '$lib/auth';
import { dateToISO } from '$lib/utils';

export type APIAgendaItem = {
  kind: string;
  title: string;
  description: string;
  date: Date | null;
  start_date: Date | null;
  end_date: Date | null;
  zones: string[];
  emoji: string;
};

export type APIAgenda = {
  school_holidays: APIAgendaItem[];
  public_holidays: APIAgendaItem[];
  elections: APIAgendaItem[];
};

export const retrieveAgenda = async (date: Date | null = null): Promise<APIAgenda> => {
  const now = new Date(date || '');
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);
  const current_date = dateToISO(today);
  const filter_items = [];
  const apiAgendaData = {
    school_holidays: localStorage.getItem('school_holidays_agenda_source') || '{}',
    public_holidays: localStorage.getItem('public_holidays_agenda_source') || '{}',
    elections: localStorage.getItem('elections_agenda_source') || '{}',
  };
  type APIAgendaKey = keyof typeof apiAgendaData;
  for (const key of Object.keys(apiAgendaData) as APIAgendaKey[]) {
    try {
      const data = JSON.parse(apiAgendaData[key]);
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
    const response = await apiFetch(
      `/api/v1/users/data/agenda?current_date=${current_date}&${items}`,
      {
        credentials: 'include',
      }
    );
    if (response.ok) {
      const apiAgenda = await response.json();
      for (const key of Object.keys(apiAgendaData) as APIAgendaKey[]) {
        if (!filter_items.includes(key)) {
          continue;
        }
        // store result if status is 'success'
        if (apiAgenda[key].status === 'success') {
          const new_data = JSON.stringify(apiAgenda[key]);
          apiAgendaData[key] = new_data;
          localStorage.setItem(`${key}_agenda_source`, new_data);
        }
      }
    }
  }
  const apiAgenda = {
    school_holidays:
      JSON.parse(apiAgendaData.school_holidays).items || ([] as APIAgendaItem[]),
    public_holidays:
      JSON.parse(apiAgendaData.public_holidays).items || ([] as APIAgendaItem[]),
    elections: JSON.parse(apiAgendaData.elections).items || ([] as APIAgendaItem[]),
  } as APIAgenda;
  for (const items of Object.values(apiAgenda)) {
    items.forEach((item) => {
      // convert dates
      item.date = item.date ? new Date(item.date) : null;
      item.start_date = item.start_date ? new Date(item.start_date) : null;
      item.end_date = item.end_date ? new Date(item.end_date) : null;
    });
  }
  return apiAgenda;
};
