import { apiFetch } from '$lib/auth';

export type APIContentSection = {
  slug: string;
  title: string;
  text: string;
};

export type APIContentPage = {
  slug: string;
  title: string;
  sections: APIContentSection[];
};

export const retrieveContentPage = async (slug: string): Promise<APIContentPage> => {
  const response = await apiFetch(`/api/v1/page/${slug}`);
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('unknown page slug');
  }
};
