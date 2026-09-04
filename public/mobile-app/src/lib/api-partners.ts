import { apiFetch } from '$lib/auth';

export type APIPartnersItem = {
  slug: string;
  name: string;
  link: string;
};

export type APIPartners = {
  partners: APIPartnersItem[];
};

export const retrievePartners = async (): Promise<APIPartners> => {
  let apiPartners = {
    partners: [] as APIPartnersItem[],
  } as APIPartners;

  try {
    const response = await apiFetch('/api/v1/users/data/partners');
    if (response.status === 200) {
      apiPartners.partners = await response.json();
      localStorage.setItem('partners', JSON.stringify(apiPartners));
    }
  } catch (error) {
    console.error(error);
  }
  apiPartners = JSON.parse(localStorage.getItem('partners') || '{"partners":[]}');

  return apiPartners;
};
