import {
  PUBLIC_CONTACT_EMAIL,
  PUBLIC_CONTACT_EMAIL_BODY,
  PUBLIC_CONTACT_URL,
} from '$env/static/public';
import { getPlatform, getVersion } from '$lib/nativeInfos';

export const getContactMailToUri = (userFcHash?: string): string => {
  const contactEmail = PUBLIC_CONTACT_EMAIL;
  const contactBody = (PUBLIC_CONTACT_EMAIL_BODY || '')
    .replace('{fc_hash}', userFcHash || '<absent>')
    .replace('{platform}', getPlatform())
    .replace('{version}', getVersion());

  let mailtoUri = `mailto:${contactEmail}`;
  if (contactBody) {
    mailtoUri += `?body=${encodeURIComponent(contactBody)}`;
  }
  return mailtoUri;
};

export const getContactUrl = (userFcHash?: string): string => {
  const contactUrl = PUBLIC_CONTACT_URL;
  return contactUrl
    .replace('{fc_hash}', encodeURIComponent(userFcHash || '<absent>'))
    .replace('{platform}', encodeURIComponent(getPlatform()))
    .replace('{version}', encodeURIComponent(getVersion()));
};
