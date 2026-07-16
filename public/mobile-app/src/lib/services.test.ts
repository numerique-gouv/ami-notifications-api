import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiServicesMethods from '$lib/api-services';
import { buildServices, Services, ServicesItem } from '$lib/services';

describe('/services.ts', () => {
  beforeEach(() => {
    localStorage.clear();
  });
  describe('ServicesItem', () => {
    describe('id', () => {
      test('should return an id from partner_id and item_type', async () => {
        // Given
        const item = new ServicesItem(
          'partner',
          'type',
          'title',
          'short description',
          'description',
          'external-url',
          false
        );

        // When
        const id = item.id;

        // Then
        expect(id).equal('partner:type');
      });
    });
    describe('formatDescription', () => {
      test('should replace {date} by parameter', async () => {
        // Given
        const item1 = new ServicesItem(
          'partner',
          'type',
          'title',
          'short description',
          'description',
          'external-url',
          false
        );
        const item2 = new ServicesItem(
          'partner',
          'type',
          'title',
          'short description',
          'description {date}',
          'external-url',
          false
        );

        // When
        const description1 = item1.formatDescription('date1');
        const description2 = item2.formatDescription('date2');

        // Then
        expect(description1).equal('description');
        expect(description2).equal('description date2');
      });
    });
    describe('getServiceUrl', () => {
      test('should replace {fc_hash}', async () => {
        // Given
        window.localStorage.setItem('user_fc_hash', 'fake-user-fc-hash');
        const item = new ServicesItem(
          'partner',
          'type',
          'title',
          'short description',
          'description',
          'external-url?id_hash_fc={fc_hash}',
          false
        );

        // When
        const url = await item.getServiceUrl();

        // Then
        expect(url).equal('external-url?id_hash_fc=fake-user-fc-hash');
      });
      test('should replace {fc_hash} - fc_hash is empty', async () => {
        // Given
        const item = new ServicesItem(
          'partner',
          'type',
          'title',
          'short description',
          'description',
          'external-url?id_hash_fc={fc_hash}',
          false
        );

        // When
        const url = await item.getServiceUrl();

        // Then
        expect(url).equal('external-url?id_hash_fc=');
      });
    });
  });
  describe('Services', () => {
    test('should order items', async () => {
      // Given
      const servicesItem1 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        title: 'Opération Tranquillité Vacances',
        short_description: 'Sécurisez votre logement',
        description: 'Vous partez en vacances ? **Securisez votre logement.**',
        url: 'http://external-url',
        with_silent_login: true,
      };
      const servicesItem2 = {
        partner_id: 'dinum-dn',
        item_type: 'JeDéménage',
        title: 'Je déménage',
        short_description: 'Indiquez votre nouvelle adresse',
        description: 'Vous déménagez ? **Indiquez votre nouvelle adresse.**',
        url: 'http://external-url',
        with_silent_login: false,
      };

      // When
      const services = new Services({
        internal: [servicesItem1, servicesItem2],
      });

      // Then
      expect(services.items.length).equal(2);
      expect(
        services.items[0].equals(
          new ServicesItem(
            'dinum-dn',
            'JeDéménage',
            'Je déménage',
            'Indiquez votre nouvelle adresse',
            'Vous déménagez ? **Indiquez votre nouvelle adresse.**',
            'http://external-url',
            false
          )
        )
      ).toBe(true);
      expect(
        services.items[1].equals(
          new ServicesItem(
            'psl',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'http://external-url',
            true
          )
        )
      ).toBe(true);
    });
    describe('find', () => {
      test('should return only one matching service', async () => {
        // Given
        const servicesItem1 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          title: 'Opération Tranquillité Vacances',
          short_description: 'Sécurisez votre logement',
          description: 'Vous partez en vacances ? **Securisez votre logement.**',
          url: 'http://external-url',
          with_silent_login: true,
        };
        const servicesItem2 = {
          partner_id: 'dinum-dn',
          item_type: 'JeDéménage',
          title: 'Je déménage',
          short_description: 'Indiquez votre nouvelle adresse',
          description: 'Vous déménagez ? **Indiquez votre nouvelle adresse.**',
          url: 'http://external-url',
          with_silent_login: false,
        };
        const servicesItem3 = {
          partner_id: 'dinum-dn',
          item_type: 'JeDéménage',
          title: 'Je déménage',
          short_description: 'Indiquez votre nouvelle adresse',
          description: 'Vous déménagez ? **Indiquez votre nouvelle adresse.**',
          url: 'http://external-url',
          with_silent_login: false,
        };
        const services = new Services({
          internal: [servicesItem1, servicesItem2, servicesItem3],
        });

        // When
        const find1 = services.find('psl', 'OperationTranquilliteVacances');
        const find2 = services.find('dinum-dn', 'JeDéménage');
        const find3 = services.find('unknown', 'unknown');

        // Then
        expect(find1).not.toBeNull();
        expect(
          find1?.equals(
            new ServicesItem(
              'psl',
              'OperationTranquilliteVacances',
              'Opération Tranquillité Vacances',
              'Sécurisez votre logement',
              'Vous partez en vacances ? **Securisez votre logement.**',
              'http://external-url',
              true
            )
          )
        ).toBe(true);
        expect(find2).toBeNull();
        expect(find3).toBeNull();
      });
    });
  });
  describe('buildServices', () => {
    test('should retrieve sources and init services with them', async () => {
      // Given
      const servicesItem = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        title: 'Opération Tranquillité Vacances',
        short_description: 'Sécurisez votre logement',
        description: 'Vous partez en vacances ? **Securisez votre logement.**',
        url: 'http://external-url',
        with_silent_login: true,
      };
      const spy = vi.spyOn(apiServicesMethods, 'retrieveServices').mockResolvedValue({
        internal: [servicesItem],
      });

      // When
      const services = await buildServices();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(services).toBeInstanceOf(Services);
      expect(services.items.length).equal(1);
      expect(
        services.items[0].equals(
          new ServicesItem(
            'psl',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'http://external-url',
            true
          )
        )
      ).toBe(true);
    });
  });
});
