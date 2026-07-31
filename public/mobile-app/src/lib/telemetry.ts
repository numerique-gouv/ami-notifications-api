import * as Sentry from '@sentry/svelte';
import { getDeviceId } from '$lib/bridges/nativeInfos';
import { trackTelemetryEvent } from '$lib/matomo';

const shortDigest = async (message: string) => {
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const hashBuffer = await window.crypto.subtle.digest('SHA-1', data);
  // @ts-expect-error: Property 'toHex' does not exist on type 'Uint8Array<ArrayBuffer>'
  const hashHex = new Uint8Array(hashBuffer).toHex();
  return hashHex.substring(0, 20);
};

export const setGlobalScope = async () => {
  const deviceId = getDeviceId();
  const user_hash = localStorage.getItem('user_fc_hash');
  const hashed_user_hash = user_hash ? await shortDigest(user_hash) : '';
  Sentry.getGlobalScope().setAttributes({
    user_id: hashed_user_hash,
    device_id: deviceId,
  });
};

export const trace = (message: string, options?: Record<string, unknown>) => {
  Sentry.logger.trace(message, options);
};

export const debug = (message: string, options?: Record<string, unknown>) => {
  Sentry.logger.debug(message, options);
};

export const info = (message: string, options?: Record<string, unknown>) => {
  Sentry.logger.info(message, options);
  trackTelemetryEvent(message);
};

export const warn = (message: string, options?: Record<string, unknown>) => {
  Sentry.logger.warn(message, options);
  trackTelemetryEvent(message);
};

export const error = (message: string, options?: Record<string, unknown>) => {
  Sentry.logger.error(message, options);
  trackTelemetryEvent(message);
};
