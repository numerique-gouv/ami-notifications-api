import type { APIServices, APIServicesItem } from '$lib/api-services';
import { retrieveServices } from '$lib/api-services';

export class ServicesItem {
  constructor(
    private _partner_id: string,
    private _item_type: string,

    private _title: string,
    private _short_description: string,
    private _description: string,
    private _link: string,

    private _with_silent_login: boolean
  ) {}

  equals(other: ServicesItem): boolean {
    if (!(other instanceof ServicesItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get id(): string {
    return `${this.partner_id}:${this.item_type}`;
  }

  get partner_id(): string {
    return this._partner_id;
  }

  get item_type(): string {
    return this._item_type;
  }

  get title(): string {
    return this._title;
  }

  get description(): string {
    return this._description;
  }

  get short_description(): string {
    return this._short_description;
  }

  get link(): string | null {
    return this._link;
  }

  get with_silent_login(): boolean {
    return this._with_silent_login;
  }

  get url(): string {
    return `/#/services/service/${this.partner_id}/${this.item_type}`;
  }

  formatDescription(date: string): string {
    return this.description.replace('{date}', date);
  }

  async getServiceUrl(): Promise<string> {
    const _serviceUrl = this.link || '';
    return _serviceUrl;
  }
}

export class Services {
  private _items: ServicesItem[] = [];

  constructor(apiServices: APIServices | null = null) {
    const servicesItems: ServicesItem[] = [];

    const items: APIServicesItem[] = apiServices?.internal || [];

    // build items
    items.forEach((item) => {
      const servicesItem = this.createServicesItem(item);
      servicesItems.push(servicesItem);
    });

    // sort items by title
    servicesItems.sort((a, b) => a.title.localeCompare(b.title, 'fr'));

    // organize items in _items or
    servicesItems.forEach((servicesItem) => {
      this._items.push(servicesItem);
    });
  }

  private createServicesItem(item: APIServicesItem): ServicesItem {
    return new ServicesItem(
      item.partner_id,
      item.item_type,
      item.title,
      item.short_description,
      item.description,
      item.url,
      item.with_silent_login
    );
  }

  get items(): ServicesItem[] {
    return this._items;
  }

  find(partner_id: string, item_type: string): ServicesItem | null {
    const found = this.items.filter(
      (item) => item.partner_id === partner_id && item.item_type === item_type
    );
    if (found.length === 0) {
      console.log(`Can not find ServicesItem ${partner_id}, ${item_type}: no result`);
      return null;
    }
    if (found.length > 1) {
      console.log(
        `Can not find ServicesItem ${partner_id}, ${item_type}: many results`
      );
      return null;
    }
    return found[0];
  }
}

export const buildServices = async (): Promise<Services> => {
  const apiServices: APIServices = await retrieveServices();
  return new Services(apiServices);
};
