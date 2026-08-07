import type { Agenda } from '$lib/agenda';
import { type User, userStore } from '$lib/state/User.svelte';
import { dateToISO } from '$lib/utils';

const oneday_in_ms = 24 * 60 * 60 * 1000;

export class AutoPromoItem {
  constructor(
    private _kind: 'address' | 'otv',
    private _title: string,
    private _description: string,
    private _link: string
  ) {}

  equals(other: AutoPromoItem): boolean {
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get kind(): string {
    return this._kind;
  }

  get title(): string {
    return this._title;
  }

  get description(): string {
    return this._description;
  }

  get link(): string {
    return this._link;
  }
}

export class AutoPromo {
  private _items: AutoPromoItem[] = [];
  private _connectedUser: User | null = null;

  constructor(agenda: Agenda) {
    this._connectedUser = userStore.connected;
    if (!this._connectedUser) {
      // user has to be connected
      return;
    }

    const addressItem = this.buildAddressItem();
    if (addressItem) {
      this._items.push(addressItem);
    }

    const OTVItem = this.buildOTVItem(agenda);
    if (OTVItem) {
      this._items.push(OTVItem);
    }
  }

  private buildAddressItem(): AutoPromoItem | null {
    if (this._connectedUser?.identity?.address) {
      return null;
    }
    return new AutoPromoItem(
      'address',
      'Renseignez votre adresse',
      'Gagnez du temps en la renseignant une seule fois',
      '/#/edit-address'
    );
  }

  private buildOTVItem(agenda: Agenda): AutoPromoItem | null {
    const holiday = agenda.holidayForOTV;
    if (!holiday) {
      return null;
    }
    if (!holiday.start_date) {
      // should not happen for public holiday
      return null;
    }
    const startDate = new Date(holiday.start_date.getTime() - 3 * 7 * oneday_in_ms);
    return new AutoPromoItem(
      'otv',
      'Opération Tranquillité Vacances',
      'Protégez votre domicile pendant votre absence',
      `/#/procedure?date=${dateToISO(startDate)}`
    );
  }

  get items(): AutoPromoItem[] {
    return this._items;
  }
}

export const buildAutoPromo = (agenda: Agenda): AutoPromo => {
  return new AutoPromo(agenda);
};
