import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiFollowupMethods from '$lib/api-followup';
import {
  buildFollowup,
  Followup,
  FollowupItemEvent,
  FollowupItem as Item,
  FollowupSubItem as SubItem,
} from '$lib/followup';

describe('/followup.ts', () => {
  describe('FollowupItemEvent', () => {
    describe('formattedDate', () => {
      test('should return localized date and hour', async () => {
        // Given
        const item = new FollowupItemEvent(
          'fake-id',
          new Date('2026-01-03T08:05:42Z'),
          'Lorem ipsum'
        );

        // When
        const date = item.formattedDate;

        // Then
        expect(date).equal('03 janvier 2026 - 09:05');
      });
    });
  });
  describe('FollowupSubItem', () => {
    describe('getItemDetailPageUrl', () => {
      test('should return detail page url from partner_id, item_type and item_external_id', async () => {
        // Given
        const item = new Item(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          'url',
          []
        );
        const sub_item = new SubItem(
          'partner2',
          'type2',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          'url'
        );

        // When
        const link = sub_item.getItemDetailPageUrl(item);

        // Then
        expect(link).equal(
          '/#/followup/item/partner/type/id/subitem/partner2/type2/id2'
        );
      });
    });
    describe('badgeClassName', () => {
      test('should return class name depending on status_if', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'new',
          'Terminée',
          false,
          'url'
        );
        const item2 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'wip',
          'Terminée',
          false,
          'url'
        );
        const item3 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          'url'
        );
        const item4 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          // @ts-expect-error: `'incorrect'` isn't a proper Status, so typescript will complain
          'incorrect',
          'Terminée',
          false,
          'url'
        );

        // When
        const className1 = item1.badgeClassName;
        const className2 = item2.badgeClassName;
        const className3 = item3.badgeClassName;
        const className4 = item4.badgeClassName;

        // Then
        expect(className1).equal(
          'fr-background-contrast--yellow-moutarde fr-text-label--yellow-moutarde'
        );
        expect(className2).equal('fr-text-default--info fr-background-contrast--info');
        expect(className3).equal('fr-badge--purple-glycine');
        expect(className4).equal('');
      });
    });
  });
  describe('FollowupItem', () => {
    describe('id', () => {
      test('should return an id from partner_id, item_type and item_external_id', async () => {
        // Given
        const item = new Item(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'title',
          'subheading',
          'description',
          'icon',
          new Date('2026-01-03T08:05:42Z'),
          'new',
          'New',
          false,
          null,
          []
        );

        // When
        const id = item.id;

        // Then
        expect(id).equal('partner:type:id');
      });
    });
    describe('formattedDate', () => {
      test('should return localized date and hour, without year', async () => {
        // Given
        const item = new Item(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'title',
          'subheading',
          'description',
          'icon',
          new Date('2026-01-03T08:05:42Z'),
          'new',
          'New',
          false,
          null,
          []
        );

        // When
        const date = item.formattedDate;

        // Then
        expect(date).equal('03 janvier 2026 - 09:05');
      });
    });
    describe('getItemDetailPageUrl', () => {
      test('should return detail page url from partner_id, item_type and item_external_id', async () => {
        // Given
        const item = new Item(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          'url',
          []
        );

        // When
        const link = item.getItemDetailPageUrl();

        // Then
        expect(link).equal('/#/followup/item/partner/type/id');
      });
    });
    describe('findSubItem', () => {
      test('should return sub item is exists', async () => {
        // Given
        const followupSubItem1 = {
          partner_id: 'dinum-dn',
          item_type: 'JeDéménage',
          item_external_id: '44',
          reference: '44',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Je déménage',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const followupSubItem2 = {
          partner_id: 'psl',
          item_type: 'JeDéménage',
          item_external_id: '45',
          reference: '45',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Je déménage',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const followupItem = {
          partner_id: 'dinum-ami',
          item_type: 'JeDéménage',
          item_external_id: '43',
          reference: '43',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Je déménage',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [followupSubItem1, followupSubItem2],
        };
        const followup = new Followup({
          notifications: [followupItem],
        });
        const item = followup.items[0];

        // When
        const result1 = item.findSubItem('dinum-dn', 'JeDéménage', '44');
        const result2 = item.findSubItem('other', 'JeDéménage', '44');
        const result3 = item.findSubItem('dinum-dn', 'other', '44');
        const result4 = item.findSubItem('dinum-dn', 'JeDéménage', 'other');
        const result5 = item.findSubItem('psl', 'JeDéménage', '45');

        // Then
        expect(
          result1?.equals(
            new SubItem(
              'dinum-dn',
              'JeDéménage',
              '44',
              '44',
              'notifications',
              [],
              'Je déménage',
              'subheading',
              'Votre demande est en brouillon.',
              'icon',
              new Date('2026-02-23T15:55:00Z'),
              'new',
              'Brouillon',
              false,
              null
            )
          )
        ).toBe(true);
        expect(result2).toBeNull();
        expect(result3).toBeNull();
        expect(result4).toBeNull();
        expect(
          result5?.equals(
            new SubItem(
              'psl',
              'JeDéménage',
              '45',
              '45',
              'notifications',
              [],
              'Je déménage',
              'subheading',
              'Votre demande est en brouillon.',
              'icon',
              new Date('2026-02-23T15:55:00.000Z'),
              'new',
              'Brouillon',
              false,
              null
            )
          )
        ).toBe(true);
      });
    });
    describe('archive', () => {
      test('should call archiveFollowupItem', async () => {
        // Given
        const item = new Item(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          [],
          'title',
          'subheading',
          'description',
          'icon',
          new Date('2026-01-03T08:05:42Z'),
          'new',
          'New',
          false,
          null,
          []
        );
        const spy = vi
          .spyOn(apiFollowupMethods, 'archiveFollowupItem')
          .mockResolvedValue(true);

        // When
        const result = await item.archive();

        // Then
        expect(result).toEqual(true);
        expect(spy).toHaveBeenCalledExactlyOnceWith('notifications', 'partner:type:id');
      });
    });
  });
  describe('Followup', () => {
    test('should organize items in items and archived_items', async () => {
      // Given
      const followupItem1 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '42',
        reference: '42',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: null,
        events: [],
        title: 'Opération Tranquillité Vacances',
        subheading: 'subheading',
        description: 'Votre demande est en brouillon.',
        icon: 'icon',
        is_archived: false,
        external_url: null,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
        sub_items: [],
      };
      const followupItem2 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '43',
        reference: '43',
        status_id: 'wip',
        status_label: 'En cours',
        milestone_start_date: null,
        milestone_end_date: null,
        events: [],
        title: 'Opération Tranquillité Vacances',
        subheading: 'subheading',
        description: 'Votre demande est en cours de traitement.',
        icon: 'icon',
        is_archived: false,
        external_url: null,
        created_at: new Date('2026-02-22T15:50:00Z'),
        updated_at: new Date('2026-02-22T15:55:00Z'),
        sub_items: [],
      };
      const followupItem3 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '44',
        reference: '44',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: null,
        events: [],
        title: 'Opération Tranquillité Vacances',
        subheading: 'subheading',
        description: 'Votre demande est en brouillon.',
        icon: 'icon',
        is_archived: true,
        external_url: null,
        created_at: new Date('2026-02-21T15:50:00Z'),
        updated_at: new Date('2026-02-21T15:55:00Z'),
        sub_items: [],
      };
      const followupItem4 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '45',
        reference: '45',
        status_id: 'closed',
        status_label: 'Terminée',
        milestone_start_date: null,
        milestone_end_date: null,
        events: [],
        title: 'Opération Tranquillité Vacances',
        subheading: 'subheading',
        description: 'Votre demande est terminée.',
        icon: 'icon',
        is_archived: true,
        external_url: null,
        created_at: new Date('2026-02-20T15:50:00Z'),
        updated_at: new Date('2026-02-20T15:55:00Z'),
        sub_items: [],
      };

      // When
      const followup = new Followup({
        notifications: [followupItem1, followupItem2, followupItem3, followupItem4],
      });

      // Then
      expect(followup.items.length).equal(2);
      expect(
        followup.items[0].equals(
          new Item(
            'psl',
            'OperationTranquilliteVacances',
            '42',
            '42',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en brouillon.',
            'icon',
            new Date('2026-02-23T15:55:00.000Z'),
            'new',
            'Brouillon',
            false,
            null,
            []
          )
        )
      ).toBe(true);
      expect(
        followup.items[1].equals(
          new Item(
            'psl',
            'OperationTranquilliteVacances',
            '43',
            '43',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en cours de traitement.',
            'icon',
            new Date('2026-02-22T15:55:00.000Z'),
            'wip',
            'En cours',
            false,
            null,
            []
          )
        )
      ).toBe(true);
      expect(followup.archived_items.length).equal(2);
      expect(
        followup.archived_items[0].equals(
          new Item(
            'psl',
            'OperationTranquilliteVacances',
            '44',
            '44',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en brouillon.',
            'icon',
            new Date('2026-02-21T15:55:00.000Z'),
            'new',
            'Brouillon',
            true,
            null,
            []
          )
        )
      ).toBe(true);
      expect(
        followup.archived_items[1].equals(
          new Item(
            'psl',
            'OperationTranquilliteVacances',
            '45',
            '45',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est terminée.',
            'icon',
            new Date('2026-02-20T15:55:00.000Z'),
            'closed',
            'Terminée',
            true,
            null,
            []
          )
        )
      ).toBe(true);
    });
    describe('hasNonArchivedItems', () => {
      test('should return true as "new" item exists for the item_type', async () => {
        // Given
        const followupItem = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '42',
          reference: '42',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followup = new Followup({
          notifications: [followupItem],
        });

        // When
        const result = followup.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(true);
      });
      test('should return true as "wip" item exists for the item_type', async () => {
        // Given
        const followupItem = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '42',
          reference: '42',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followup = new Followup({
          notifications: [followupItem],
        });

        // When
        const result = followup.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(true);
      });
      test('should return true as "closed" item exists for the item_type', async () => {
        // Given
        const followupItem = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '42',
          reference: '42',
          status_id: 'closed',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followup = new Followup({
          notifications: [followupItem],
        });

        // When
        const result = followup.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(true);
      });
      test('should return false as archived items exist for the item_type', async () => {
        // Given
        const followupItem1 = {
          partner_id: 'other',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '42',
          reference: '42',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followupItem2 = {
          partner_id: 'psl',
          item_type: 'Other',
          item_external_id: '43',
          reference: '43',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followupItem3 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '44',
          reference: '44',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followupItem4 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '45',
          reference: '45',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followupItem5 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '46',
          reference: '46',
          status_id: 'closed',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followup = new Followup({
          notifications: [
            followupItem1,
            followupItem2,
            followupItem3,
            followupItem4,
            followupItem5,
          ],
        });

        // When
        const result = followup.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(false);
      });
    });
    describe('findItem', () => {
      test('should return item from items of archived_items if exists', async () => {
        // Given
        const followupItem1 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '42',
          reference: '42',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Opération Tranquillité Vacances',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [],
        };
        const followupItem2 = {
          partner_id: 'dinum-ami',
          item_type: 'JeDéménage',
          item_external_id: '43',
          reference: '43',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          events: [],
          title: 'Je déménage',
          subheading: 'subheading',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
          sub_items: [
            {
              partner_id: 'dinum-dn',
              item_type: 'JeDéménage',
              item_external_id: '44',
              reference: '44',
              status_id: 'new',
              status_label: 'Brouillon',
              milestone_start_date: new Date('2026-01-23T15:50:00Z'),
              milestone_end_date: null,
              events: [],
              title: 'Je déménage',
              subheading: 'subheading',
              description: 'Votre demande est en brouillon.',
              icon: 'icon',
              is_archived: false,
              external_url: null,
              created_at: new Date('2026-02-23T15:50:00Z'),
              updated_at: new Date('2026-02-23T15:55:00Z'),
            },
          ],
        };
        const followup = new Followup({
          notifications: [followupItem1, followupItem2],
        });

        // When
        const result1 = followup.findItem('psl', 'OperationTranquilliteVacances', '42');
        const result2 = followup.findItem(
          'other',
          'OperationTranquilliteVacances',
          '42'
        );
        const result3 = followup.findItem('psl', 'other', '42');
        const result4 = followup.findItem(
          'psl',
          'OperationTranquilliteVacances',
          'other'
        );
        const result5 = followup.findItem('dinum-ami', 'JeDéménage', '43');
        const result6 = followup.findItem('other', 'JeDéménage', '43');
        const result7 = followup.findItem('dinum-ami', 'other', '43');
        const result8 = followup.findItem('dinum-ami', 'JeDéménage', 'other');
        const result9 = followup.findItem('dinum-dn', 'JeDéménage', '44'); // sub item

        // Then
        expect(
          result1?.equals(
            new Item(
              'psl',
              'OperationTranquilliteVacances',
              '42',
              '42',
              'notifications',
              [],
              'Opération Tranquillité Vacances',
              'subheading',
              'Votre demande est en brouillon.',
              'icon',
              new Date('2026-02-23T15:55:00.000Z'),
              'new',
              'Brouillon',
              false,
              null,
              []
            )
          )
        ).toBe(true);
        expect(result2).toBeNull();
        expect(result3).toBeNull();
        expect(result4).toBeNull();
        expect(
          result5?.equals(
            new Item(
              'dinum-ami',
              'JeDéménage',
              '43',
              '43',
              'notifications',
              [],
              'Je déménage',
              'subheading',
              'Votre demande est en brouillon.',
              'icon',
              new Date('2026-02-23T15:55:00.000Z'),
              'new',
              'Brouillon',
              true,
              null,
              [
                new SubItem(
                  'dinum-dn',
                  'JeDéménage',
                  '44',
                  '44',
                  'notifications',
                  [],
                  'Je déménage',
                  'subheading',
                  'Votre demande est en brouillon.',
                  'icon',
                  new Date('2026-02-23T15:55:00Z'),
                  'new',
                  'Brouillon',
                  false,
                  null
                ),
              ]
            )
          )
        ).toBe(true);
        expect(result6).toBeNull();
        expect(result7).toBeNull();
        expect(result8).toBeNull();
        expect(result9).toBeNull();
      });
    });
  });
  describe('buildFollowup', () => {
    test('should retrieve inventories and init followup with them', async () => {
      // Given
      const followupItem1 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '42',
        reference: '42',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: null,
        milestone_end_date: null,
        events: [],
        title: 'Opération Tranquillité Vacances',
        subheading: 'subheading',
        description: 'Votre demande est en brouillon.',
        icon: 'icon',
        is_archived: false,
        external_url: null,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
        sub_items: [],
      };
      const followupItem2 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '43',
        reference: '43',
        status_id: 'closed',
        status_label: 'Terminée',
        milestone_start_date: null,
        milestone_end_date: null,
        events: [],
        title: 'Opération Tranquillité Vacances',
        subheading: 'subheading',
        description: 'Votre demande est terminée.',
        icon: 'icon',
        is_archived: true,
        external_url: null,
        created_at: new Date('2026-02-22T15:50:00Z'),
        updated_at: new Date('2026-02-22T15:55:00Z'),
        sub_items: [],
      };
      const spy = vi.spyOn(apiFollowupMethods, 'retrieveFollowup').mockResolvedValue({
        notifications: [followupItem1, followupItem2],
      });

      // When
      const followup = await buildFollowup();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(followup).toBeInstanceOf(Followup);
      expect(followup.items.length).equal(1);
      expect(
        followup.items[0].equals(
          new Item(
            'psl',
            'OperationTranquilliteVacances',
            '42',
            '42',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en brouillon.',
            'icon',
            new Date('2026-02-23T15:55:00.000Z'),
            'new',
            'Brouillon',
            false,
            null,
            []
          )
        )
      ).toBe(true);
      expect(followup.archived_items.length).equal(1);
      expect(
        followup.archived_items[0].equals(
          new Item(
            'psl',
            'OperationTranquilliteVacances',
            '43',
            '43',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est terminée.',
            'icon',
            new Date('2026-02-22T15:55:00.000Z'),
            'closed',
            'Terminée',
            true,
            null,
            []
          )
        )
      ).toBe(true);
    });
  });
});
