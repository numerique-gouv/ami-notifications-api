import type { APIConsents, APIConsentsItem } from '$lib/api-consents';
import {
  retrieveConsents,
  updateAllApiConsents,
  updateApiConsent,
} from '$lib/api-consents';
import type { Followup, FollowupItem } from '$lib/followup';

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

  constructor(apiConsents: APIConsents | null = null, partnerIds: string[]) {
    const consentsItems: ConsentsItem[] = [];

    const items: APIConsentsItem[] = apiConsents?.consents || [];

    partnerIds.forEach((partnerId) => {
      const item: APIConsentsItem | undefined = items.find(
        (item) => item.partner_id === partnerId
      );
      let consentsItem: ConsentsItem;
      if (item) {
        consentsItem = this.createConsentsItem(item);
      } else {
        consentsItem = this.createFakeConsentsItem(partnerId);
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
    return new ConsentsItem(item.partner_id, item.consent_datetime);
  }

  private createFakeConsentsItem(partnerId: string): ConsentsItem {
    return new ConsentsItem(partnerId, null);
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

export const buildConsents = async (partnerIds: string[]): Promise<Consents> => {
  const apiConsents: APIConsents = await retrieveConsents();
  return new Consents(apiConsents, partnerIds);
};

export const updateConsent = async (partnerId: string, checked: boolean) => {
  await updateApiConsent(partnerId, checked);
};

export const updateAllConsents = async (checked: boolean) => {
  await updateAllApiConsents(checked);
};
