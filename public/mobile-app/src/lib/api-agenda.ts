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

export type APIAgendaItems = {
  school_holidays: APIAgendaItem[];
  public_holidays: APIAgendaItem[];
  elections: APIAgendaItem[];
};

export const retrieveAgenda = async (
  date: Date | null = null
): Promise<APIAgendaItems> => {
  const now = new Date(date || '');
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);
  const current_date = dateToISO(today);
  const filter_items = [];
  const agendaItemsData = {
    school_holidays: localStorage.getItem('school_holidays_agenda_items') || '{}',
    public_holidays: localStorage.getItem('public_holidays_agenda_items') || '{}',
    elections: localStorage.getItem('elections_agenda_items') || '{}',
  };
  type APIAgendaItemsKey = keyof typeof agendaItemsData;
  for (const key of Object.keys(agendaItemsData) as APIAgendaItemsKey[]) {
    try {
      const data = JSON.parse(agendaItemsData[key]);
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
      `/api/v1/users/agenda/items?current_date=${current_date}&${items}`,
      {
        credentials: 'include',
      }
    );
    if (response.ok) {
      const agendaItems = await response.json();
      for (const key of Object.keys(agendaItemsData) as APIAgendaItemsKey[]) {
        if (!filter_items.includes(key)) {
          continue;
        }
        // store result if status is 'success'
        if (agendaItems[key].status === 'success') {
          const new_data = JSON.stringify(agendaItems[key]);
          agendaItemsData[key] = new_data;
          localStorage.setItem(`${key}_agenda_items`, new_data);
        }
      }
    }
  }
  const agendaItems = {
    school_holidays:
      JSON.parse(agendaItemsData.school_holidays).items || ([] as APIAgendaItem[]),
    public_holidays:
      JSON.parse(agendaItemsData.public_holidays).items || ([] as APIAgendaItem[]),
    elections: JSON.parse(agendaItemsData.elections).items || ([] as APIAgendaItem[]),
  } as APIAgendaItems;
  for (const items of Object.values(agendaItems)) {
    items.forEach((item) => {
      // convert dates
      item.date = item.date ? new Date(item.date) : null;
      item.start_date = item.start_date ? new Date(item.start_date) : null;
      item.end_date = item.end_date ? new Date(item.end_date) : null;
    });
  }
  return agendaItems;
};
