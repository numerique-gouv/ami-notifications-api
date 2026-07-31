import { emit } from '$lib/bridges/nativeBridge';
import { getUrlAliases } from '$lib/urlAliases';

window.WebAppBridge = {
  getUrlAliases: () => JSON.stringify(getUrlAliases()),
};

export const notifyWebappBridgeReady = () => {
  emit('webappBridgeReady');
};
