import MiniSearch, {
  type SearchResult as MiniSearchResult,
  type Options,
} from 'minisearch';
import type {
  APIServices,
  APIServicesItem,
  Parameter,
  ParameterKey,
  ServicesItemsParameters,
} from '$lib/api-services';
import {
  getServicesItemParameters,
  isParameterKey,
  PARAMETER_KEYS,
  retrieveServices,
} from '$lib/api-services';
import { getVersion } from '$lib/bridges/nativeInfos';
import { userStore } from '$lib/state/User.svelte';
import * as telemetry from '$lib/telemetry';

export type ServicesItemSearchResult = {
  terms: string;
  services: ServicesItem[];
};

const normalize = (term: string) =>
  term
    .toLowerCase()
    .replace(/œ/g, 'oe')
    .replace(/æ/g, 'ae')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');

const STOP_WORDS = new Set(
  [
    'le',
    'la',
    'les',
    'un',
    'une',
    'des',
    'du',
    'de',
    'd',
    'l',
    'au',
    'aux',
    'et',
    'ou',
    'a',
    'à',
    'en',
    'dans',
    'sur',
    'sous',
    'par',
    'pour',
    'avec',
    'sans',
    'ce',
    'cet',
    'cette',
    'ces',
    'se',
    's',
    'sa',
    'son',
    'ses',
    'qui',
    'que',
    'qu',
    'quoi',
    'dont',
    'ne',
    'n',
    'pas',
    'y',
    'je',
    'j',
    'tu',
    'il',
    'elle',
    'on',
    'nous',
    'vous',
    'ils',
    'elles',
    'me',
    'm',
    'te',
    't',
    'mon',
    'ma',
    'mes',
    'ton',
    'ta',
    'tes',
    'est',
    'sont',
    'été',
    'être',
    'avoir',
    'ai',
    'as',
    'ont',
    'c',
  ].map(normalize)
);

const processTerm = (term: string): string | null => {
  const t = normalize(term);
  return STOP_WORDS.has(t) ? null : t;
};

interface IndexedServicesItem {
  id: string;
  kind: string;
  partner_id: string;
  item_type: string;
  title: string;
}

const searchOptions: Options<IndexedServicesItem> = {
  fields: ['title'],
  storeFields: ['kind', 'partner_id', 'item_type'],
  processTerm: processTerm,
  searchOptions: {
    prefix: true,
    fuzzy: (term) => (term.length > 4 ? 0.2 : false),
    combineWith: 'AND',
  },
};

export class ServicesItem {
  constructor(
    private _partner_id: string,
    private _item_type: string,
    private _kind: string,

    private _title: string,
    private _service_name: string,
    private _description: string,
    private _link: string,
    private _icon: string,

    private _with_silent_login: boolean
  ) {}

  equals(other: ServicesItem): boolean {
    if (!(other instanceof ServicesItem)) {
      return false;
    }
    return JSON.stringify(this) === JSON.stringify(other);
  }

  get id(): string {
    return `${this.kind}:${this.partner_id}:${this.item_type}`;
  }

  get partner_id(): string {
    return this._partner_id;
  }

  get item_type(): string {
    return this._item_type;
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

  get service_name(): string {
    return this._service_name;
  }

  get link(): string | null {
    return this._link;
  }

  get icon(): string | null {
    return this._icon;
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
    let _serviceUrl = this.link || '';

    // first replace front values
    _serviceUrl = _serviceUrl.replace(
      '{fc_hash}',
      localStorage.getItem('user_fc_hash') || ''
    );
    _serviceUrl = _serviceUrl.replace('{app_version_id}', getVersion());

    // and try to replace back values
    const parametersRegexp = new RegExp(
      `\\{back_param_(${PARAMETER_KEYS.join('|')})\\}`,
      'g'
    );
    const matches = [..._serviceUrl.matchAll(parametersRegexp)];
    const keys: ParameterKey[] = [...new Set(matches.map((m) => m[1]))].filter(
      isParameterKey
    );
    const parameters: Parameter[] = [];
    // build parameters for getServicesItemParameters call
    keys.forEach((parameter) => {
      switch (parameter) {
        case 'otv_jwt_token': {
          if (!userStore.connected) {
            return;
          }
          const userIdentity = userStore.connected.identity;
          if (!userIdentity) {
            return;
          }
          parameters.push({
            parameter: 'otv_jwt_token',
            values: {
              preferred_username: userIdentity.preferred_username || '',
              email: userIdentity.email || '',
              address_city: userIdentity.address?.city || '',
              address_postcode: userIdentity.address?.postcode || '',
              address_citycode: userIdentity.address?.citycode || '',
              address_name: userIdentity.address?.name || '',
            },
          });
          break;
        }
        default: {
          console.log(`no handler found for back_param ${parameter}`);
        }
      }
    });
    let parametersValues: ServicesItemsParameters = {};
    if (parameters.length) {
      // call getServicesItemParameters
      parametersValues = await getServicesItemParameters(parameters);
    }
    // and replace params in url
    keys.forEach((key) => {
      _serviceUrl = _serviceUrl.replace(
        `{back_param_${key}}`,
        parametersValues[key] || ''
      );
    });
    return _serviceUrl;
  }
}

export class Services {
  private _items: ServicesItem[] = [];
  private _miniSearch: MiniSearch<IndexedServicesItem> | null = null;

  constructor(apiServices: APIServices | null = null) {
    const internal: APIServicesItem[] = apiServices?.internal || [];

    // build items
    internal.forEach((item) => {
      const servicesItem = this.createServicesItem(item);
      this._items.push(servicesItem);
    });

    // sort items by title
    this._items.sort((a, b) => a.title.localeCompare(b.title, 'fr'));

    // load miniSearch
    this.loadMiniSeach();
  }

  private createServicesItem(item: APIServicesItem): ServicesItem {
    return new ServicesItem(
      item.partner_id,
      item.item_type,
      item.kind,
      item.title,
      item.service_name,
      item.description,
      item.url,
      item.icon,
      item.with_silent_login
    );
  }

  private loadMiniSeach() {
    const data = localStorage.getItem(`services_minisearch`);
    if (data !== null) {
      try {
        this._miniSearch = MiniSearch.loadJSON<IndexedServicesItem>(
          data,
          searchOptions
        );
        return;
      } catch (error) {
        telemetry.error('Error loading services indexation', {
          error: `${error}`,
        });
        localStorage.removeItem(`services_minisearch`);
      }
    }
    this._miniSearch = this.createMiniSearch();
  }

  private createMiniSearch(): MiniSearch<IndexedServicesItem> | null {
    const miniSearch = new MiniSearch(searchOptions);
    try {
      miniSearch.addAll(this.items);
    } catch (error) {
      telemetry.error('Error indexing services', {
        error: `${error}`,
      });
      return null;
    }
    localStorage.setItem(`services_minisearch`, JSON.stringify(miniSearch));
    return miniSearch;
  }

  get items(): ServicesItem[] {
    return this._items;
  }

  get catalog(): ServicesItem[] {
    return this.items.filter((item) => item.kind === 'catalog');
  }

  get sos(): ServicesItem[] {
    return this.items.filter((item) => item.kind === 'sos');
  }

  get steps(): ServicesItem[] {
    return this.items.filter((item) => item.kind === 'steps');
  }

  find(kind: string, partner_id: string, item_type: string): ServicesItem | null {
    const found = this.items.filter(
      (item) =>
        item.kind === kind &&
        item.partner_id === partner_id &&
        item.item_type === item_type
    );
    if (found.length === 0) {
      console.log(
        `Can not find ServicesItem ${kind}, ${partner_id}, ${item_type}: no result`
      );
      return null;
    }
    if (found.length > 1) {
      console.log(
        `Can not find ServicesItem ${kind}, ${partner_id}, ${item_type}: many results`
      );
      return null;
    }
    return found[0];
  }

  search(terms: string): ServicesItemSearchResult | null {
    if (this._miniSearch === null) {
      return null;
    }
    const results: MiniSearchResult[] = this._miniSearch.search(terms);
    const filteredServices = results
      .slice(0, 10)
      .map((item) => this.find(item.kind, item.partner_id, item.item_type))
      .filter((item): item is ServicesItem => item !== null);
    return {
      terms: terms,
      services: filteredServices,
    };
  }
}

export const buildServices = async (): Promise<Services> => {
  const apiServices: APIServices = await retrieveServices();
  return new Services(apiServices);
};
