import { apiFetch } from '$lib/auth';

export type APIPartnersItem = {
  slug: string;
  name: string;
  link: string;
};

export const retrievePartners = async (
  date: Date | null = null
): Promise<APIPartnersItem[]> => {
  const now = date || new Date();
  const apiPartnersData = localStorage.getItem('partners') || '{}';

  let needCall: boolean = false;
  try {
    const data = JSON.parse(apiPartnersData);
    if (!data || data.status !== 'success') {
      needCall = true;
    } else if (!data.expires_at) {
      needCall = true;
    } else {
      const expires_at = new Date(data.expires_at);
      if (expires_at < now) {
        needCall = true;
      }
    }
  } catch {
    needCall = true;
  }

  if (needCall) {
    try {
      const response = await apiFetch('/api/v1/users/data/partners');
      if (response.status === 200) {
        const result = await response.json();
        localStorage.setItem('partners', JSON.stringify(result));
      }
    } catch (error) {
      console.error(error);
    }
  }
  return JSON.parse(localStorage.getItem('partners') || '{"items":[]}')
    .items as APIPartnersItem[];
};
