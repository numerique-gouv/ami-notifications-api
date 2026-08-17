import { retrieveAgenda } from '$lib/api-agenda';
import { retrieveNotifications } from '$lib/notifications';

export const initializeLocalStorage = (searchParams: URLSearchParams) => {
  if (
    localStorage.getItem('id_token') === null &&
    searchParams.get('id_token') !== ''
  ) {
    localStorage.setItem('id_token', searchParams.get('id_token') || '');
  }
  if (
    localStorage.getItem('user_data') === null &&
    searchParams.get('user_data') !== ''
  ) {
    localStorage.setItem('user_data', searchParams.get('user_data') || '');
  }
  if (
    localStorage.getItem('user_fc_hash') === null &&
    searchParams.get('user_fc_hash') !== ''
  ) {
    localStorage.setItem('user_fc_hash', searchParams.get('user_fc_hash') || '');
  }
  if (
    localStorage.getItem('user_api_particulier_encoded_address') === null &&
    searchParams.get('address') !== ''
  ) {
    localStorage.setItem(
      'user_api_particulier_encoded_address',
      searchParams.get('address') || ''
    );
  }
};

export const initializeData = async () => {
  await Promise.all([retrieveAgenda(), retrieveNotifications()]);
};
