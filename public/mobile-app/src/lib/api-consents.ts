import { apiFetch } from '$lib/auth';

export type APIConsentsItem = {
  partner_id: string;
  consent_datetime: Date | null;
};

export type APIConsents = {
  consents: APIConsentsItem[];
};

export const retrieveConsents = async (): Promise<APIConsents> => {
  const apiConsents = {
    consents: [] as APIConsentsItem[],
  } as APIConsents;

  try {
    const response = await apiFetch('/api/v1/users/consents');
    if (response.status === 200) {
      apiConsents.consents = await response.json();
    }
  } catch (error) {
    console.error(error);
  }

  return apiConsents;
};

export const updateApiConsent = async (partnerId: string, checked: boolean) => {
  const payload = {
    partner_id: partnerId,
    consent: checked,
  };
  try {
    const response = await apiFetch(`/api/v1/users/consents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (response.status === 200) {
      return true;
    }
  } catch (error) {
    console.error(error);
  }
  return false;
};
