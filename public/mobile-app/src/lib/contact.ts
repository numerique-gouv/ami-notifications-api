import { PUBLIC_CONTACT_EMAIL, PUBLIC_CONTACT_URL } from '$env/static/public';
import { getPlatform, getVersion } from '$lib/nativeInfos';

export const getContactEmail = (): string => {
  return PUBLIC_CONTACT_EMAIL;
};

export const getContactUrl = (userFcHash?: string): string => {
  const contactUrl = PUBLIC_CONTACT_URL;
  return contactUrl
    .replace('{fc_hash}', encodeURIComponent(userFcHash || '<absent>'))
    .replace('{platform}', encodeURIComponent(getPlatform()))
    .replace('{version}', encodeURIComponent(getVersion()));
};
