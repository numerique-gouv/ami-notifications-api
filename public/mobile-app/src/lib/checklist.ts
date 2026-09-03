import type { APICheckList, APICheckListLink } from '$lib/api-checklist';
import CNMSS001 from '$lib/data/checklists/CNMSS001.json';
import F3109 from '$lib/data/checklists/F3109.json';
import F16225 from '$lib/data/checklists/F16225.json';

export class CheckListLink {
  constructor(
    private _text: string,
    private _url: string,
    private _external: boolean,
    private _type?: string
  ) {}

  get url(): string {
    return this._url;
  }

  get text(): string {
    return this._text;
  }

  isTeleservice(): boolean {
    return this._type === 'Téléservice';
  }

  isExternal(): boolean {
    return this._external;
  }
}

export class CheckListItem {
  private _links: CheckListLink[] = [];

  constructor(
    private _checklist: CheckList,
    private _id: string,
    private _text: string,
    private _section_id: string,
    links?: APICheckListLink[]
  ) {
    if (links) {
      this._links = links.map(
        (link) =>
          new CheckListLink(link.text, link.url, link.external === true, link.type)
      );
    }
  }

  get checklist(): CheckList {
    return this._checklist;
  }

  get id(): string {
    return this._id;
  }

  get text(): string {
    return this._text;
  }

  get section_id(): string {
    return this._section_id;
  }

  get links(): CheckListLink[] {
    return this._links;
  }

  get url(): string {
    return `/#/checklist/${this.checklist.id}/checks/${this.section_id}/item/${this.id}/`;
  }

  hasLinks(): boolean {
    return this._links && this._links.length > 0;
  }

  hasTeleserviceLinks(): boolean {
    return this._links && this.getTeleserviceLinks().length > 0;
  }

  getTeleserviceLinks(): CheckListLink[] {
    return this._links.filter((x) => x.isTeleservice());
  }

  get unique_id(): string {
    return `${this.checklist.id}-${this.section_id}-${this.id}`;
  }

  get checked(): boolean {
    const storedCheckedItems = JSON.parse(localStorage.getItem('checkedItems') || '{}');
    return storedCheckedItems[this.unique_id] === true;
  }

  markAs(checked: boolean) {
    const storedCheckedItems = JSON.parse(localStorage.getItem('checkedItems') || '{}');
    storedCheckedItems[this.unique_id] = checked;
    localStorage.setItem('checkedItems', JSON.stringify(storedCheckedItems));
  }
}

export class CheckListSection {
  constructor(
    private _checklist: CheckList,
    private _id: string,
    private _title: string
  ) {}

  get checklist(): CheckList {
    return this._checklist;
  }

  get id(): string {
    return this._id;
  }

  get title(): string {
    return this._title;
  }

  get url(): string {
    return `/#/checklist/${this.checklist.id}/checks/${this.id}/`;
  }
}

export class CheckList {
  private _title: string;
  private _description: string | null;
  private _sections: CheckListSection[];
  private _items: CheckListItem[];

  constructor(
    private _id: string,
    apiCheckList: APICheckList
  ) {
    this._title = apiCheckList.title;
    this._description = apiCheckList.description || null;
    this._sections = apiCheckList.sections.map(
      (section) => new CheckListSection(this, section.id, section.title)
    );
    this._items = apiCheckList.items.map(
      (item) =>
        new CheckListItem(this, item.id, item.text, item.section || '', item.links)
    );
  }

  get id(): string {
    return this._id;
  }

  get title(): string {
    return this._title;
  }

  get description(): string {
    return this._description || '';
  }

  get sections(): CheckListSection[] {
    return this._sections;
  }

  hasSections(): boolean {
    return this._sections && this._sections.length > 1;
  }

  getSectionById(section_id: string): CheckListSection {
    return this._sections.filter((x) => x.id === section_id)[0];
  }

  get items(): CheckListItem[] {
    return this._items;
  }

  getItemsForSection(section_id: string): CheckListItem[] {
    return this._items.filter((x) => x.section_id === section_id);
  }

  getItemById(item_id: string): CheckListItem {
    return this._items.filter((x) => x.id === item_id)[0];
  }

  get url(): string {
    return `/#/checklist/${this.id}/`;
  }
}

export const buildCheckList = async (id: string): Promise<CheckList> => {
  let apiCheckList: APICheckList = { title: 'Inconnue', sections: [], items: [] };
  if (id === 'F3109') {
    apiCheckList = F3109;
  } else if (id === 'F16225') {
    apiCheckList = F16225;
  } else if (id === 'CNMSS001') {
    apiCheckList = CNMSS001;
  } else {
    throw new Error('invalid checklist id');
  }
  return new CheckList(id, apiCheckList);
};
