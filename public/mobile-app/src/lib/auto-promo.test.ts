import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Agenda } from '$lib/agenda';
import type { APIAgendaItem } from '$lib/api-agenda';
import { AutoPromo, AutoPromoItem } from '$lib/auto-promo';
import { userStore } from '$lib/state/User.svelte';
import { mockAddress, mockUserInfo } from '$tests/utils';

describe('/auto-promo.ts', () => {
  beforeEach(async () => {
    await userStore.login(mockUserInfo);
  });

  describe('AutoPromo', () => {
    test('user has no address (null) and no school holiday eligible for an otv', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      delete userStore.connected?.identity?.address;
      const agenda = new Agenda();
      vi.spyOn(agenda, 'holidayForOTV', 'get').mockReturnValue(null);

      // When
      const autoPromo = new AutoPromo(agenda);

      // Then
      expect(autoPromo.items.length).equal(1);
      expect(
        autoPromo.items[0].equals(
          new AutoPromoItem(
            'address',
            'Renseignez votre adresse',
            'Gagnez du temps en la renseignant une seule fois',
            '/#/edit-address',
            'house.svg'
          )
        )
      ).toBe(true);
    });

    test('user has no address (empty) and a school holiday eligible for an otv', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      const agenda = new Agenda();
      vi.spyOn(agenda, 'holidayForOTV', 'get').mockReturnValue({
        kind: 'holiday',
        title: 'Holiday',
        description: '',
        date: null,
        start_date: new Date('2026-02-06T23:00:00Z'),
        end_date: new Date('2026-02-22T23:00:00Z'),
        zones: ['Zone A'],
        emoji: 'foo',
      } as APIAgendaItem);

      // When
      const autoPromo = new AutoPromo(agenda);

      // Then
      expect(autoPromo.items.length).equal(2);
      expect(
        autoPromo.items[0].equals(
          new AutoPromoItem(
            'address',
            'Renseignez votre adresse',
            'Gagnez du temps en la renseignant une seule fois',
            '/#/edit-address',
            'house.svg'
          )
        )
      ).toBe(true);
      expect(
        autoPromo.items[1].equals(
          new AutoPromoItem(
            'otv',
            'Opération Tranquillité Vacances',
            'Protégez votre domicile pendant votre absence',
            '/#/procedure?date=2026-01-17',
            'house.svg'
          )
        )
      ).toBe(true);
    });

    test('user has address and no school holiday eligible for an otv', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      userStore.connected?.setAddress(mockAddress);
      const agenda = new Agenda();
      vi.spyOn(agenda, 'holidayForOTV', 'get').mockReturnValue(null);

      // When
      const autoPromo = new AutoPromo(agenda);

      // Then
      expect(autoPromo.items.length).equal(0);
    });

    test('user has address and a school holiday eligible for an otv', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      userStore.connected?.setAddress(mockAddress);
      const agenda = new Agenda();
      vi.spyOn(agenda, 'holidayForOTV', 'get').mockReturnValue({
        kind: 'holiday',
        title: 'Holiday',
        description: '',
        date: null,
        start_date: new Date('2026-02-06T23:00:00Z'),
        end_date: new Date('2026-02-22T23:00:00Z'),
        zones: ['Zone A'],
        emoji: 'foo',
      } as APIAgendaItem);

      // When
      const autoPromo = new AutoPromo(agenda);

      // Then
      expect(autoPromo.items.length).equal(1);
      expect(
        autoPromo.items[0].equals(
          new AutoPromoItem(
            'otv',
            'Opération Tranquillité Vacances',
            'Protégez votre domicile pendant votre absence',
            '/#/procedure?date=2026-01-17',
            'house.svg'
          )
        )
      ).toBe(true);
    });
  });
});
