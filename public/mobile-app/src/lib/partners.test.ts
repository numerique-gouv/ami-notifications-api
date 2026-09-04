import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiPartnersMethods from '$lib/api-partners';
import { buildPartners, Partners, PartnersItem } from '$lib/partners';

describe('/partners.ts', () => {
  describe('Partners', () => {
    test('should create items from api', async () => {
      // Given
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
      const partnersItem3 = {
        slug: 'rdv-sp',
        name: 'RDV Service Public',
        link: 'https://fake-link-3',
      };

      // When
      const partners = new Partners([partnersItem1, partnersItem2, partnersItem3]);

      // Then
      expect(partners.items.length).equal(3);
      expect(partners.items[0]).toEqual(
        new PartnersItem('dinum-ami', 'AMI', 'https://fake-link-1')
      );
      expect(partners.items[1]).toEqual(
        new PartnersItem('dinum-dn', 'Démarche Numérique', 'https://fake-link-2')
      );
      expect(partners.items[2]).toEqual(
        new PartnersItem('rdv-sp', 'RDV Service Public', 'https://fake-link-3')
      );
    });
  });
  describe('buildPartners', () => {
    test('should retrieve inventory and init partners with them', async () => {
      // Given
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
      const spy = vi
        .spyOn(apiPartnersMethods, 'retrievePartners')
        .mockResolvedValue([partnersItem1, partnersItem2]);

      // When
      const partners = await buildPartners();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(partners).toBeInstanceOf(Partners);
      expect(partners.items.length).equal(2);
      expect(partners.items[0]).toEqual(
        new PartnersItem('dinum-ami', 'AMI', 'https://fake-link-1')
      );
      expect(partners.items[1]).toEqual(
        new PartnersItem('dinum-dn', 'Démarche Numérique', 'https://fake-link-2')
      );
    });
  });
});
