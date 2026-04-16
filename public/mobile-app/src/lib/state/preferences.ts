import type { Address } from '$lib/address';
import { zones } from '$lib/address';
import type { CatalogItem } from '$lib/api-catalog';
import type { ToggleTag } from '$lib/types/components/toggletag';

export type ZoneInfo = {
  zone: string;
  tags: ToggleTag[];
  selected: boolean;
};

export class Preferences {
  constructor(
    private _zones: string[],
    private _addresses: Address[]
  ) {}

  static fromJSON(json: any): Preferences {
    return new Preferences(json._zones || [], json._addresses || []);
  }

  get zones(): string[] {
    return this._zones;
  }

  get addresses(): Address[] {
    return this._addresses;
  }

  static getDefault(userAddress: Address | undefined): Preferences {
    const defaultZones = ['Zone A', 'Zone B', 'Zone C', 'Corse'];
    const defaultPreferences = new Preferences(defaultZones, []);

    if (userAddress === undefined) {
      return defaultPreferences;
    }

    const userZone = userAddress.zone;

    if (defaultZones.includes(userZone)) {
      return defaultPreferences;
    }

    return new Preferences([userZone], []);
  }

  isSchoolHolidayConcerned(holiday: CatalogItem): boolean {
    if (!holiday.zones.length || !this._zones) {
      return false;
    }
    if (!this._zones.filter((value) => holiday.zones.includes(value)).length) {
      return false;
    }
    return true;
  }

  getSchoolHolidayDescription(
    holiday: CatalogItem,
    userAddress: Address | undefined
  ): string {
    if (!holiday.zones.length || !this._zones) {
      return '';
    }
    const matchingZones = this._zones.filter((value) => holiday.zones.includes(value));
    if (!matchingZones.length) {
      return '';
    }

    const seenZones: string[] = [];
    const result: string[] = [];

    if (userAddress !== undefined) {
      if (matchingZones.includes(userAddress.zone)) {
        result.push(`${userAddress.city} (${userAddress.departement}) 🏠`);
        seenZones.push(userAddress.zone);
      }
    }

    // first look at cities in preferences
    this._addresses.forEach((address) => {
      if (seenZones.includes(address.zone)) {
        return;
      }
      if (!matchingZones.includes(address.zone)) {
        return;
      }
      result.push(`${address.city} (${address.departement})`);
      seenZones.push(address.zone);
    });

    // then add remaining zones
    matchingZones.forEach((zone) => {
      if (seenZones.includes(zone)) {
        return;
      }
      result.push(zone);
    });

    return result.join(', ');
  }

  addZone(zone: string) {
    if (this._zones.includes(zone)) {
      return;
    }
    this._zones.push(zone);
  }

  removeZone(zone: string) {
    this._zones = this._zones.filter((value) => zone !== value);
  }

  getZoneInfos(userAddress: Address | undefined): ZoneInfo[] {
    const result: ZoneInfo[] = [];
    zones.forEach((zone) => {
      const selected = this._zones.includes(zone.label);
      const tags: ToggleTag[] = [];
      if (userAddress?.zone === zone.label) {
        tags.push({
          label: `${userAddress.city} (${userAddress.departement}) 🏠`,
          removable: false,
        });
      }
      this._addresses.forEach((address) => {
        if (address.zone === zone.label) {
          tags.push({
            label: `${address.city} (${address.departement})`,
            removable: true,
          });
        }
      });
      result.push({ zone: zone.label, tags: tags, selected: selected });
    });
    return result;
  }
}
