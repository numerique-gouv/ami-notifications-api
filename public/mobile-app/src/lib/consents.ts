import type { APIConsents, APIConsentsItem } from '$lib/api-consents';
import { retrieveConsents, updateApiConsent } from '$lib/api-consents';

export class ConsentsItem {
  constructor(
    private _partner_id: string,
    private _consent_datetime: Date | null = null
  ) {}

  equals(other: ConsentsItem): boolean {
    if (!(other instanceof ConsentsItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get partner_id(): string {
    return this._partner_id;
  }

  get consent_datetime(): Date | null {
    return this._consent_datetime;
  }
}

export class Consents {
  private _items: ConsentsItem[] = [];

  constructor(apiConsents: APIConsents | null = null) {
    const consentsItems: ConsentsItem[] = [];

    const items: APIConsentsItem[] = apiConsents?.consents || [];

    items.forEach((item) => {
      const consentsItem = this.createConsentsItem(item);
      consentsItems.push(consentsItem);
    });

    consentsItems.sort((a, b) => a.partner_id.localeCompare(b.partner_id, 'fr'));

    consentsItems.forEach((consentsItem) => {
      this._items.push(consentsItem);
    });
  }

  get items(): ConsentsItem[] {
    return this._items;
  }

  private createConsentsItem(item: APIConsentsItem): ConsentsItem {
    return new ConsentsItem(item.partner_id, item.consent_datetime);
  }

  hasAnyConsents() {
    if (this.items) {
      return this.items.some((item) => item.consent_datetime !== null);
    }
    return false;
  }
}

export const buildConsents = async (): Promise<Consents> => {
  const apiConsents: APIConsents = await retrieveConsents();
  return new Consents(apiConsents);
};

export const updateConsent = async (partnerId: string, checked: boolean) => {
  await updateApiConsent(partnerId, checked);
};
