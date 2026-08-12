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

  get id(): string {
    return `${this.partner_id}:${this.consent_datetime}`;
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

    // build items
    items.forEach((item) => {
      const consentsItem = this.createConsentsItem(item);
      consentsItems.push(consentsItem);
    });

    // sort items by title
    consentsItems.sort((a, b) => a.partner_id.localeCompare(b.partner_id, 'fr'));

    // organize items in _items or
    consentsItems.forEach((consentsItem) => {
      this._items.push(consentsItem);
    });
  }

  private createConsentsItem(item: APIConsentsItem): ConsentsItem {
    return new ConsentsItem(item.partner_id, item.consent_datetime);
  }

  get items(): ConsentsItem[] {
    return this._items;
  }

  find(partner_id: string): ConsentsItem | null {
    const found = this.items.filter((item) => item.partner_id === partner_id);
    if (found.length === 0) {
      console.log(`Can not find ConsentsItem ${partner_id}: no result`);
      return null;
    }
    if (found.length > 1) {
      console.log(`Can not find ConsentsItem ${partner_id}: many results`);
      return null;
    }
    return found[0];
  }
}

export const buildConsents = async (): Promise<Consents> => {
  const apiConsents: APIConsents = await retrieveConsents();
  return new Consents(apiConsents);
};

export const updateConsent = async (id: string, checked: boolean) => {
  const today: Date | null = checked ? new Date() : null;
  const consentsItem: ConsentsItem = new ConsentsItem(id, today);

  await updateApiConsent(consentsItem);
};
