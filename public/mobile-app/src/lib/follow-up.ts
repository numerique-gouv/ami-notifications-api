import type { Inventory, InventoryItem } from '$lib/api-inventory';
import { retrieveInventory } from '$lib/api-inventory';

type Status = 'new' | 'wip' | 'closed';

export class RequestItem {
  constructor(
    private _title: string,
    private _description: string,

    private _date: Date,
    private _milestone_end_date: Date | null,

    private _status_id: Status,
    private _status_label: string
  ) {}

  equals(other: RequestItem): boolean {
    if (!(other instanceof RequestItem)) {
      return false;
    }
    return Object.entries(this).every(([key, thisValue]) => {
      const otherValue = other[key as keyof RequestItem];
      // Special handling for Date objects
      if (thisValue instanceof Date || otherValue instanceof Date) {
        return (
          (thisValue as Date | null)?.getTime() ===
          (otherValue as Date | null)?.getTime()
        );
      }
      return thisValue === otherValue;
    });
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

  is_past(): boolean {
    if (this._status_id === 'closed') {
      return true;
    }
    if (this._milestone_end_date && this._milestone_end_date < new Date()) {
      return true;
    }
    return false;
  }

  private static readonly StatusInfo: Record<Status, { icon: string }> = {
    new: {
      icon: 'fr-icon-mail-fill',
    },
    wip: {
      icon: 'fr-icon-eye-fill',
    },
    closed: {
      icon: 'fr-icon-success-fill',
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
  private _current: RequestItem[] = [];
  private _past: RequestItem[] = [];

  constructor(inventory: Inventory | null = null) {
    const requestItems: RequestItem[] = [];

    const inventoryItems: InventoryItem[] = inventory?.psl || [];

    // build items
    inventoryItems.forEach((inventoryItem) => {
      const requestItem = this.createRequestItem(inventoryItem);
      requestItems.push(requestItem);
    });

    // sort items by date
    requestItems.sort((a, b) => a.date.getTime() - b.date.getTime());

    // organize items in _current or _past arrays
    requestItems.forEach((requestItem) => {
      if (requestItem.is_past()) {
        this._past.push(requestItem);
      } else {
        this._current.push(requestItem);
      }
    });
  }

  private createRequestItem(inventoryItem: InventoryItem): RequestItem {
    return new RequestItem(
      inventoryItem.title,
      inventoryItem.description,
      inventoryItem.updated_at,
      inventoryItem.milestone_end_date,
      inventoryItem.status_id as Status,
      inventoryItem.status_label
    );
  }

  get current(): RequestItem[] {
    return this._current;
  }

  get past(): RequestItem[] {
    return this._past;
  }
}

export const buildFollowUp = async (): Promise<FollowUp> => {
  const inventory: Inventory = await retrieveInventory();
  return new FollowUp(inventory);
};
