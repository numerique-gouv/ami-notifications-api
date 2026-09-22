import type { APIConsents, APIConsentsItem } from '$lib/api-consents';
import {
  retrieveConsents,
  updateAllApiConsents,
  updateApiConsent,
} from '$lib/api-consents';
import type { Followup, FollowupItem } from '$lib/followup';
import type { Partners, PartnersItem } from '$lib/partners';

export class ConsentsItem {
  private _partner_id: string;
  private _partner_name: string;
  private _consent_datetime: Date | null = null;

  constructor(partner_id: string, partner_name: string, consent_datetime: Date | null) {
    this._partner_id = partner_id;
    this._partner_name = partner_name;
    this._consent_datetime = consent_datetime;
  }

  equals(other: ConsentsItem): boolean {
    if (!(other instanceof ConsentsItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get partner_id(): string {
    return this._partner_id;
  }

  get partner_name(): string {
    return this._partner_name;
  }

  get consent_datetime(): Date | null {
    return this._consent_datetime;
  }

  hasFollowupItem = (followup: Followup | null) => {
    if (!followup || !followup.items) {
      return false;
    }
    const followupItems: FollowupItem[] | undefined = followup.items?.filter(
      (item) => item.partner_id === this.partner_id
    );
    if (!followupItems) {
      return false;
    }
    return followupItems.length > 0;
  };
}

export class Consents {
  private _items: ConsentsItem[] = [];

  constructor(apiConsents: APIConsents | null = null, partnersItems: PartnersItem[]) {
    const consentsItems: ConsentsItem[] = [];

    const items: APIConsentsItem[] = apiConsents?.consents || [];

    partnersItems.forEach((partnersItem) => {
      const apiConsentsItem: APIConsentsItem | undefined = items.find(
        (item) => item.partner_id === partnersItem.slug
      );
      let consentsItem: ConsentsItem;
      if (apiConsentsItem) {
        consentsItem = this.createConsentsItem(apiConsentsItem);
      } else {
        consentsItem = this.createFakeConsentsItem(partnersItem);
      }
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
    return new ConsentsItem(item.partner_id, item.partner_name, item.consent_datetime);
  }

  private createFakeConsentsItem(partnersItem: PartnersItem): ConsentsItem {
    return new ConsentsItem(partnersItem.slug, partnersItem.name, null);
  }

  hasAnyConsents() {
    if (this.items) {
      return this.items.some((item) => item.consent_datetime !== null);
    }
    return false;
  }

  hasAllConsents() {
    if (this.items.length > 0) {
      return this.items.every((item) => item.consent_datetime !== null);
    }
    return false;
  }
}

export const buildConsents = async (partners: Partners | null): Promise<Consents> => {
  const apiConsents: APIConsents = await retrieveConsents();
  const partnersItems: PartnersItem[] = partners ? partners.items : [];
  return new Consents(apiConsents, partnersItems);
};

export const updateConsent = async (partnerId: string, checked: boolean) => {
  await updateApiConsent(partnerId, checked);
};

export const updateAllConsents = async (checked: boolean) => {
  await updateAllApiConsents(checked);
};
