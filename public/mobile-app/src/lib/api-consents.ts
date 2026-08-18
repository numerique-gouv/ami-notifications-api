import { apiFetch } from '$lib/auth';
import type { ConsentsItem } from '$lib/consents';

export type APIConsentsItem = {
  partner_id: string;
  consent_datetime: Date;
};

export type APIConsents = {
  consents: APIConsentsItem[];
};

export const retrieveConsents = async (): Promise<APIConsents> => {
  const apiConsents = {
    consents: [] as APIConsentsItem[],
  } as APIConsents;

  try {
    const response = await apiFetch('/api/v1/users/consents', {
      credentials: 'include',
    });
    if (response.status === 200) {
      apiConsents.consents = await response.json();
    }
  } catch (error) {
    console.error(error);
  }

  return apiConsents;
};

export const updateApiConsent = async (consentsItem: ConsentsItem) => {
  const payload = {
    partner_id: consentsItem.partner_id,
    consent_datetime: consentsItem.consent_datetime,
  };
  try {
    const response = await apiFetch(`/api/v1/users/consents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
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
