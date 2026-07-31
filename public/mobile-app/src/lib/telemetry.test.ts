import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as sentryMethods from '@sentry/svelte';
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
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      trace('test');
      expect(sentryMethods.logger.trace).toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
  });
  describe('debug', () => {
    test('debug should go to sentry and not matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      debug('test');
      expect(sentryMethods.logger.debug).toHaveBeenCalled();
      expect(spy).not.toHaveBeenCalled();
    });
  });
  describe('info', () => {
    test('info should go to both sentry and matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      info('test');
      expect(sentryMethods.logger.info).toHaveBeenCalled();
      expect(spy).toHaveBeenCalled();
    });
  });
  describe('warn', () => {
    test('warn should go to both sentry and matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      warn('test');
      expect(sentryMethods.logger.warn).toHaveBeenCalled();
      expect(spy).toHaveBeenCalled();
    });
  });
  describe('error', () => {
    test('error should go to both sentry and matomo', () => {
      const spy = vi.spyOn(matomoMethods, 'trackTelemetryEvent').mockReturnValue();
      error('test');
      expect(sentryMethods.logger.error).toHaveBeenCalled();
      expect(spy).toHaveBeenCalled();
    });
  });
});
