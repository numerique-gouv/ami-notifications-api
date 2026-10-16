import { apiFetch } from '$lib/auth';

export type APIPersonalDataConsent = {
  consent_datetime: Date | null;
};

export const retrievePersonalDataConsent =
  async (): Promise<APIPersonalDataConsent> => {
    let apiPersonalDataConsent = {} as APIPersonalDataConsent;

    try {
      const response = await apiFetch('/api/v1/users/personal-data-consent');
      if (response.status === 200) {
        apiPersonalDataConsent = await response.json();
        localStorage.setItem(
          'personal-data-consent',
          JSON.stringify(apiPersonalDataConsent)
        );
      }
    } catch (error) {
      console.error(error);
    }
    apiPersonalDataConsent = JSON.parse(
      localStorage.getItem('personal-data-consent') || '{"consent_datetime":null}'
    );

    return apiPersonalDataConsent;
  };

export const updateApiPersonalDataConsent = async (
  checked: boolean
): Promise<boolean> => {
  const payload = {
    consent: checked,
  };
  try {
    const response = await apiFetch(`/api/v1/users/personal-data-consent`, {
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
