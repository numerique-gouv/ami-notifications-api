import { Item as AgendaItem } from '$lib/agenda';
import type { APIFollowup, APIFollowupItem } from '$lib/api-followup';
import { archiveFollowupItem, retrieveFollowup } from '$lib/api-followup';
import { uniqueId } from '$lib/utils';
import * as self from './followup';

export type Status = 'new' | 'wip' | 'closed';

const formatDate = (date: Date): string => {
  const day = String(date.getDate()).padStart(2, '0');
  const month = date.toLocaleString('fr-FR', { month: 'long' });
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day} ${month} ${year} - ${hours}:${minutes}`;
};

const capitalizeFirstLetter = (val: string) => {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1);
};

export const getPeriod = (
  start_date: Date | null,
  end_date: Date | null
): string | undefined => {
  if (start_date === null && end_date === null) {
    return undefined;
  }

  const locale = 'fr-FR';
  let startFormat: Intl.DateTimeFormatOptions = {
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  };
  const dateFormat: Intl.DateTimeFormatOptions = startFormat;

  if (end_date === null) {
    const start = start_date?.toLocaleDateString(locale, startFormat);
    return `À partir du ${start}`;
  }

  if (start_date == null) {
    const end = end_date.toLocaleDateString(locale, dateFormat);
    return `Avant le ${end}`;
  }

  if (
    end_date.getTime() === start_date.getTime() ||
    start_date.toLocaleDateString() === end_date.toLocaleDateString()
  ) {
    startFormat = {
      month: 'long',
      day: 'numeric',
      weekday: 'long',
      hour: '2-digit',
      minute: '2-digit',
    };
    const start = start_date.toLocaleDateString(locale, startFormat);
    return capitalizeFirstLetter(start.replace(':', 'h'));
  }

  startFormat = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
  const endFormat = startFormat;
  if (start_date.getFullYear() === end_date.getFullYear()) {
    startFormat = { month: 'long', day: 'numeric', weekday: 'long' };
    if (start_date.getMonth() === end_date.getMonth()) {
      startFormat = { day: 'numeric', weekday: 'long' };
    }
  }
  const start = start_date.toLocaleDateString(locale, startFormat);
  const end = end_date.toLocaleDateString(locale, endFormat);
  return `Du ${start} au ${end}`;
};

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
    return formatDate(this.created_at);
  }
}

export class FollowupSubItem {
  constructor(
    private _partner_id: string,
    private _item_type: string,
    private _item_external_id: string,
    private _reference: string,
    private _source: string,

    private _milestone_start_date: Date | null,
    private _milestone_end_date: Date | null,

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

  equals(other: FollowupSubItem): boolean {
    if (!(other instanceof FollowupSubItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

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

  get milestone_start_date(): Date | null {
    return this._milestone_start_date;
  }

  get milestone_end_date(): Date | null {
    return this._milestone_end_date;
  }

  get duration(): string | undefined {
    if (this.milestone_start_date === null || this.milestone_end_date === null) {
      return undefined;
    }

    if (
      this.milestone_start_date.toLocaleDateString() !==
      this.milestone_end_date.toLocaleDateString()
    ) {
      // not the same days
      return undefined;
    }

    let diff = Math.abs(
      this.milestone_end_date.getTime() - this.milestone_start_date.getTime()
    );
    if (!diff) {
      // exactly same times
      return undefined;
    }

    const units: [string, number][] = [
      ['heure', 1000 * 60 * 60],
      ['minute', 1000 * 60],
      ['seconde', 1000],
    ];

    const parts: string[] = [];

    for (const [label, ms] of units) {
      const value = Math.floor(diff / ms);
      if (value > 0) {
        parts.push(`${value} ${label}${value > 1 ? 's' : ''}`);
        diff -= value * ms;
      }
    }

    return parts.slice(0, 2).join(' et ');
  }

  get period(): string | undefined {
    return self.getPeriod(this.milestone_start_date, this.milestone_end_date);
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
    if (this.hasMilestone()) {
      return 'Personnel';
    }
    return this._status_label;
  }

  get is_archived(): boolean {
    return this._is_archived;
  }

  get link(): string | null {
    return this._link;
  }

  get icon(): string {
    if (this.hasMilestone()) {
      return 'fr-icon-user-fill';
    }
    return this._icon;
  }

  get formattedDate(): string {
    return formatDate(this.date);
  }

  get badgeClassName(): string {
    if (this.hasMilestone()) {
      return 'am-badge--user';
    }
    switch (this._status_id) {
      case 'new':
        return 'fr-background-contrast--yellow-moutarde fr-text-label--yellow-moutarde';
      case 'wip':
        return 'fr-text-default--info fr-background-contrast--info';
      case 'closed':
        return 'fr-badge--purple-glycine';
      default:
        return '';
    }
  }

  getItemDetailPageUrl(item: FollowupItem): string {
    return `/#/followup/item/${item.partner_id}/${item.item_type}/${item.item_external_id}/subitem/${this.partner_id}/${this.item_type}/${this.item_external_id}`;
  }

  buildAgendaItem(item: FollowupItem): AgendaItem | null {
    if (!this.hasMilestone()) {
      return null;
    }
    return new AgendaItem(
      uniqueId(),
      'personal',
      this.title,
      this.getItemDetailPageUrl(item),
      null,
      null,
      this.milestone_start_date,
      this.milestone_end_date
    );
  }

  hasMilestone(): boolean {
    return this.milestone_start_date !== null || this.milestone_end_date !== null;
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

    _milestone_start_date: Date | null,
    _milestone_end_date: Date | null,

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
      _milestone_start_date,
      _milestone_end_date,
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

  get wipSubItems(): FollowupSubItem[] {
    return this.sub_items.filter((sub_item) => sub_item.status_id !== 'closed');
  }

  get closedSubItems(): FollowupSubItem[] {
    return this.sub_items.filter((sub_item) => sub_item.status_id === 'closed');
  }

  get subItemWithoutMilestone(): FollowupSubItem[] {
    return this.sub_items.filter((sub_item) => !sub_item.hasMilestone());
  }

  get pastSubItemWithMilestone(): FollowupSubItem[] {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return this.sub_items.filter(
      (sub_item) =>
        sub_item.milestone_end_date !== null && sub_item.milestone_end_date < today
    );
  }

  get futureSubItemWithMilestone(): FollowupSubItem[] {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return this.sub_items.filter(
      (sub_item) =>
        sub_item.milestone_end_date === null || sub_item.milestone_end_date >= today
    );
  }

  getItemDetailPageUrl(): string {
    return `/#/followup/item/${this.partner_id}/${this.item_type}/${this.item_external_id}`;
  }

  findSubItem(
    subpartner_id: string,
    subitem_type: string,
    subitem_external_id: string
  ): FollowupSubItem | null {
    return (
      this.sub_items.find(
        (sub_item) =>
          sub_item.partner_id === subpartner_id &&
          sub_item.item_type === subitem_type &&
          sub_item.item_external_id === subitem_external_id
      ) || null
    );
  }

  buildAgendaItem(): AgendaItem | null {
    if (!this.hasMilestone()) {
      return null;
    }
    return new AgendaItem(
      uniqueId(),
      'personal',
      this.title,
      this.getItemDetailPageUrl(),
      null,
      null,
      this.milestone_start_date,
      this.milestone_end_date
    );
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
        sub_item.milestone_start_date,
        sub_item.milestone_end_date,
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
      item.milestone_start_date,
      item.milestone_end_date,
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

  isEmpty(): boolean {
    return !this.items.length;
  }

  hasNonArchivedItems(partner_id: string, item_type: string): boolean {
    return this.items.some(
      (item) => item.partner_id === partner_id && item.item_type === item_type
    );
  }

  private _findItem(
    source: FollowupItem[],
    partner_id: string,
    item_type: string,
    item_external_id: string
  ): FollowupItem | null {
    return (
      source.find(
        (item) =>
          item.partner_id === partner_id &&
          item.item_type === item_type &&
          item.item_external_id === item_external_id
      ) || null
    );
  }

  findItem(
    partner_id: string,
    item_type: string,
    item_external_id: string
  ): FollowupItem | null {
    const item = this._findItem(this.items, partner_id, item_type, item_external_id);

    if (item) {
      return item;
    }

    return this._findItem(this.archived_items, partner_id, item_type, item_external_id);
  }
}

export const buildFollowup = async (): Promise<Followup> => {
  const apiFollowup: APIFollowup = await retrieveFollowup();
  return new Followup(apiFollowup);
};
