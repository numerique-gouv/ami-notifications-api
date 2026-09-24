import { apiFetch } from '$lib/auth';

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
  intertitle?: string;
  links?: APICheckListLink[];
  conditions?: APICheckListCondition[];
};

export type APICheckListSection = {
  id: string;
  title: string;
};

export type APICheckListDefinition = {
  title: string;
  description?: string;
  sections: APICheckListSection[];
  items: APICheckListItem[];
};

export type APICheckList = {
  icon: string;
  definition: APICheckListDefinition;
};

export const retrieveCheckList = async (id: string): Promise<APICheckList> => {
  const response = await apiFetch(`/api/v1/users/data/checklist/${id}`);
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('unknown checklist id');
  }
};
