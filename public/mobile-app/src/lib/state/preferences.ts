import type { Address } from '$lib/address';

type PreferencesJSON = {
  _zones: string[];
  _addresses: Address[];
};

export class Preferences {
  constructor(
    private _zones: string[],
    private _addresses: Address[]
  ) {}

  static fromJSON(json: Preferences | PreferencesJSON): Preferences {
    if (json instanceof Preferences) {
      return json;
    }
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
}
