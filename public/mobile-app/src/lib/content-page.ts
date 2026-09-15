import type { APIContentPage } from '$lib/api-content-page';
import { retrieveContentPage } from '$lib/api-content-page';

export class ContentSection {
  constructor(
    private _page: ContentPage,
    private _slug: string,
    private _title: string,
    private _text: string
  ) {}

  get page(): ContentPage {
    return this._page;
  }

  get slug(): string {
    return this._slug;
  }

  get title(): string {
    return this._title;
  }

  get text(): string {
    return this._text;
  }

  get url(): string {
    return `/#/page/${this.page.slug}/${this.slug}`;
  }
}

export class ContentPage {
  private _slug: string;
  private _title: string;
  private _sections: ContentSection[];

  constructor(apiContentPage: APIContentPage) {
    this._slug = apiContentPage.slug;
    this._title = apiContentPage.title;
    this._sections = apiContentPage.sections.map(
      (section) => new ContentSection(this, section.slug, section.title, section.text)
    );
  }

  get slug(): string {
    return this._slug;
  }

  get title(): string {
    return this._title;
  }

  get sections(): ContentSection[] {
    return this._sections;
  }

  getSectionBySlug(section_slug: string): ContentSection {
    return this._sections.filter((x) => x.slug === section_slug)[0];
  }

  get url(): string {
    return `/#/page/${this.slug}`;
  }
}

export const buildContentPage = async (slug: string): Promise<ContentPage> => {
  const apiContentPage: APIContentPage = await retrieveContentPage(slug);
  return new ContentPage(apiContentPage);
};
