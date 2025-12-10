import { afterEach, describe, expect, test, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { Agenda, buildAgenda, Item } from '$lib/agenda'
import * as holidaysMethods from '$lib/api-holidays'
import { userStore } from '$lib/state/User.svelte'
import { mockUserIdentity, mockUserInfo } from '$tests/utils'

describe('/agenda.ts', () => {
  describe('Item', () => {
    describe('dayName', () => {
      test('should return short day name', async () => {
        // Given
        const item1 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-11-11'),
          null,
          null
        )
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-11-11'),
          null
        )

        // When
        const name1 = item1.dayName
        const name2 = item2.dayName

        // Then
        expect(name1).equal('mar')
        expect(name2).equal('mar')
      })
    })
    describe('dayNum', () => {
      test('should return short day num', async () => {
        // Given
        const item1 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-11-11'),
          null,
          null
        )
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-11-11'),
          null
        )

        // When
        const num1 = item1.dayNum
        const num2 = item2.dayNum

        // Then
        expect(num1).equal(11)
        expect(num2).equal(11)
      })
    })
    describe('monthName', () => {
      test('should return long month name', async () => {
        // Given
        const item1 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-11-11'),
          null,
          null
        )
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-11-11'),
          null
        )

        // When
        const name1 = item1.monthName
        const name2 = item2.monthName

        // Then
        expect(name1).equal('Novembre')
        expect(name2).equal('Novembre')
      })
    })
    describe('period', () => {
      test('should not mention start date year', async () => {
        // Given
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-10-15'),
          new Date('2025-11-15')
        )

        // When
        const period = item.period

        // Then
        expect(period).equal('Du 15 octobre au 15 novembre 2025')
      })
      test('should not mention start date year and month', async () => {
        // Given
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-10-15'),
          new Date('2025-10-20')
        )

        // When
        const period = item.period

        // Then
        expect(period).equal('Du 15 au 20 octobre 2025')
      })
      test('should mention start date year and month', async () => {
        // Given
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-12-20'),
          new Date('2026-01-02')
        )

        // When
        const period = item.period

        // Then
        expect(period).equal('Du 20 décembre 2025 au 2 janvier 2026')
      })
      test('should mention "À partir de"', async () => {
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-12-20'),
          null
        )

        // When
        const period = item.period

        // Then
        expect(period).equal('À partir du 20 décembre 2025')
      })
      test('should mention only the date', async () => {
        const item = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20'),
          null,
          null
        )

        // When
        const period = item.period

        // Then
        expect(period).equal('20 décembre 2025')
      })
    })
    describe('label', () => {
      test('should return a label depending on kind', async () => {
        // Given
        const item1 = new Item(
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          'description',
          new Date('2025-12-20')
        )
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20')
        )
        const item3 = new Item('otv', 'title', 'description', new Date('2025-12-20'))

        // When
        const label1 = item1.label
        const label2 = item2.label
        const label3 = item3.label

        // Then
        expect(label1).equal('')
        expect(label2).equal('Vacances et jours fériés')
        expect(label3).equal('Logement')
      })
    })
    describe('icon', () => {
      test('should return an icon depending on kind', async () => {
        // Given
        const item1 = new Item(
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          'description',
          new Date('2025-12-20')
        )
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20')
        )
        const item3 = new Item('otv', 'title', 'description', new Date('2025-12-20'))

        // When
        const icon1 = item1.icon
        const icon2 = item2.icon
        const icon3 = item3.icon

        // Then
        expect(icon1).equal('')
        expect(icon2).equal('fr-icon-calendar-event-fill')
        expect(icon3).equal('fr-icon-home-4-fill')
      })
    })
    describe('link', () => {
      test('should return a link depending on kind', async () => {
        // Given
        const item1 = new Item(
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          'description',
          new Date('2025-12-20')
        )
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20')
        )
        const item3 = new Item('otv', 'title', 'description', new Date('2025-12-20'))

        // When
        const link1 = item1.link
        const link2 = item2.link
        const link3 = item3.link

        // Then
        expect(link1).equal('')
        expect(link2).equal('/#/agenda')
        expect(link3).equal('/#/procedure')
      })
    })
  })
  describe('Agenda', () => {
    afterEach(() => {
      localStorage.clear()
      userStore.connected = null
    })
    test('should organize items in now and next', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris')
      const holiday1 = {
        description: 'Holiday 1',
        start_date: new Date('2025-09-20T23:00:00Z'),
        end_date: new Date('2025-12-15T23:00:00Z'),
        zones: 'Zone',
        emoji: 'foo',
      }
      const holiday2 = {
        description: 'Holiday 2',
        start_date: new Date('2025-10-20T23:00:00Z'),
        end_date: new Date('2025-11-15T23:00:00Z'),
        zones: 'Zone',
        emoji: '',
      }
      const holiday3 = {
        description: 'Holiday 3',
        start_date: new Date('2025-11-20T23:00:00Z'),
        end_date: new Date('2025-12-15T23:00:00Z'),
        zones: '',
        emoji: 'foo',
      }
      const holiday4 = {
        description: 'Holiday 4',
        start_date: new Date('2025-11-30T23:00:00Z'),
        end_date: new Date('2025-12-16T23:00:00Z'),
        zones: '',
        emoji: '',
      }
      const holiday5 = {
        description: 'Holiday 5',
        start_date: new Date('2025-12-20T23:00:00Z'),
        end_date: new Date('2025-12-24T23:00:00Z'),
        zones: '',
        emoji: '',
      }

      // When
      const agenda = new Agenda(
        [holiday1, holiday2, holiday3, holiday4, holiday5],
        new Date('2025-11-01T12:00:00Z')
      )

      // Then
      expect(agenda.now.length).equal(8)
      expect(
        agenda.now[0].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-08-30T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(
        agenda.now[1].equals(
          new Item(
            'holiday',
            'Holiday 1 Zone foo',
            null,
            null,
            holiday1.start_date,
            holiday1.end_date
          )
        )
      ).toBe(true)
      expect(
        agenda.now[2].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-09-29T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(
        agenda.now[3].equals(
          new Item(
            'holiday',
            'Holiday 2 Zone',
            null,
            null,
            holiday2.start_date,
            holiday2.end_date
          )
        )
      ).toBe(true)
      expect(
        agenda.now[4].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-10-30T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(
        agenda.now[5].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-11-09T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(
        agenda.now[6].equals(
          new Item(
            'holiday',
            'Holiday 3 foo',
            null,
            null,
            holiday3.start_date,
            holiday3.end_date
          )
        )
      ).toBe(true)
      expect(
        agenda.now[7].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-11-29T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(agenda.next.length).equal(2)
      expect(
        agenda.next[0].equals(
          new Item(
            'holiday',
            'Holiday 4',
            null,
            null,
            holiday4.start_date,
            holiday4.end_date
          )
        )
      ).toBe(true)
      expect(
        agenda.next[1].equals(
          new Item(
            'holiday',
            'Holiday 5',
            null,
            null,
            holiday5.start_date,
            holiday5.end_date
          )
        )
      ).toBe(true)
    })
    test('should not display past holidays or OTV related to past holidays', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris')
      const holiday1 = {
        description: 'Holiday',
        start_date: new Date('2026-02-06T23:00:00Z'),
        end_date: new Date('2026-02-22T23:00:00Z'),
        zones: 'Zone A',
        emoji: 'foo',
      }
      const holiday2 = {
        description: 'Holiday',
        start_date: new Date('2026-02-13T23:00:00Z'),
        end_date: new Date('2026-03-01T23:00:00Z'),
        zones: 'Zone B',
        emoji: 'foo',
      }

      // When
      const agenda = new Agenda([holiday1, holiday2], new Date('2026-02-24T12:00:00Z'))

      // Then
      expect(agenda.now.length).equal(1)
      expect(agenda.now[0].title).toEqual('Holiday Zone B foo')
    })
    test('should generate only one OTV per holiday', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris')
      const holiday1 = {
        description: 'Holiday',
        start_date: new Date('2026-02-06T23:00:00Z'),
        end_date: new Date('2026-02-22T23:00:00Z'),
        zones: 'Zone',
        emoji: 'foo',
      }
      const holiday2 = {
        description: 'Holiday',
        start_date: new Date('2026-02-13T23:00:00Z'),
        end_date: new Date('2026-03-01T23:00:00Z'),
        zones: 'Zone',
        emoji: 'foo',
      }

      // When
      const agenda = new Agenda([holiday1, holiday2], new Date('2026-02-01T12:00:00Z'))

      // Then
      expect(agenda.now.length).equal(3)
    })
    test('should mark holidays as custom if zones match user zone', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris')
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity))
      const holiday1 = {
        description: 'Holiday',
        start_date: new Date('2026-02-06T23:00:00Z'),
        end_date: new Date('2026-02-22T23:00:00Z'),
        zones: 'Zone A',
        emoji: 'foo',
      }
      const holiday2 = {
        description: 'Holiday',
        start_date: new Date('2026-02-13T23:00:00Z'),
        end_date: new Date('2026-03-01T23:00:00Z'),
        zones: 'Zone C',
        emoji: 'foo',
      }
      const holiday3 = {
        description: 'Summer Holiday',
        start_date: new Date('2026-07-01T23:00:00Z'),
        end_date: new Date('2026-08-31T23:00:00Z'),
        zones: '',
        emoji: 'bar',
      }

      // When
      await userStore.login(mockUserInfo)
      const agenda = new Agenda(
        [holiday1, holiday2, holiday3],
        new Date('2026-02-01T12:00:00Z')
      )

      // Then
      expect(agenda.now.length).equal(3)
      expect(agenda.now[0].custom).toEqual(false)
      expect(agenda.now[0].title).toEqual('Opération Tranquillité Vacances 🏠')
      expect(agenda.now[0].description).toEqual(
        'Inscrivez-vous pour protéger votre domicile pendant votre absence'
      )
      expect(agenda.now[1].custom).toEqual(false)
      expect(agenda.now[1].title).toEqual('Holiday Zone A foo')
      expect(agenda.now[1].description).toBeNull()
      expect(agenda.now[2].custom).toEqual(true)
      expect(agenda.now[2].title).toEqual('Holiday Zone C foo')
      expect(agenda.now[2].description).toEqual('Paris 🏠')
      expect(agenda.next.length).equal(2)
      expect(agenda.next[0].custom).toEqual(false)
      expect(agenda.next[0].title).toEqual('Opération Tranquillité Vacances 🏠')
      expect(agenda.next[0].description).toEqual(
        'Inscrivez-vous pour protéger votre domicile pendant votre absence'
      )
      expect(agenda.next[1].custom).toEqual(true)
      expect(agenda.next[1].title).toEqual('Summer Holiday bar')
      expect(agenda.next[1].description).toEqual('Paris 🏠')
    })
  })
  describe('buildAgenda', () => {
    test('should retrieve holidays and init agenda with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris')
      const holiday1 = {
        description: 'Holiday 1',
        start_date: new Date('2025-09-20T23:00:00Z'),
        end_date: new Date('2025-12-15T23:00:00Z'),
        zones: 'Zone',
        emoji: 'foo',
      }
      const holiday4 = {
        description: 'Holiday 4',
        start_date: new Date('2025-11-30T23:00:00Z'),
        end_date: new Date('2025-12-16T23:00:00Z'),
        zones: '',
        emoji: '',
      }
      const spy = vi
        .spyOn(holidaysMethods, 'retrieveHolidays')
        .mockResolvedValue([holiday1, holiday4])

      // When
      const agenda = await buildAgenda(new Date('2025-11-01T12:00:00Z'))

      // Then
      expect(spy).toHaveBeenCalledTimes(1)
      expect(agenda).toBeInstanceOf(Agenda)
      expect(agenda.now.length).equal(3)
      expect(
        agenda.now[0].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-08-30T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(
        agenda.now[1].equals(
          new Item(
            'holiday',
            'Holiday 1 Zone foo',
            null,
            null,
            holiday1.start_date,
            holiday1.end_date
          )
        )
      ).toBe(true)
      expect(
        agenda.now[2].equals(
          new Item(
            'otv',
            'Opération Tranquillité Vacances 🏠',
            'Inscrivez-vous pour protéger votre domicile pendant votre absence',
            null,
            new Date('2025-11-09T23:00:00Z'),
            null
          )
        )
      ).toBe(true)
      expect(agenda.next.length).equal(1)
      expect(
        agenda.next[0].equals(
          new Item(
            'holiday',
            'Holiday 4',
            null,
            null,
            holiday4.start_date,
            holiday4.end_date
          )
        )
      ).toBe(true)
    })
  })
})
