import {
  PUBLIC_CONTACT_EMAIL,
  PUBLIC_CONTACT_EMAIL_BODY,
  PUBLIC_CONTACT_URL,
  PUBLIC_CURRENT_COMMIT_ID,
} from '$env/static/public';
import { getPlatform, getVersion } from '$lib/bridges/nativeInfos';

export const getContactMailToUri = (userFcHash?: string): string => {
  const contactEmail = PUBLIC_CONTACT_EMAIL;
  const contactBody = (PUBLIC_CONTACT_EMAIL_BODY || '')
    .replace('{fc_hash}', userFcHash || '<absent>')
    .replace('{platform}', getPlatform())
    .replace('{version}', getVersion())
    .replace('{commit_id}', PUBLIC_CURRENT_COMMIT_ID);

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
    .replace('{version}', encodeURIComponent(getVersion()))
    .replace('{commit_id}', encodeURIComponent(PUBLIC_CURRENT_COMMIT_ID));
};
