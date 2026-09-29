import type { APIPersonalDataConsent } from '$lib/api-personal-data-consent';
import {
  retrievePersonalDataConsent,
  updateApiPersonalDataConsent,
} from '$lib/api-personal-data-consent';

export class PersonalDataConsent {
  private _consent_datetime: Date | null = null;

  constructor(apiPersonalDataConsent: APIPersonalDataConsent | null = null) {
    if (apiPersonalDataConsent) {
      this._consent_datetime = apiPersonalDataConsent.consent_datetime;
    } else {
      this._consent_datetime = null;
    }
  }

  get consent_datetime(): Date | null {
    return this._consent_datetime;
  }

  updateConsent = async (checked: boolean): Promise<boolean> => {
    return await updateApiPersonalDataConsent(checked);
  };
}

export const buildPersonalDataConsent = async (): Promise<PersonalDataConsent> => {
  const apiPersonalDataConsent: APIPersonalDataConsent =
    await retrievePersonalDataConsent();
  return new PersonalDataConsent(apiPersonalDataConsent);
};
