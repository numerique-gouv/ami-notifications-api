import { apiFetch } from '$lib/auth';

export type APIServicesItem = {
  partner_id: string;
  item_type: string;
  title: string;
  short_description: string;
  description: string;
  url: string;
  with_silent_login: boolean;
};

export type APIServices = {
  internal: APIServicesItem[];
};

export const retrieveServices = async (
  date: Date | null = null
): Promise<APIServices> => {
  const now = date || new Date();
  const filter_items = [];
  const apiServicesData = {
    internal: localStorage.getItem('internal_services_source') || '{}',
  };
  type APIServicesKey = keyof typeof apiServicesData;
  for (const key of Object.keys(apiServicesData) as APIServicesKey[]) {
    try {
      const data = JSON.parse(apiServicesData[key]);
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
    const response = await apiFetch(`/api/v1/users/data/services?${items}`, {
      credentials: 'include',
    });
    if (response.ok) {
      const apiServices = await response.json();
      for (const key of Object.keys(apiServicesData) as APIServicesKey[]) {
        if (!filter_items.includes(key)) {
          continue;
        }
        // store result if status is 'success'
        if (apiServices[key].status === 'success') {
          const new_data = JSON.stringify(apiServices[key]);
          apiServicesData[key] = new_data;
          localStorage.setItem(`${key}_services_source`, new_data);
        }
      }
    }
  }
  const apiServices = {
    internal: JSON.parse(apiServicesData.internal).items || ([] as APIServicesItem[]),
  } as APIServices;
  return apiServices;
};

const PARAMETER_DEFINITIONS = {
  otv_jwt_token: {} as {
    preferred_username: string;
    email: string;
    address_city: string;
    address_postcode: string;
    address_name: string;
  },
};

export type ParameterKey = keyof typeof PARAMETER_DEFINITIONS;

export const PARAMETER_KEYS = Object.keys(PARAMETER_DEFINITIONS) as ParameterKey[];

export function isParameterKey(key: string): key is ParameterKey {
  return (PARAMETER_KEYS as string[]).includes(key);
}

export type Parameter = {
  [key in ParameterKey]: {
    parameter: key;
    values: (typeof PARAMETER_DEFINITIONS)[key];
  };
}[ParameterKey];

export type ServicesItemsParameters = {
  [key: string]: string;
};

interface ServicesItemsParametersResponse {
  data: ServicesItemsParameters;
}

export const getServicesItemParameters = async (
  parameters: Parameter[]
): Promise<ServicesItemsParameters> => {
  try {
    const response = await apiFetch('/api/v1/users/data/services/item/parameters', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ parameters: parameters }),
      credentials: 'include',
    });
    if (response.status === 200) {
      const result = (await response.json()) as ServicesItemsParametersResponse;
      return result.data;
    }
    return {};
  } catch (error) {
    console.error(error);
    return {};
  }
};
