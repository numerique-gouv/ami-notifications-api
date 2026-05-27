import {
  PUBLIC_API_GEO_CITY_QUERY_BASE_URL,
  PUBLIC_API_GEO_CITY_QUERY_SEARCH_ENDPOINT,
  PUBLIC_API_GEO_PLATEFORME_BASE_URL,
  PUBLIC_API_GEO_PLATEFORME_SEARCH_ENDPOINT,
} from '$env/static/public';
import { Address } from '$lib/address';
import type { ResponseFromBAN } from '$lib/addressesFromBAN';

type Departement = {
  code: string;
  nom: string;
};

export type ResponseFromGeoAPI = {
  nom: string;
  code: string;
  departement: Departement;
};

export const callGeoAPI = async (inputValue: string) => {
  const encodedInputValue = encodeURI(inputValue);
  const endpoint_headers = {
    accept: 'application/json',
  };
  const response = await fetch(
    `${PUBLIC_API_GEO_CITY_QUERY_BASE_URL}${PUBLIC_API_GEO_CITY_QUERY_SEARCH_ENDPOINT.replace('{q}', encodedInputValue)}`,
    {
      headers: endpoint_headers,
    }
  );

  if (response.status >= 400) {
    return { errorCode: 'geo-api-unavailable', errorMessage: 'Geo API unavailable' };
  }

  let result = [] as ResponseFromGeoAPI[];
  try {
    result = await response.json();
  } catch (error) {
    console.error(error);
  }

  return {
    results: result,
  };
};

export const cityToBAN = async (city: ResponseFromGeoAPI) => {
  const endpoint_headers = {
    accept: 'application/json',
  };
  const response = await fetch(
    `${PUBLIC_API_GEO_PLATEFORME_BASE_URL}${PUBLIC_API_GEO_PLATEFORME_SEARCH_ENDPOINT}?q=${encodeURI(city.nom)}&citycode=${city.code}&limit=1`,
    {
      headers: endpoint_headers,
    }
  );

  if (response.status >= 400) {
    return { errorCode: 'ban-unavailable', errorMessage: 'BAN unavailable' };
  }

  let result = {} as ResponseFromBAN;
  try {
    result = await response.json();
  } catch (error) {
    console.error(error);
  }

  const data = result.features?.[0]?.properties;
  if (!data) {
    return { address: null };
  }

  const address = new Address(
    data.city,
    data.context,
    data.id,
    data.label,
    data.name,
    data.postcode
  );
  return { address: address };
};
