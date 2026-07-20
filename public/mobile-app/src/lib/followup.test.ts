import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiFollowupMethods from '$lib/api-followup';
import {
  buildFollowup,
  Followup,
  FollowupItem,
  FollowupItemEvent,
  FollowupItem as Item,
} from '$lib/followup';

describe('/followup.ts', () => {
  describe('FollowupItemEvent', () => {
    describe('formattedDate', () => {
      test('should return localized date and hour', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
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
  describe('FollowupItem', () => {
    describe('id', () => {
      test('should return an id from partner_id, item_type and item_external_id', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new FollowupItem(
          'partner',
          'type',
          'id',
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
          null
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
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new FollowupItem(
          'partner',
          'type',
          'id',
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
          null
        );

        // When
        const date = item.formattedDate;

        // Then
        expect(date).equal('le 3 janvier à 09H05');
      });
    });
    describe('itemDetailPageUrl', () => {
      test('should return detail page url without is_archived query param when item is not archived', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new Item(
          'partner',
          'type',
          'id',
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
        const link = item.itemDetailPageUrl;

        // Then
        expect(link).equal('/#/followup/item/partner/type/id');
      });
      test('should return detail page url with is_archived query param when item is archived', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new Item(
          'partner',
          'type',
          'id',
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
          'url'
        );

        // When
        const link = item.itemDetailPageUrl;

        // Then
        expect(link).equal('/#/followup/item/partner/type/id?is_archived=true');
      });
    });
    describe('archive', () => {
      test('should call archiveFollowupItem', async () => {
        // Given
        const item = new FollowupItem(
          'partner',
          'type',
          'id',
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
          null
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
      vi.stubEnv('TZ', 'Europe/Paris');
      const followupItem1 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '42',
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
      };
      const followupItem2 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '43',
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
      };
      const followupItem3 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '44',
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
      };
      const followupItem4 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '45',
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
      };

      // When
      const followup = new Followup({
        notifications: [followupItem1, followupItem2, followupItem3, followupItem4],
      });

      // Then
      expect(followup.items.length).equal(2);
      expect(
        followup.items[0].equals(
          new FollowupItem(
            'psl',
            'OperationTranquilliteVacances',
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
            null
          )
        )
      ).toBe(true);
      expect(
        followup.items[1].equals(
          new FollowupItem(
            'psl',
            'OperationTranquilliteVacances',
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
            null
          )
        )
      ).toBe(true);
      expect(followup.archived_items.length).equal(2);
      expect(
        followup.archived_items[0].equals(
          new FollowupItem(
            'psl',
            'OperationTranquilliteVacances',
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
            null
          )
        )
      ).toBe(true);
      expect(
        followup.archived_items[1].equals(
          new FollowupItem(
            'psl',
            'OperationTranquilliteVacances',
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
            null
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
        };
        const followupItem2 = {
          partner_id: 'psl',
          item_type: 'Other',
          item_external_id: '43',
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
        };
        const followupItem3 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '44',
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
        };
        const followupItem4 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '45',
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
        };
        const followupItem5 = {
          partner_id: 'psl',
          item_type: 'OperationTranquilliteVacances',
          item_external_id: '46',
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
  });
  describe('buildFollowup', () => {
    test('should retrieve inventories and init followup with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const followupItem1 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '42',
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
      };
      const followupItem2 = {
        partner_id: 'psl',
        item_type: 'OperationTranquilliteVacances',
        item_external_id: '43',
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
          new FollowupItem(
            'psl',
            'OperationTranquilliteVacances',
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
            null
          )
        )
      ).toBe(true);
      expect(followup.archived_items.length).equal(1);
      expect(
        followup.archived_items[0].equals(
          new FollowupItem(
            'psl',
            'OperationTranquilliteVacances',
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
            null
          )
        )
      ).toBe(true);
    });
  });
});
