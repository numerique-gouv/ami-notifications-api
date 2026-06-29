import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiFollowUpMethods from '$lib/api-followup';
import { buildFollowUp, FollowUp, RequestItem } from '$lib/follow-up';

describe('/follow-up.ts', () => {
  describe('RequestItem', () => {
    describe('id', () => {
      test('should return an id from partner_id, external_item_type and external_item_id', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new RequestItem(
          'partner',
          'type',
          'id',
          'notifications',
          'title',
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
        const item = new RequestItem(
          'partner',
          'type',
          'id',
          'notifications',
          'title',
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
    describe('archive', () => {
      test('should call archiveFollowUpItem', async () => {
        // Given
        const item = new RequestItem(
          'partner',
          'type',
          'id',
          'notifications',
          'title',
          'description',
          'icon',
          new Date('2026-01-03T08:05:42Z'),
          'new',
          'New',
          false,
          null
        );
        const spy = vi
          .spyOn(apiFollowUpMethods, 'archiveFollowUpItem')
          .mockResolvedValue(true);

        // When
        const result = await item.archive();

        // Then
        expect(result).toEqual(true);
        expect(spy).toHaveBeenCalledExactlyOnceWith('notifications', 'partner:type:id');
      });
    });
  });
  describe('FollowUp', () => {
    test('should organize items in items and archived_items', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const request1 = {
        partner_id: 'psl',
        external_item_type: 'OperationTranquilliteVacances',
        external_item_id: '42',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        icon: 'icon',
        is_archived: false,
        external_url: null,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
      };
      const request2 = {
        partner_id: 'psl',
        external_item_type: 'OperationTranquilliteVacances',
        external_item_id: '43',
        status_id: 'wip',
        status_label: 'En cours',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en cours de traitement.',
        icon: 'icon',
        is_archived: false,
        external_url: null,
        created_at: new Date('2026-02-22T15:50:00Z'),
        updated_at: new Date('2026-02-22T15:55:00Z'),
      };
      const request3 = {
        partner_id: 'psl',
        external_item_type: 'OperationTranquilliteVacances',
        external_item_id: '44',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        icon: 'icon',
        is_archived: true,
        external_url: null,
        created_at: new Date('2026-02-21T15:50:00Z'),
        updated_at: new Date('2026-02-21T15:55:00Z'),
      };
      const request4 = {
        partner_id: 'psl',
        external_item_type: 'OperationTranquilliteVacances',
        external_item_id: '45',
        status_id: 'closed',
        status_label: 'Terminée',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est terminée.',
        icon: 'icon',
        is_archived: true,
        external_url: null,
        created_at: new Date('2026-02-20T15:50:00Z'),
        updated_at: new Date('2026-02-20T15:55:00Z'),
      };

      // When
      const followUp = new FollowUp({
        notifications: [request1, request2, request3, request4],
      });

      // Then
      expect(followUp.items.length).equal(2);
      expect(
        followUp.items[0].equals(
          new RequestItem(
            'psl',
            'OperationTranquilliteVacances',
            '42',
            'notifications',
            'Opération Tranquillité Vacances',
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
        followUp.items[1].equals(
          new RequestItem(
            'psl',
            'OperationTranquilliteVacances',
            '43',
            'notifications',
            'Opération Tranquillité Vacances',
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
      expect(followUp.archived_items.length).equal(2);
      expect(
        followUp.archived_items[0].equals(
          new RequestItem(
            'psl',
            'OperationTranquilliteVacances',
            '44',
            'notifications',
            'Opération Tranquillité Vacances',
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
        followUp.archived_items[1].equals(
          new RequestItem(
            'psl',
            'OperationTranquilliteVacances',
            '45',
            'notifications',
            'Opération Tranquillité Vacances',
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
      test('should return true as "new" item exists for the external_item_type', async () => {
        // Given
        const request = {
          partner_id: 'psl',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '42',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const followUp = new FollowUp({
          notifications: [request],
        });

        // When
        const result = followUp.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(true);
      });
      test('should return true as "wip" item exists for the external_item_type', async () => {
        // Given
        const request = {
          partner_id: 'psl',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '42',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const followUp = new FollowUp({
          notifications: [request],
        });

        // When
        const result = followUp.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(true);
      });
      test('should return true as "closed" item exists for the external_item_type', async () => {
        // Given
        const request = {
          partner_id: 'psl',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '42',
          status_id: 'closed',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const followUp = new FollowUp({
          notifications: [request],
        });

        // When
        const result = followUp.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(true);
      });
      test('should return false as archived items exist for the external_item_type', async () => {
        // Given
        const request1 = {
          partner_id: 'other',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '42',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const request2 = {
          partner_id: 'psl',
          external_item_type: 'Other',
          external_item_id: '43',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: false,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const request3 = {
          partner_id: 'psl',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '44',
          status_id: 'new',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const request4 = {
          partner_id: 'psl',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '45',
          status_id: 'wip',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const request5 = {
          partner_id: 'psl',
          external_item_type: 'OperationTranquilliteVacances',
          external_item_id: '46',
          status_id: 'closed',
          status_label: 'Brouillon',
          milestone_start_date: new Date('2026-01-23T15:50:00Z'),
          milestone_end_date: null,
          title: 'Opération Tranquillité Vacances',
          description: 'Votre demande est en brouillon.',
          icon: 'icon',
          is_archived: true,
          external_url: null,
          created_at: new Date('2026-02-23T15:50:00Z'),
          updated_at: new Date('2026-02-23T15:55:00Z'),
        };
        const followUp = new FollowUp({
          notifications: [request1, request2, request3, request4, request5],
        });

        // When
        const result = followUp.hasNonArchivedItems(
          'psl',
          'OperationTranquilliteVacances'
        );

        // Then
        expect(result).toEqual(false);
      });
    });
  });
  describe('buildFollowUp', () => {
    test('should retrieve inventories and init follow-up with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const request1 = {
        partner_id: 'psl',
        external_item_type: 'OperationTranquilliteVacances',
        external_item_id: '42',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        icon: 'icon',
        is_archived: false,
        external_url: null,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
      };
      const request2 = {
        partner_id: 'psl',
        external_item_type: 'OperationTranquilliteVacances',
        external_item_id: '43',
        status_id: 'closed',
        status_label: 'Terminée',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est terminée.',
        icon: 'icon',
        is_archived: true,
        external_url: null,
        created_at: new Date('2026-02-22T15:50:00Z'),
        updated_at: new Date('2026-02-22T15:55:00Z'),
      };
      const spy = vi.spyOn(apiFollowUpMethods, 'retrieveFollowUp').mockResolvedValue({
        notifications: [request1, request2],
      });

      // When
      const followUp = await buildFollowUp();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(followUp).toBeInstanceOf(FollowUp);
      expect(followUp.items.length).equal(1);
      expect(
        followUp.items[0].equals(
          new RequestItem(
            'psl',
            'OperationTranquilliteVacances',
            '42',
            'notifications',
            'Opération Tranquillité Vacances',
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
      expect(followUp.archived_items.length).equal(1);
      expect(
        followUp.archived_items[0].equals(
          new RequestItem(
            'psl',
            'OperationTranquilliteVacances',
            '43',
            'notifications',
            'Opération Tranquillité Vacances',
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
