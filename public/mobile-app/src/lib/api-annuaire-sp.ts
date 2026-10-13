import { apiFetch } from '$lib/auth';

export type APIMairie = {
  url_service_public: string;
};

export const retrieveMairie = async (
  code_insee_commune: string
): Promise<APIMairie | null> => {
  const now = new Date();
  let toFetch = false;
  let apiData = localStorage.getItem(`mairie_${code_insee_commune}`);
  if (apiData === null) {
    toFetch = true;
  } else {
    try {
      const data = JSON.parse(apiData);
      if (!data) {
        toFetch = true;
      } else if (!data.expires_at) {
        toFetch = true;
      } else {
        const expires_at = new Date(data.expires_at);
        if (expires_at < now) {
          toFetch = true;
        }
      }
    } catch {
      toFetch = true;
    }
  }
  if (toFetch) {
    const response = await apiFetch(`/api/v1/users/data/mairie/${code_insee_commune}`);
    if (response.ok) {
      apiData = await response.text();
      localStorage.setItem(`mairie_${code_insee_commune}`, apiData);
    }
  }
  if (apiData) {
    const data = JSON.parse(apiData);
    return { url_service_public: data.url_service_public };
  }
  return null;
};
