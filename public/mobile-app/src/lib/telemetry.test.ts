import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as sentryMethods from '@sentry/svelte';
import * as envModule from '$env/static/public';
import * as nativeInfosMethods from '$lib/bridges/nativeInfos';
import * as matomoMethods from '$lib/matomo';
import { debug, error, info, setGlobalScope, trace, warn } from './telemetry';

vi.mock('@sentry/svelte', () => ({
  getGlobalScope: () => ({
    setAttributes: vi.fn(),
  }),
  logger: {
    trace: vi.fn(),
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock('$env/static/public', async (importOriginal) => {
  const original = (await importOriginal()) as Record<string, unknown>;
  return Promise.resolve({
    ...original,
  });
});

describe('/telemetry.ts', () => {
  describe('setGlobalScope', () => {
    test('should call getDeviceId', async () => {
      const spy = vi
        .spyOn(nativeInfosMethods, 'getDeviceId')
        .mockReturnValue('fake-device-id');
      await setGlobalScope();
      expect(spy).toHaveBeenCalled();
    });
  });
  describe('trace', () => {
    test('trace should go to sentry and not matomo', () => {
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'trace';
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      trace('test');
      expect(sentryMethods.logger.trace).toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
    test('trace but log level is higher', () => {
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'info';
      trace('test');
      expect(sentryMethods.logger.trace).not.toHaveBeenCalled();
    });
  });
  describe('debug', () => {
    test('debug should go to sentry and not matomo', () => {
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'trace';
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      debug('test');
      expect(sentryMethods.logger.debug).toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
    test('debug but log level is higher', () => {
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'info';
      debug('test');
      expect(sentryMethods.logger.debug).not.toHaveBeenCalled();
    });
  });
  describe('info', () => {
    test('info should go to both sentry and matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'info';
      info('test');
      expect(sentryMethods.logger.info).toHaveBeenCalled();
      expect(spy).toHaveBeenCalled();
    });
    test('info but log level is higher', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'fatal';
      info('test');
      expect(sentryMethods.logger.info).not.toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
  });
  describe('warn', () => {
    test('warn should go to both sentry and matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'info';
      warn('test');
      expect(sentryMethods.logger.warn).toHaveBeenCalled();
      expect(spy).toHaveBeenCalled();
    });
    test('warn but log level is higher', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'fatal';
      warn('test');
      expect(sentryMethods.logger.warn).not.toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
  });
  describe('error', () => {
    test('error should go to both sentry and matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'info';
      error('test');
      expect(sentryMethods.logger.error).toHaveBeenCalled();
      expect(spy).toHaveBeenCalled();
    });
    test('error but log level is higher', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      vi.mocked(envModule).PUBLIC_LOG_LEVEL = 'fatal';
      error('test');
      expect(sentryMethods.logger.error).not.toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
  });
});
