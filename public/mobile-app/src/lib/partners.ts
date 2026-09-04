import type { APIPartners, APIPartnersItem } from '$lib/api-partners';
import { retrievePartners } from '$lib/api-partners';

export class PartnersItem {
  constructor(
    private _slug: string,
    private _name: string,
    private _link: string
  ) {}

  equals(other: PartnersItem): boolean {
    if (!(other instanceof PartnersItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get slug(): string {
    return this._slug;
  }

  get name(): string {
    return this._name;
  }

  get link(): string {
    return this._link;
  }
}

export class Partners {
  private _items: PartnersItem[] = [];

  constructor(apiPartners: APIPartners | null = null) {
    const partnersItems: PartnersItem[] = [];

    const items: APIPartnersItem[] = apiPartners?.partners || [];

    items.forEach((item) => {
      const partnersItem = this.createPartnersItem(item);
      partnersItems.push(partnersItem);
    });

    partnersItems.sort((a, b) => a.slug.localeCompare(b.slug, 'fr'));

    partnersItems.forEach((partnersItem) => {
      this._items.push(partnersItem);
    });
  }

  get items(): PartnersItem[] {
    return this._items;
  }

  private createPartnersItem(item: APIPartnersItem): PartnersItem {
    return new PartnersItem(item.slug, item.name, item.link);
  }
}

export const buildPartners = async (): Promise<Partners> => {
  const apiPartners: APIPartners = await retrievePartners();
  return new Partners(apiPartners);
};
