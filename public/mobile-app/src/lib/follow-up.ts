import type { Inventory, InventoryItem } from '$lib/api-followup';
import { archiveFollowUpItem, retrieveFollowUp } from '$lib/api-followup';

type Status = 'new' | 'wip' | 'closed';

export class RequestItem {
  constructor(
    private _partner_id: string,
    private _external_item_type: string,
    private _external_item_id: string,
    private _inventory: string,

    private _title: string,
    private _description: string,
    private _icon: string,

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
    return `${this.partner_id}:${this.external_item_type}:${this.external_item_id}`;
  }

  get partner_id(): string {
    return this._partner_id;
  }

  get external_item_type(): string {
    return this._external_item_type;
  }

  get external_item_id(): string {
    return this._external_item_id;
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

  get icon(): string {
    return this._icon;
  }

  get formattedDate(): string {
    const day = this.date.getDate();
    const month = this.date.toLocaleString('fr-FR', { month: 'long' });
    const hours = String(this.date.getHours()).padStart(2, '0');
    const minutes = String(this.date.getMinutes()).padStart(2, '0');
    return `le ${day} ${month} à ${hours}H${minutes}`;
  }

  async archive(): Promise<boolean> {
    const result = await archiveFollowUpItem(this.inventory, this.id);
    return result;
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
      inventoryItem.partner_id,
      inventoryItem.external_item_type,
      inventoryItem.external_item_id,
      'notifications',
      inventoryItem.title,
      inventoryItem.description,
      inventoryItem.icon,
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

  hasNonArchivedItems(partner_id: string, external_item_type: string): boolean {
    return this.items.some(
      (item) =>
        item.partner_id === partner_id && item.external_item_type === external_item_type
    );
  }
}

export const buildFollowUp = async (): Promise<FollowUp> => {
  const inventory: Inventory = await retrieveFollowUp();
  return new FollowUp(inventory);
};
