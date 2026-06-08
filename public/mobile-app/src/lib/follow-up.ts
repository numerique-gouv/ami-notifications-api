import type { Inventory, InventoryItem } from '$lib/api-inventory';
import { retrieveInventory } from '$lib/api-inventory';

type Status = 'new' | 'wip' | 'closed';

export class RequestItem {
  constructor(
    private _id: string,
    private _inventory: string,

    private _title: string,
    private _description: string,

    private _date: Date,

    private _status_id: Status,
    private _status_label: string,
    private _is_archived: boolean,

    private _link: string | null
  ) {}

  equals(other: RequestItem): boolean {
    if (!(other instanceof RequestItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get id(): string {
    return this._id;
  }

  get inventory(): string {
    return this._inventory;
  }

  get title(): string {
    return this._title;
  }

  get description(): string {
    return this._description;
  }

  get date(): Date {
    return this._date;
  }

  get status_id(): string {
    return this._status_id;
  }

  get status_label(): string {
    return this._status_label;
  }

  get is_archived(): boolean {
    return this._is_archived;
  }

  get link(): string | null {
    return this._link;
  }

  private static readonly StatusInfo: Record<Status, { icon: string }> = {
    new: {
      icon: 'fr-icon-mail-fill',
    },
    wip: {
      icon: 'fr-icon-eye-fill',
    },
    closed: {
      icon: 'fr-icon-flag-fill',
    },
  };

  get icon(): string {
    const info = RequestItem.StatusInfo[this._status_id];
    if (info === undefined) {
      return '';
    }
    return info.icon;
  }

  get formattedDate(): string {
    const day = this.date.getDate();
    const month = this.date.toLocaleString('fr-FR', { month: 'long' });
    const hours = String(this.date.getHours()).padStart(2, '0');
    const minutes = String(this.date.getMinutes()).padStart(2, '0');
    return `le ${day} ${month} à ${hours}H${minutes}`;
  }
}

export class FollowUp {
  private _items: RequestItem[] = [];
  private _archived_items: RequestItem[] = [];

  constructor(inventory: Inventory | null = null) {
    const requestItems: RequestItem[] = [];

    const inventoryItems: InventoryItem[] = inventory?.notifications || [];

    // build items
    inventoryItems.forEach((inventoryItem) => {
      const requestItem = this.createRequestItem(inventoryItem);
      requestItems.push(requestItem);
    });

    // sort items by date
    requestItems.sort((a, b) => b.date.getTime() - a.date.getTime());

    // organize items in _items or _archived_items arrays
    requestItems.forEach((requestItem) => {
      if (requestItem.is_archived) {
        this._archived_items.push(requestItem);
      } else {
        this._items.push(requestItem);
      }
    });
  }

  private createRequestItem(inventoryItem: InventoryItem): RequestItem {
    return new RequestItem(
      inventoryItem.external_id,
      'notifications',
      inventoryItem.title,
      inventoryItem.description,
      inventoryItem.updated_at,
      inventoryItem.status_id as Status,
      inventoryItem.status_label,
      inventoryItem.is_archived,
      inventoryItem.external_url
    );
  }

  get items(): RequestItem[] {
    return this._items;
  }

  get archived_items(): RequestItem[] {
    return this._archived_items;
  }
}

export const buildFollowUp = async (): Promise<FollowUp> => {
  const inventory: Inventory = await retrieveInventory();
  return new FollowUp(inventory);
};
