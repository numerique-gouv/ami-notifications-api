import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as apiFollowupMethods from '$lib/api-followup';
import * as followupMethods from '$lib/followup';
import {
  buildFollowup,
  Followup,
  FollowupItemEvent,
  getPeriod,
  FollowupItem as Item,
  FollowupSubItem as SubItem,
} from '$lib/followup';

describe('/followup.ts', () => {
  describe('getPeriod', () => {
    test('should return undefined', async () => {
      // When
      const result = getPeriod(null, null);

      // Then
      expect(result).toEqual(undefined);
    });
    test('should mention date and hour', async () => {
      // When
      const result1 = getPeriod(
        new Date('2025-09-20T15:05:00Z'),
        new Date('2025-09-20T15:05:00Z')
      );
      const result2 = getPeriod(
        new Date('2025-09-20T15:05:00Z'),
        new Date('2025-09-20T16:05:00Z')
      );

      // Then
      expect(result1).toEqual('Samedi 20 septembre à 17h05');
      expect(result2).toEqual('Samedi 20 septembre à 17h05');
    });
    test('should mention start date', async () => {
      // When
      const result = getPeriod(new Date('2025-09-20T15:05:00Z'), null);

      // Then
      expect(result).toEqual('À partir du samedi 20 septembre');
    });
    test('should mention end date', async () => {
      // When
      const result = getPeriod(null, new Date('2025-09-20T15:05:00Z'));

      // Then
      expect(result).toEqual('Avant le samedi 20 septembre');
    });
    test('should mention a period', async () => {
      // When
      const result1 = getPeriod(
        new Date('2025-09-20T15:05:00Z'),
        new Date('2025-09-21T15:05:00Z')
      );
      const result2 = getPeriod(
        new Date('2025-09-20T15:05:00Z'),
        new Date('2025-10-20T16:05:00Z')
      );
      const result3 = getPeriod(
        new Date('2025-09-20T15:05:00Z'),
        new Date('2026-01-20T16:05:00Z')
      );

      // Then
      expect(result1).toEqual('Du samedi 20 au dimanche 21 septembre 2025');
      expect(result2).toEqual('Du samedi 20 septembre au lundi 20 octobre 2025');
      expect(result3).toEqual('Du samedi 20 septembre 2025 au mardi 20 janvier 2026');
    });
  });
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
    describe('duration', () => {
      test('should return human readable duration, if start and end miletone dates are defined in the same day', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
          new Date(),
          null,
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
        const item3 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          new Date(),
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
        const item4 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T23:00:00Z'),
          new Date('2025-09-20T23:00:00Z'),
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
        const item5 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T20:00:00Z'),
          new Date('2025-09-20T22:00:00Z'), // not the same day for Europe/Paris timezone
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
        const item6 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T12:00:01Z'),
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
        const item7 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T12:01:00Z'),
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
        const item8 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T12:01:01Z'),
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
        const item9 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T13:00:00Z'),
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
        const item10 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T13:01:00Z'),
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
        const item11 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T13:01:01Z'),
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
        const item12 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T21:59:59Z'),
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
        const item13 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T12:04:03Z'),
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
        const item14 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date('2025-09-20T12:00:00Z'),
          new Date('2025-09-20T15:05:00Z'),
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

        // When
        const result1 = item1.duration;
        const result2 = item2.duration;
        const result3 = item3.duration;
        const result4 = item4.duration;
        const result5 = item5.duration;
        const result6 = item6.duration;
        const result7 = item7.duration;
        const result8 = item8.duration;
        const result9 = item9.duration;
        const result10 = item10.duration;
        const result11 = item11.duration;
        const result12 = item12.duration;
        const result13 = item13.duration;
        const result14 = item14.duration;

        // Then
        expect(result1).toEqual(undefined);
        expect(result2).toEqual(undefined);
        expect(result3).toEqual(undefined);
        expect(result4).toEqual(undefined);
        expect(result5).toEqual(undefined);
        expect(result6).toEqual('1 seconde');
        expect(result7).toEqual('1 minute');
        expect(result8).toEqual('1 minute et 1 seconde');
        expect(result9).toEqual('1 heure');
        expect(result10).toEqual('1 heure et 1 minute');
        expect(result11).toEqual('1 heure et 1 minute');
        expect(result12).toEqual('9 heures et 59 minutes');
        expect(result13).toEqual('4 minutes et 3 secondes');
        expect(result14).toEqual('3 heures et 5 minutes');
      });
    });
    describe('period', () => {
      test('should call getPeriod', async () => {
        // Given
        const spy = vi.spyOn(followupMethods, 'getPeriod').mockReturnValue('A Period');
        const item = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date(),
          new Date(),
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

        // When
        const result = item.period;

        // Then
        expect(result).toEqual('A Period');
        expect(spy).toHaveBeenCalledWith(
          item.milestone_start_date,
          item.milestone_end_date
        );
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
          null,
          null,
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
          null,
          null,
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
    describe('status_label', () => {
      test('should return custom label for item with milestone', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
        const item2 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date(),
          null,
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
        const status_label1 = item1.status_label;
        const status_label2 = item2.status_label;

        // Then
        expect(status_label1).equal('New');
        expect(status_label2).equal('Personnel');
      });
    });
    describe('icon', () => {
      test('should return custom icon for item with milestone', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
        const item2 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date(),
          null,
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
        const icon1 = item1.icon;
        const icon2 = item2.icon;

        // Then
        expect(icon1).equal('icon');
        expect(icon2).equal('fr-icon-user-fill');
      });
    });
    describe('formattedDate', () => {
      test('should return localized date and hour', async () => {
        // Given
        const item = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
        expect(date).equal('03 janvier 2026 - 09:05');
      });
    });
    describe('badgeClassName', () => {
      test('should return class name depending on status_id', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
          null,
          null,
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
          null,
          null,
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
          null,
          null,
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
      test('should return custom class name for item with milestone', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date(),
          null,
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
          new Date(),
          null,
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
          new Date(),
          null,
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
          new Date(),
          null,
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
        expect(className1).equal('am-badge--user');
        expect(className2).equal('am-badge--user');
        expect(className3).equal('am-badge--user');
        expect(className4).equal('am-badge--user');
      });
    });
    describe('hasMilestone', () => {
      test('should return true if has milesone start or end date', async () => {
        // Given
        const item1 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
          new Date(),
          null,
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
        const item3 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          new Date(),
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
        const item4 = new SubItem(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          new Date(),
          new Date(),
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

        // When
        const result1 = item1.hasMilestone();
        const result2 = item2.hasMilestone();
        const result3 = item3.hasMilestone();
        const result4 = item4.hasMilestone();

        // Then
        expect(result1).toEqual(false);
        expect(result2).toEqual(true);
        expect(result3).toEqual(true);
        expect(result4).toEqual(true);
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
          null,
          null,
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
    describe('getItemDetailPageUrl', () => {
      test('should return detail page url from partner_id, item_type and item_external_id', async () => {
        // Given
        const item = new Item(
          'partner',
          'type',
          'id',
          'ref',
          'notifications',
          null,
          null,
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
              new Date('2026-01-23T15:50:00Z'),
              null,
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
              new Date('2026-01-23T15:50:00Z'),
              null,
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
          null,
          null,
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
            new Date('2026-01-23T15:50:00Z'),
            null,
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
            null,
            null,
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
            new Date('2026-01-23T15:50:00Z'),
            null,
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
            null,
            null,
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
    describe('isEmpty', () => {
      test('should return true as followup has no items', async () => {
        // Given
        const followup = new Followup();

        // When
        const result = followup.isEmpty();

        // Then
        expect(result).toEqual(true);
      });
      test('should return false as followup has items', async () => {
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
        const result = followup.isEmpty();

        // Then
        expect(result).toEqual(false);
      });
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
          milestone_start_date: new Date('2026-01-24T15:50:00Z'),
          milestone_end_date: new Date('2026-01-25T15:50:00Z'),
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
              new Date('2026-01-23T15:50:00Z'),
              null,
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
              new Date('2026-01-24T15:50:00Z'),
              new Date('2026-01-25T15:50:00Z'),
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
                  new Date('2026-01-23T15:50:00Z'),
                  null,
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
            null,
            null,
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
            null,
            null,
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
