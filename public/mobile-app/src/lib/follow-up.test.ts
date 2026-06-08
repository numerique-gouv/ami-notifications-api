import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import * as inventoryMethods from '$lib/api-inventory';
import { buildFollowUp, FollowUp, RequestItem } from '$lib/follow-up';

describe('/follow-up.ts', () => {
  describe('RequestItem', () => {
    describe('formattedDate', () => {
      test('should return localized date and hour, without year', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const item = new RequestItem(
          'id',
          'title',
          'description',
          new Date('2026-01-03T08:05:42Z'),
          'new',
          'New',
          null
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
          'id1',
          'title',
          'description',
          new Date(),
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'Incorrect',
          null
        );
        const item2 = new RequestItem(
          'id2',
          'title',
          'description',
          new Date(),
          'new',
          'New',
          null
        );
        const item3 = new RequestItem(
          'id3',
          'title',
          'description',
          new Date(),
          'wip',
          'WIP',
          null
        );
        const item4 = new RequestItem(
          'id4',
          'title',
          'description',
          new Date(),
          'closed',
          'Closed',
          null
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
        expect(icon4).equal('fr-icon-flag-fill');
      });
    });
  });
  describe('buildFollowUp', () => {
    test('should retrieve inventories and init follow-up with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const request1 = {
        external_id: 'psl:OperationTranquilliteVacances:42',
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
        external_id: 'psl:OperationTranquilliteVacances:43',
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
        notifications: [request1, request2],
      });

      // When
      const followUp = await buildFollowUp();

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(followUp).toBeInstanceOf(FollowUp);
      expect(followUp.items.length).equal(2);
      expect(
        followUp.items[0].equals(
          new RequestItem(
            'psl:OperationTranquilliteVacances:42',
            'Opération Tranquillité Vacances',
            'Votre demande est en brouillon.',
            new Date('2026-02-23T15:55:00.000Z'),
            'new',
            'Brouillon',
            null
          )
        )
      ).toBe(true);
      expect(
        followUp.items[1].equals(
          new RequestItem(
            'psl:OperationTranquilliteVacances:43',
            'Opération Tranquillité Vacances',
            'Votre demande est terminée.',
            new Date('2026-02-22T15:55:00.000Z'),
            'closed',
            'Terminée',
            null
          )
        )
      ).toBe(true);
    });
  });
});
