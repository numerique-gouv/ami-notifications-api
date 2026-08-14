import type { APIFollowup, APIFollowupItem } from '$lib/api-followup';
import { archiveFollowupItem, retrieveFollowup } from '$lib/api-followup';

export type Status = 'new' | 'wip' | 'closed';

export class FollowupItemEvent {
  constructor(
    private _id: string,
    private _created_at: Date,
    private _description: string
  ) {}

  get id(): string {
    return this._id;
  }

  get created_at(): Date {
    return this._created_at;
  }

  get description(): string {
    return this._description;
  }

  get formattedDate(): string {
    const day = String(this.created_at.getDate()).padStart(2, '0');
    const month = this.created_at.toLocaleString('fr-FR', { month: 'long' });
    const year = this.created_at.getFullYear();
    const hours = String(this.created_at.getHours()).padStart(2, '0');
    const minutes = String(this.created_at.getMinutes()).padStart(2, '0');
    return `${day} ${month} ${year} - ${hours}:${minutes}`;
  }
}

export class FollowupSubItem {
  constructor(
    private _partner_id: string,
    private _item_type: string,
    private _item_external_id: string,
    private _reference: string,
    private _source: string,
    private _events: FollowupItemEvent[],

    private _title: string,
    private _subheading: string,
    private _description: string,
    private _icon: string,

    private _date: Date,

    private _status_id: Status,
    private _status_label: string,
    private _is_archived: boolean,

    private _link: string | null
  ) {}

  get id(): string {
    return `${this.partner_id}:${this.item_type}:${this.item_external_id}`;
  }

  get partner_id(): string {
    return this._partner_id;
  }

  get item_type(): string {
    return this._item_type;
  }

  get item_external_id(): string {
    return this._item_external_id;
  }

  get reference(): string {
    return this._reference;
  }

  get source(): string {
    return this._source;
  }

  get events(): FollowupItemEvent[] {
    return this._events;
  }

  get title(): string {
    return this._title;
  }

  get subheading(): string {
    return this._subheading;
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

  get itemDetailPageUrl(): string {
    return `/#/followup/item/${this.partner_id}/${this.item_type}/${this.item_external_id}`;
  }

  async archive(): Promise<boolean> {
    const result = await archiveFollowupItem(this.source, this.id);
    return result;
  }
}

export class FollowupItem extends FollowupSubItem {
  constructor(
    _partner_id: string,
    _item_type: string,
    _item_external_id: string,
    _reference: string,
    _source: string,
    _events: FollowupItemEvent[],

    _title: string,
    _subheading: string,
    _description: string,
    _icon: string,

    _date: Date,

    _status_id: Status,
    _status_label: string,
    _is_archived: boolean,

    _link: string | null,

    private _sub_items: FollowupSubItem[]
  ) {
    super(
      _partner_id,
      _item_type,
      _item_external_id,
      _reference,
      _source,
      _events,
      _title,
      _subheading,
      _description,
      _icon,
      _date,
      _status_id,
      _status_label,
      _is_archived,
      _link
    );
  }

  equals(other: FollowupItem): boolean {
    if (!(other instanceof FollowupItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get sub_items(): FollowupSubItem[] {
    return this._sub_items;
  }
}

export class Followup {
  private _items: FollowupItem[] = [];
  private _archived_items: FollowupItem[] = [];

  constructor(apiFollowup: APIFollowup | null = null) {
    const followupItems: FollowupItem[] = [];

    const items: APIFollowupItem[] = apiFollowup?.notifications || [];

    // build items
    items.forEach((item) => {
      const followupItem = this.createFollowupItem(item);
      followupItems.push(followupItem);
    });

    // sort items by date
    followupItems.sort((a, b) => b.date.getTime() - a.date.getTime());

    // organize items in _items or _archived_items arrays
    followupItems.forEach((followupItem) => {
      if (followupItem.is_archived) {
        this._archived_items.push(followupItem);
      } else {
        this._items.push(followupItem);
      }
    });
  }

  private createFollowupItem(item: APIFollowupItem): FollowupItem {
    const events: FollowupItemEvent[] = item.events.map(
      (event) =>
        new FollowupItemEvent(event.id, new Date(event.created_at), event.description)
    );

    const sub_items: FollowupSubItem[] = item.sub_items.map((sub_item) => {
      const sub_item_events: FollowupItemEvent[] = sub_item.events.map(
        (event) =>
          new FollowupItemEvent(event.id, new Date(event.created_at), event.description)
      );
      return new FollowupSubItem(
        sub_item.partner_id,
        sub_item.item_type,
        sub_item.item_external_id,
        sub_item.reference,
        'notifications',
        sub_item_events,
        sub_item.title,
        sub_item.subheading,
        sub_item.description,
        sub_item.icon,
        sub_item.updated_at,
        sub_item.status_id as Status,
        sub_item.status_label,
        sub_item.is_archived,
        sub_item.external_url
      );
    });

    return new FollowupItem(
      item.partner_id,
      item.item_type,
      item.item_external_id,
      item.reference,
      'notifications',
      events,
      item.title,
      item.subheading,
      item.description,
      item.icon,
      item.updated_at,
      item.status_id as Status,
      item.status_label,
      item.is_archived,
      item.external_url,
      sub_items
    );
  }

  get items(): FollowupItem[] {
    return this._items;
  }

  get archived_items(): FollowupItem[] {
    return this._archived_items;
  }

  hasNonArchivedItems(partner_id: string, item_type: string): boolean {
    return this.items.some(
      (item) => item.partner_id === partner_id && item.item_type === item_type
    );
  }
}

export const buildFollowup = async (): Promise<Followup> => {
  const apiFollowup: APIFollowup = await retrieveFollowup();
  return new Followup(apiFollowup);
};
