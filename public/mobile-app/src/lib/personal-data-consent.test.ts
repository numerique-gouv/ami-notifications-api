import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiPersonalDataConsentMethods from '$lib/api-personal-data-consent';
import {
  buildPersonalDataConsent,
  PersonalDataConsent,
} from '$lib/personal-data-consent';

describe('/personal-data-consent.ts', () => {
  describe('PersonalDataConsent', () => {
    test('should create item from api', async () => {
      // Given
      const apiPersonalDataConsent = {
        consent_datetime: new Date('2026-01-23T15:50:00Z'),
      };

      // When
      const personalDataConsent = new PersonalDataConsent(apiPersonalDataConsent);

      // Then
      expect(personalDataConsent).toBeInstanceOf(PersonalDataConsent);
      expect(personalDataConsent.consent_datetime).toEqual(
        new Date('2026-01-23T15:50:00Z')
      );
    });
    describe('updateConsent', () => {
      test('should call update personal-data-consent from api', async () => {
        // Given
        const apiPersonalDataConsent = {
          consent_datetime: new Date('2026-01-23T15:50:00Z'),
        };
        const personalDataConsent = new PersonalDataConsent(apiPersonalDataConsent);

        const spy = vi
          .spyOn(apiPersonalDataConsentMethods, 'updateApiPersonalDataConsent')
          .mockResolvedValue(true);

        // When
        const result = await personalDataConsent.updateConsent(true);

        // Then
        expect(spy).toHaveBeenCalledWith(true);
        expect(result).toBeTruthy();
      });
    });
  });
  describe('buildPersonalDataConsent', () => {
    test('should retrieve apiConsent and init consent with it', async () => {
      // Given
      const apiPersonalDataConsent = {
        consent_datetime: new Date('2026-01-23T15:50:00Z'),
      };
      const spy = vi
        .spyOn(apiPersonalDataConsentMethods, 'retrievePersonalDataConsent')
        .mockResolvedValue(apiPersonalDataConsent);

      // When
      const personalDataConsent = await buildPersonalDataConsent();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(personalDataConsent).toBeInstanceOf(PersonalDataConsent);
      expect(personalDataConsent.consent_datetime).toEqual(
        new Date('2026-01-23T15:50:00Z')
      );
    });
  });
});
