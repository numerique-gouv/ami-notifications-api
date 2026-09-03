export type APICheckListCondition = {
  type: string;
  var?: string;
  conditions?: APICheckListCondition[];
};

export type APICheckListLink = {
  text: string;
  url: string;
  external?: boolean;
  type?: string;
};

export type APICheckListItem = {
  id: string;
  text: string;
  section: string;
  links?: APICheckListLink[];
  conditions?: APICheckListCondition[];
};

export type APICheckListSection = {
  id: string;
  title: string;
};

export type APICheckList = {
  title: string;
  description?: string;
  sections: APICheckListSection[];
  items: APICheckListItem[];
};
