import * as Sentry from '@sentry/svelte';
import { PUBLIC_LOG_LEVEL } from '$env/static/public';
import { getDeviceId } from '$lib/bridges/nativeInfos';
import { trackTelemetryEvent } from '$lib/matomo';

const LOG_LEVELS = ['trace', 'debug', 'info', 'warn', 'error', 'fatal'];

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
  if (LOG_LEVELS.indexOf(PUBLIC_LOG_LEVEL) > LOG_LEVELS.indexOf('trace')) {
    return;
  }
  Sentry.logger.trace(message, options);
};

export const debug = (message: string, options?: Record<string, unknown>) => {
  if (LOG_LEVELS.indexOf(PUBLIC_LOG_LEVEL) > LOG_LEVELS.indexOf('debug')) {
    return;
  }
  Sentry.logger.trace(message, options);
  Sentry.logger.debug(message, options);
};

export const info = (message: string, options?: Record<string, unknown>) => {
  if (LOG_LEVELS.indexOf(PUBLIC_LOG_LEVEL) > LOG_LEVELS.indexOf('info')) {
    return;
  }
  Sentry.logger.info(message, options);
  trackTelemetryEvent(message);
};

export const warn = (message: string, options?: Record<string, unknown>) => {
  if (LOG_LEVELS.indexOf(PUBLIC_LOG_LEVEL) > LOG_LEVELS.indexOf('warn')) {
    return;
  }
  Sentry.logger.warn(message, options);
  trackTelemetryEvent(message);
};

export const error = (message: string, options?: Record<string, unknown>) => {
  if (LOG_LEVELS.indexOf(PUBLIC_LOG_LEVEL) > LOG_LEVELS.indexOf('error')) {
    return;
  }
  Sentry.logger.error(message, options);
  trackTelemetryEvent(message);
};
