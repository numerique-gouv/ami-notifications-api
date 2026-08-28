import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiConsentsMethods from '$lib/api-consents';
import {
  buildConsents,
  Consents,
  ConsentsItem,
  hasAnyConsents,
  updateConsent,
} from '$lib/consents';

describe('/consents.ts', () => {
  describe('Consents', () => {
    test('should create items from api', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const consentsItem1 = {
        partner_id: 'dinum-ami',
        consent_datetime: new Date('2026-01-23T15:50:00Z'),
      };
      const consentsItem2 = {
        partner_id: 'psl',
        consent_datetime: new Date('2026-02-22T15:50:00Z'),
      };
      const consentsItem3 = {
        partner_id: 'psl',
        consent_datetime: new Date('2026-02-21T15:50:00Z'),
      };
      const consentsItem4 = {
        partner_id: 'dinum-ami',
        consent_datetime: new Date('2026-02-21T15:50:00Z'),
      };

      // When
      const consents = new Consents({
        consents: [consentsItem1, consentsItem2, consentsItem3, consentsItem4],
      });

      // Then
      expect(consents.items.length).equal(4);
      expect(consents.items[0]).toEqual(
        new ConsentsItem('dinum-ami', new Date('2026-01-23T15:50:00Z'))
      );
      expect(consents.items[1]).toEqual(
        new ConsentsItem('dinum-ami', new Date('2026-02-21T15:50:00Z'))
      );
      expect(consents.items[2]).toEqual(
        new ConsentsItem('psl', new Date('2026-02-22T15:50:00Z'))
      );
      expect(consents.items[3]).toEqual(
        new ConsentsItem('psl', new Date('2026-02-21T15:50:00Z'))
      );
    });
  });
  describe('buildConsents', () => {
    test('should retrieve inventory and init consents with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const consentsItem1 = {
        partner_id: 'dinum-ami',
        consent_datetime: new Date('2026-01-23T15:50:00Z'),
      };
      const consentsItem2 = {
        partner_id: 'psl',
        consent_datetime: new Date('2026-02-22T15:50:00Z'),
      };
      const spy = vi.spyOn(apiConsentsMethods, 'retrieveConsents').mockResolvedValue({
        consents: [consentsItem1, consentsItem2],
      });

      // When
      const consents = await buildConsents();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(consents).toBeInstanceOf(Consents);
      expect(consents.items.length).equal(2);
      expect(consents.items[0]).toEqual(
        new ConsentsItem('dinum-ami', new Date('2026-01-23T15:50:00Z'))
      );
      expect(consents.items[1]).toEqual(
        new ConsentsItem('psl', new Date('2026-02-22T15:50:00Z'))
      );
    });
  });
  describe('updateConsent', () => {
    test('should call update consent from api', async () => {
      // Given
      const spy = vi.spyOn(apiConsentsMethods, 'updateApiConsent');

      // When
      await updateConsent('dinum-ami', true);

      // Then
      expect(spy).toHaveBeenCalledWith('dinum-ami', true);
    });
  });
  describe('hasAnyConsents', () => {
    test('should return false when no consent', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      vi.spyOn(apiConsentsMethods, 'retrieveConsents').mockResolvedValue({
        consents: [],
      });

      // When
      const result = await hasAnyConsents();

      // Then
      expect(result).toBeFalsy();
    });
    test('should return false when consent has no consent_datetime', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const consentsItem = {
        partner_id: 'psl',
        consent_datetime: null,
      };
      vi.spyOn(apiConsentsMethods, 'retrieveConsents').mockResolvedValue({
        consents: [consentsItem],
      });

      // When
      const result = await hasAnyConsents();

      // Then
      expect(result).toBeFalsy();
    });
    test('should return true when at least one consent has a consent_datetime', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const consentsItem1 = {
        partner_id: 'dinum-ami',
        consent_datetime: null,
      };
      const consentsItem2 = {
        partner_id: 'psl',
        consent_datetime: new Date('2026-02-22T15:50:00Z'),
      };
      vi.spyOn(apiConsentsMethods, 'retrieveConsents').mockResolvedValue({
        consents: [consentsItem1, consentsItem2],
      });

      // When
      const result = await hasAnyConsents();

      // Then
      expect(result).toBeTruthy();
    });
  });
});
