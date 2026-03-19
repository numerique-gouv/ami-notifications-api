import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as inventoryMethods from '$lib/api-inventory';
import { buildFollowUp, FollowUp, RequestItem } from '$lib/follow-up';

describe('/follow-up.ts', () => {
  describe('RequestItem', () => {
    describe('is_past', () => {
      test('should return true', async () => {
        // Given
        const now = new Date();
        const past = new Date(now.getTime() - 60 * 1000);
        const item1 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          'closed',
          'Closed'
        );
        const item2 = new RequestItem(
          'title',
          'description',
          new Date(),
          past,
          'new',
          'New'
        );

        // When
        const is_past1 = item1.is_past();
        const is_past2 = item2.is_past();

        // Then
        expect(is_past1).equal(true);
        expect(is_past2).equal(true);
      });
      test('should return false', async () => {
        // Given
        const now = new Date();
        const future = new Date(now.getTime() + 60 * 1000);
        const item1 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          'new',
          'New'
        );
        const item2 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          'wip',
          'Wip'
        );
        const item3 = new RequestItem(
          'title',
          'description',
          new Date(),
          future,
          'new',
          'New'
        );
        const item4 = new RequestItem(
          'title',
          'description',
          new Date(),
          future,
          'wip',
          'Wip'
        );

        // When
        const is_past1 = item1.is_past();
        const is_past2 = item2.is_past();
        const is_past3 = item3.is_past();
        const is_past4 = item4.is_past();

        // Then
        expect(is_past1).equal(false);
        expect(is_past2).equal(false);
        expect(is_past3).equal(false);
        expect(is_past4).equal(false);
      });
    });
    describe('formattedDate', () => {
      test('should return localized date and hour, without year', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new RequestItem(
          'title',
          'description',
          new Date('2026-01-03T08:05:42Z'),
          null,
          'new',
          'New'
        );

        // When
        const date = item.formattedDate;

        // Then
        expect(date).equal('le 3 janvier à 09H05');
      });
    });
    describe('icon', () => {
      test('should return an icon depending on status_id', async () => {
        // Given
        const item1 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'Incorrect'
        );
        const item2 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          'new',
          'New'
        );
        const item3 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          'wip',
          'WIP'
        );
        const item4 = new RequestItem(
          'title',
          'description',
          new Date(),
          null,
          'closed',
          'Closed'
        );

        // When
        const icon1 = item1.icon;
        const icon2 = item2.icon;
        const icon3 = item3.icon;
        const icon4 = item4.icon;

        // Then
        expect(icon1).equal('');
        expect(icon2).equal('fr-icon-mail-fill');
        expect(icon3).equal('fr-icon-eye-fill');
        expect(icon4).equal('fr-icon-success-fill');
      });
    });
  });
  describe('FollowUp', () => {
    test('should organize items in current and past', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const now = new Date();
      const past = new Date(now.getTime() - 60 * 1000);
      const future = new Date(now.getTime() + 60 * 1000);
      const request1 = {
        external_id: 'OperationTranquilliteVacances:42',
        kind: 'otv',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: future,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        external_url: null,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
      };
      const request2 = {
        external_id: 'OperationTranquilliteVacances:43',
        kind: 'otv',
        status_id: 'wip',
        status_label: 'En cours',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en cours de traitement.',
        external_url: null,
        created_at: new Date('2026-02-22T15:50:00Z'),
        updated_at: new Date('2026-02-22T15:55:00Z'),
      };
      const request3 = {
        external_id: 'OperationTranquilliteVacances:44',
        kind: 'otv',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: new Date('2026-01-23T15:50:00Z'),
        milestone_end_date: past,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        external_url: null,
        created_at: new Date('2026-02-21T15:50:00Z'),
        updated_at: new Date('2026-02-21T15:55:00Z'),
      };
      const request4 = {
        external_id: 'OperationTranquilliteVacances:45',
        kind: 'otv',
        status_id: 'closed',
        status_label: 'Terminée',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est terminée.',
        external_url: null,
        created_at: new Date('2026-02-20T15:50:00Z'),
        updated_at: new Date('2026-02-20T15:55:00Z'),
      };

      // When
      const followUp = new FollowUp({
        psl: [request1, request2, request3, request4],
      });

      // Then
      expect(followUp.current.length).equal(2);
      expect(
        followUp.current[0].equals(
          new RequestItem(
            'Opération Tranquillité Vacances',
            'Votre demande est en brouillon.',
            new Date('2026-02-23T15:55:00.000Z'),
            future,
            'new',
            'Brouillon'
          )
        )
      ).toBe(true);
      expect(
        followUp.current[1].equals(
          new RequestItem(
            'Opération Tranquillité Vacances',
            'Votre demande est en cours de traitement.',
            new Date('2026-02-22T15:55:00.000Z'),
            null,
            'wip',
            'En cours'
          )
        )
      ).toBe(true);
      expect(followUp.past.length).equal(2);
      expect(
        followUp.past[0].equals(
          new RequestItem(
            'Opération Tranquillité Vacances',
            'Votre demande est en brouillon.',
            new Date('2026-02-21T15:55:00.000Z'),
            past,
            'new',
            'Brouillon'
          )
        )
      ).toBe(true);
      expect(
        followUp.past[1].equals(
          new RequestItem(
            'Opération Tranquillité Vacances',
            'Votre demande est terminée.',
            new Date('2026-02-20T15:55:00.000Z'),
            null,
            'closed',
            'Terminée'
          )
        )
      ).toBe(true);
    });
  });
  describe('buildFollowUp', () => {
    test('should retrieve inventories and init follow-up with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const request1 = {
        external_id: 'OperationTranquilliteVacances:42',
        kind: 'otv',
        status_id: 'new',
        status_label: 'Brouillon',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est en brouillon.',
        external_url: null,
        created_at: new Date('2026-02-23T15:50:00Z'),
        updated_at: new Date('2026-02-23T15:55:00Z'),
      };
      const request2 = {
        external_id: 'OperationTranquilliteVacances:43',
        kind: 'otv',
        status_id: 'closed',
        status_label: 'Terminée',
        milestone_start_date: null,
        milestone_end_date: null,
        title: 'Opération Tranquillité Vacances',
        description: 'Votre demande est terminée.',
        external_url: null,
        created_at: new Date('2026-02-22T15:50:00Z'),
        updated_at: new Date('2026-02-22T15:55:00Z'),
      };
      const spy = vi.spyOn(inventoryMethods, 'retrieveInventory').mockResolvedValue({
        psl: [request1, request2],
      });

      // When
      const followUp = await buildFollowUp();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(followUp).toBeInstanceOf(FollowUp);
      expect(followUp.current.length).equal(1);
      expect(
        followUp.current[0].equals(
          new RequestItem(
            'Opération Tranquillité Vacances',
            'Votre demande est en brouillon.',
            new Date('2026-02-23T15:55:00.000Z'),
            null,
            'new',
            'Brouillon'
          )
        )
      ).toBe(true);
      expect(followUp.past.length).equal(1);
      expect(
        followUp.past[0].equals(
          new RequestItem(
            'Opération Tranquillité Vacances',
            'Votre demande est terminée.',
            new Date('2026-02-22T15:55:00.000Z'),
            null,
            'closed',
            'Terminée'
          )
        )
      ).toBe(true);
    });
  });
});
