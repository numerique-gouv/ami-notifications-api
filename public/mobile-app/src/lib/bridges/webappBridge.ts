import { PUBLIC_APP_URL } from '$env/static/public';
import { emit } from '$lib/bridges/nativeBridge';
import { getUrlAliases } from '$lib/urlAliases';

window.WebAppBridge = {
  getUrlAliases: () => JSON.stringify(getUrlAliases()),
  getAuthenticationUrls: () => authenticationUrls,
};

export const notifyWebappBridgeReady = () => {
  emit('webappBridgeReady');
};

const authenticationUrls: string[] = [
  `${PUBLIC_APP_URL}/login-france-connect`,
  `${PUBLIC_APP_URL}/relogin-france-connect`,
  `${PUBLIC_APP_URL}/silent-login-ami-fi`,
  `${PUBLIC_APP_URL}/login-callback`,
  `${PUBLIC_APP_URL}/goto-redirect-url`,
  `${PUBLIC_APP_URL}/api/v1/fi/authorize/`,
  `${PUBLIC_APP_URL}/#/relogin`,
  `${PUBLIC_APP_URL}/#/silent-login`,
  `${PUBLIC_APP_URL}/#/login-callback`,
  `${PUBLIC_APP_URL}/#/passkey-authentication`,
];
