import type { Address as AddressType } from '$lib/address';
import { Address, zones } from '$lib/address';
import type { CatalogItem } from '$lib/api-catalog';
import type { ToggleTag } from '$lib/types/components/toggletag';

export type ZoneInfo = {
  zone: string;
  tags: ToggleTag[];
  selected: boolean;
};

type PreferencesJSON = {
  _zones: string[];
  _addresses: AddressType[];
};

export class Preferences {
  constructor(
    private _zones: string[],
    private _addresses: AddressType[]
  ) {}

  static fromJSON(json: Preferences | PreferencesJSON): Preferences {
    if (json instanceof Preferences) {
      return json;
    }
    return new Preferences(
      json._zones || [],
      json._addresses.map((address) => Address.fromJSON(address)) || []
    );
  }

  get zones(): string[] {
    return this._zones;
  }

  get addresses(): AddressType[] {
    return this._addresses;
  }

  static getDefault(userAddress: AddressType | undefined): Preferences {
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
    userAddress: AddressType | undefined
  ): string {
    if (!holiday.zones.length || !this._zones) {
      return '';
    }
    const matchingZones = this._zones.filter((value) => holiday.zones.includes(value));
    if (!matchingZones.length) {
      return '';
    }

    if (matchingZones.length === this._zones.length) {
      // holiday zones match all user preferences
      return '';
    }

    const zonesDict: Record<string, string[]> = {};
    matchingZones.forEach((zone) => {
      zonesDict[zone] = [];
      // add user address in corresponding zone
      if (userAddress !== undefined) {
        if (zone === userAddress.zone) {
          zonesDict[zone].push(`${userAddress.city} (${userAddress.departement}) 🏠`);
        }
      }
      // add cities in preferences in corresponding zones
      this._addresses.forEach((address) => {
        if (zone !== address.zone) {
          return;
        }
        zonesDict[zone].push(`${address.city} (${address.departement})`);
      });
    });

    const result: string[] = [];
    matchingZones.forEach((zone) => {
      const zoneInfo: string[] = [zone];
      const cities: string[] = [];
      zonesDict[zone].sort();
      zonesDict[zone].forEach((city) => {
        cities.push(city);
      });
      if (cities.length) {
        zoneInfo.push(`<strong>${cities.join(', ')}</strong>`);
      }
      result.push(zoneInfo.join('&nbsp;: '));
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

  getZoneInfos(userAddress: AddressType | undefined): ZoneInfo[] {
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
