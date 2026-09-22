import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiConsentsMethods from '$lib/api-consents';
import {
  buildConsents,
  Consents,
  ConsentsItem,
  updateAllConsents,
  updateConsent,
} from '$lib/consents';
import { Followup, FollowupItem } from '$lib/followup';
import { Partners } from '$lib/partners';

describe('/consents.ts', () => {
  describe('ConsentsItem', () => {
    describe('hasFollowupItem', () => {
      test('should return false when followup is null', async () => {
        // Given
        const consentsItem = new ConsentsItem(
          'dinum-ami',
          'AMI',
          new Date('2026-01-23T15:50:00Z')
        );

        // When
        const result = consentsItem.hasFollowupItem(null);

        // Then
        expect(result).toBeFalsy();
      });
      test('should return false when followup has no item', async () => {
        // Given
        const consentsItem = new ConsentsItem(
          'dinum-ami',
          'AMI',
          new Date('2026-01-23T15:50:00Z')
        );

        const followup: Followup = new Followup();
        vi.spyOn(followup, 'items', 'get').mockReturnValue([]);

        // When
        const result = consentsItem.hasFollowupItem(followup);

        // Then
        expect(result).toBeFalsy();
      });
      test('should return false when followup has no item of the existing partner', async () => {
        // Given
        const consentsItem = new ConsentsItem(
          'dinum-ami',
          'AMI',
          new Date('2026-01-23T15:50:00Z')
        );

        const item: FollowupItem = new FollowupItem(
          'partner',
          'type',
          'id1',
          'ref1',
          'notifications',
          null,
          null,
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        );
        const followup: Followup = new Followup();
        vi.spyOn(followup, 'items', 'get').mockReturnValue([item]);

        // When
        const result = consentsItem.hasFollowupItem(followup);

        // Then
        expect(result).toBeFalsy();
      });
      test('should return true when followup has at least one item of the existing partner', async () => {
        // Given
        const consentsItem = new ConsentsItem(
          'dinum-ami',
          'AMI',
          new Date('2026-01-23T15:50:00Z')
        );

        const item: FollowupItem = new FollowupItem(
          'dinum-ami',
          'type',
          'id1',
          'ref1',
          'notifications',
          null,
          null,
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        );
        const followup: Followup = new Followup();
        vi.spyOn(followup, 'items', 'get').mockReturnValue([item]);

        // When
        const result = consentsItem.hasFollowupItem(followup);

        // Then
        expect(result).toBeTruthy();
      });
    });
  });
  describe('Consents', () => {
    test('should create items from api', async () => {
      // Given
      const apiConsentsItem1 = {
        partner_id: 'dinum-ami',
        partner_name: 'AMI',
        consent_datetime: new Date('2026-01-23T15:50:00Z'),
      };
      const apiConsentsItem2 = {
        partner_id: 'psl',
        partner_name: 'Service Public',
        consent_datetime: new Date('2026-02-22T15:50:00Z'),
      };
      const apiConsentsItem3 = {
        partner_id: 'dinum-dn',
        partner_name: 'Démarche Numérique',
        consent_datetime: new Date('2026-02-21T15:50:00Z'),
      };
      const apiConsentsItem4 = {
        partner_id: 'rdv-sp',
        partner_name: 'Rendez-vous SP',
        consent_datetime: new Date('2026-02-21T15:50:00Z'),
      };

      const partnersItem1 = {
        slug: 'dinum-ami',
        name: 'AMI',
        link: 'https://fake-link-1',
      };
      const partnersItem2 = {
        slug: 'psl',
        name: 'Service Public',
        link: 'https://fake-link-2',
      };
      const partnersItem3 = {
        slug: 'dinum-dn',
        name: 'Démarche Numérique',
        link: 'https://fake-link-3',
      };
      const partnersItem4 = {
        slug: 'rdv-sp',
        name: 'RDV Service Public',
        link: 'https://fake-link-4',
      };
      const partners = new Partners([
        partnersItem1,
        partnersItem2,
        partnersItem3,
        partnersItem4,
      ]);

      // When
      const consents = new Consents(
        {
          consents: [
            apiConsentsItem1,
            apiConsentsItem2,
            apiConsentsItem3,
            apiConsentsItem4,
          ],
        },
        partners.items
      );

      // Then
      expect(consents.items.length).equal(4);
      expect(consents.items[0]).toBeInstanceOf(ConsentsItem);
      expect(consents.items[0].partner_id).toEqual('dinum-ami');
      expect(consents.items[0].partner_name).toEqual('AMI');
      expect(consents.items[0].consent_datetime).toEqual(
        new Date('2026-01-23T15:50:00Z')
      );
      expect(consents.items[1].partner_id).toEqual('dinum-dn');
      expect(consents.items[1].partner_name).toEqual('Démarche Numérique');
      expect(consents.items[1].consent_datetime).toEqual(
        new Date('2026-02-21T15:50:00Z')
      );
      expect(consents.items[2].partner_id).toEqual('psl');
      expect(consents.items[2].partner_name).toEqual('Service Public');
      expect(consents.items[2].consent_datetime).toEqual(
        new Date('2026-02-22T15:50:00Z')
      );
      expect(consents.items[3].partner_id).toEqual('rdv-sp');
      expect(consents.items[3].partner_name).toEqual('Rendez-vous SP');
      expect(consents.items[3].consent_datetime).toEqual(
        new Date('2026-02-21T15:50:00Z')
      );
    });
    describe('hasAnyConsents', () => {
      test('should return false when no consent', async () => {
        // Given
        const consents = new Consents({ consents: [] }, []);

        // When
        const result = consents.hasAnyConsents();

        // Then
        expect(result).toBeFalsy();
      });
      test('should return false when consent has no consent_datetime', async () => {
        // Given
        const consentsItem1 = {
          partner_id: 'dinum-ami',
          partner_name: 'AMI',
          consent_datetime: null,
        };
        const partnersItem = {
          slug: 'dinum-ami',
          name: 'AMI',
          link: 'https://fake-link-1',
        };
        const partners = new Partners([partnersItem]);

        const consents = new Consents({ consents: [consentsItem1] }, partners.items);

        // When
        const result = consents.hasAnyConsents();

        // Then
        expect(result).toBeFalsy();
      });
      test('should return true when at least one consent has a consent_datetime', async () => {
        // Given
        const consentsItem1 = {
          partner_id: 'dinum-ami',
          partner_name: 'AMI',
          consent_datetime: null,
        };
        const consentsItem2 = {
          partner_id: 'dinum-dn',
          partner_name: 'Démarche Numérique',
          consent_datetime: new Date('2026-02-22T15:50:00Z'),
        };
        const partnersItem1 = {
          slug: 'dinum-ami',
          name: 'AMI',
          link: 'https://fake-link-1',
        };
        const partnersItem2 = {
          slug: 'dinum-dn',
          name: 'Démarche Numérique',
          link: 'https://fake-link-2',
        };
        const partners = new Partners([partnersItem1, partnersItem2]);
        const consents = new Consents(
          { consents: [consentsItem1, consentsItem2] },
          partners.items
        );

        // When
        const result = consents.hasAnyConsents();

        // Then
        expect(result).toBeTruthy();
      });
    });
    describe('hasAllConsents', () => {
      test('should return false when no consent', async () => {
        // Given
        const partnersItem = {
          slug: 'dinum-ami',
          name: 'AMI',
          link: 'https://fake-link-1',
        };
        const partners = new Partners([partnersItem]);
        const consents = new Consents({ consents: [] }, partners.items);

        // When
        const result = consents.hasAllConsents();

        // Then
        expect(result).toBeFalsy();
      });
      test('should return false when consent has no consent_datetime', async () => {
        // Given
        const consentsItem1 = {
          partner_id: 'dinum-ami',
          partner_name: 'AMI',
          consent_datetime: null,
        };
        const partnersItem = {
          slug: 'dinum-ami',
          name: 'AMI',
          link: 'https://fake-link-1',
        };
        const partners = new Partners([partnersItem]);
        const consents = new Consents({ consents: [consentsItem1] }, partners.items);

        // When
        const result = consents.hasAllConsents();

        // Then
        expect(result).toBeFalsy();
      });
      test('should return false when at least one consent has a consent_datetime', async () => {
        // Given
        const consentsItem1 = {
          partner_id: 'dinum-ami',
          partner_name: 'AMI',
          consent_datetime: null,
        };
        const consentsItem2 = {
          partner_id: 'dinum-dn',
          partner_name: 'Démarche Numérique',
          consent_datetime: new Date('2026-02-22T15:50:00Z'),
        };
        const partnersItem1 = {
          slug: 'dinum-ami',
          name: 'AMI',
          link: 'https://fake-link-1',
        };
        const partnersItem2 = {
          slug: 'dinum-dn',
          name: 'Démarche Numérique',
          link: 'https://fake-link-2',
        };
        const partners = new Partners([partnersItem1, partnersItem2]);
        const consents = new Consents(
          { consents: [consentsItem1, consentsItem2] },
          partners.items
        );

        // When
        const result = consents.hasAllConsents();

        // Then
        expect(result).toBeFalsy();
      });
      test('should return true when all consents have a consent_datetime', async () => {
        // Given
        const consentsItem1 = {
          partner_id: 'dinum-ami',
          partner_name: 'AMI',
          consent_datetime: new Date('2026-01-23T15:50:00Z'),
        };
        const consentsItem2 = {
          partner_id: 'dinum-dn',
          partner_name: 'Démarche Numérique',
          consent_datetime: new Date('2026-02-22T15:50:00Z'),
        };
        const partnersItem1 = {
          slug: 'dinum-ami',
          name: 'AMI',
          link: 'https://fake-link-1',
        };
        const partnersItem2 = {
          slug: 'dinum-dn',
          name: 'Démarche Numérique',
          link: 'https://fake-link-2',
        };
        const partners = new Partners([partnersItem1, partnersItem2]);
        const consents = new Consents(
          { consents: [consentsItem1, consentsItem2] },
          partners.items
        );

        // When
        const result = consents.hasAllConsents();

        // Then
        expect(result).toBeTruthy();
      });
    });
  });
  describe('buildConsents', () => {
    test('should retrieve inventory and init consents with them', async () => {
      // Given
      const consentsItem1 = {
        partner_id: 'dinum-ami',
        partner_name: 'AMI',
        consent_datetime: new Date('2026-01-23T15:50:00Z'),
      };
      const consentsItem2 = {
        partner_id: 'dinum-dn',
        partner_name: 'Démarche Numérique',
        consent_datetime: new Date('2026-02-22T15:50:00Z'),
      };
      const spy = vi.spyOn(apiConsentsMethods, 'retrieveConsents').mockResolvedValue({
        consents: [consentsItem1, consentsItem2],
      });

      const partnersItem1 = {
        slug: 'dinum-ami',
        name: 'AMI',
        link: 'https://fake-link-1',
      };
      const partnersItem2 = {
        slug: 'dinum-dn',
        name: 'Démarche Numérique',
        link: 'https://fake-link-2',
      };
      const partners = new Partners([partnersItem1, partnersItem2]);

      // When
      const consents = await buildConsents(partners);

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(consents).toBeInstanceOf(Consents);
      expect(consents.items.length).equal(2);
      expect(consents.items[0]).toBeInstanceOf(ConsentsItem);
      expect(consents.items[0].partner_id).toEqual('dinum-ami');
      expect(consents.items[0].partner_name).toEqual('AMI');
      expect(consents.items[0].consent_datetime).toEqual(
        new Date('2026-01-23T15:50:00Z')
      );
      expect(consents.items[1].partner_id).toEqual('dinum-dn');
      expect(consents.items[1].partner_name).toEqual('Démarche Numérique');
      expect(consents.items[1].consent_datetime).toEqual(
        new Date('2026-02-22T15:50:00Z')
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
  describe('updateAllConsents', () => {
    test('should call update all consents from api', async () => {
      // Given
      const spy = vi.spyOn(apiConsentsMethods, 'updateAllApiConsents');

      // When
      await updateAllConsents(true);

      // Then
      expect(spy).toHaveBeenCalledWith(true);
    });
  });
});
