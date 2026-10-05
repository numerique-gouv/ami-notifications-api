import * as Sentry from '@sentry/svelte';
import { PUBLIC_LOG_LEVEL } from '$env/static/public';
import { getDeviceId } from '$lib/bridges/nativeInfos';
import { trackTelemetryEvent } from '$lib/matomo';

const LOG_LEVELS = ['trace', 'debug', 'info', 'warn', 'error', 'fatal'];

function uint8ToHex(uint8: Uint8Array) {
  return Array.from(uint8)
    .map((i) => i.toString(16).padStart(2, '0'))
    .join('');
}

const shortDigest = async (message: string) => {
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const hashBuffer = await window.crypto.subtle.digest('SHA-1', data);
  const hashHex = uint8ToHex(new Uint8Array(hashBuffer));
  return hashHex.substring(0, 20);
};

export const setGlobalScope = async () => {
  const deviceId = getDeviceId();
  const user_hash = localStorage.getItem('user_fc_hash');
  if (user_hash) {
    const hashed_user_hash = await shortDigest(user_hash);
    Sentry.setUser({ id: hashed_user_hash });
  }
  Sentry.setAttribute('device_id', deviceId);
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
