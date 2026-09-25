import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Agenda, buildAgenda, Item, slugify } from '$lib/agenda';
import * as apiAgendaMethods from '$lib/api-agenda';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem, FollowupSubItem } from '$lib/followup';
import * as scheduledNotificationsMethods from '$lib/scheduled-notifications';
import { Preferences } from '$lib/state/preferences';
import { User, userStore } from '$lib/state/User.svelte';
import * as utilsMethods from '$lib/utils';
import { getTimestamp, parseISODate } from '$lib/utils';
import { mockUserIdentity, mockUserInfo } from '$tests/utils';

describe('/agenda.ts', () => {
  describe('Item', () => {
    describe('hide', () => {
      test('should hide item by adding it to localstorage', () => {
        // Given
        const item = new Item(
          'fake-id',
          'holiday',
          'Holiday 1',
          '',
          'Zone A',
          null,
          new Date('2025-09-20T23:00:00Z'),
          new Date('2025-12-15T23:00:00Z')
        );

        // When
        item.hide();

        // Then
        const result = JSON.parse(
          localStorage.getItem('hidden_agenda_items_holiday') || '[]'
        );
        expect(result.length).toBe(1);
        expect(result[0]).toBe('ami-holiday:1758409200:holiday-1');
      });
    });
    describe('isHidden', () => {
      let item1: Item;

      beforeEach(() => {
        const existing = [];
        item1 = new Item(
          'fake-id-holyday-1',
          'holiday',
          'Holiday 1',
          '',
          'Zone A',
          null,
          new Date('2025-09-20T23:00:00Z'),
          new Date('2025-12-15T23:00:00Z')
        );
        const itemKey = `ami-holiday:${getTimestamp(item1.date)}:${slugify(item1.title)}`;
        existing.push(itemKey);
        localStorage.setItem('hidden_agenda_items_holiday', JSON.stringify(existing));
      });

      test('should return true if item is in hidden items list', () => {
        // When
        const result = item1.isHidden();

        // Then
        expect(result).toBe(true);
      });

      test('should return false if item is not in hidden items list', () => {
        // Given
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'Holiday 2',
          '',
          'Corse',
          null,
          new Date('2025-11-30T23:00:00Z'),
          new Date('2025-12-16T23:00:00Z')
        );

        // When
        const result = item2.isHidden();

        // Then
        expect(result).toBe(false);
      });
    });
    describe('dayName', () => {
      test('should return short day name', async () => {
        // Given
        const item1 = new Item(
          'fake-id-holiday-1',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          null,
          new Date('2025-11-11'),
          null
        );

        // When
        const name1 = item1.dayName;
        const name2 = item2.dayName;

        // Then
        expect(name1).equal('Mar');
        expect(name2).equal('Mar');
      });
    });
    describe('fullDayName', () => {
      test('should return full day name', async () => {
        // Given
        const item1 = new Item(
          'fake-id-holiday-1',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          null,
          new Date('2025-11-11'),
          null
        );

        // When
        const name1 = item1.fullDayName;
        const name2 = item2.fullDayName;

        // Then
        expect(name1).equal('Mardi');
        expect(name2).equal('Mardi');
      });
    });
    describe('dayNum', () => {
      test('should return short day num', async () => {
        // Given
        const item1 = new Item(
          'fake-id-holiday-1',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          null,
          new Date('2025-11-11'),
          null
        );

        // When
        const num1 = item1.dayNum;
        const num2 = item2.dayNum;

        // Then
        expect(num1).equal(11);
        expect(num2).equal(11);
      });
    });
    describe('monthName', () => {
      test('should return long month name', async () => {
        // Given
        const item1 = new Item(
          'fake-id-holiday-1',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          null,
          new Date('2025-11-11'),
          null
        );

        // When
        const name1 = item1.monthName;
        const name2 = item2.monthName;

        // Then
        expect(name1).equal('Novembre');
        expect(name2).equal('Novembre');
      });
    });
    describe('endDate', () => {
      test('should return the max endDate of subitems', async () => {
        // Given
        const item1 = new Item(
          'fake-id-holiday-1',
          'holiday',
          'title',
          '',
          'description',
          null,
          null,
          null
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          null,
          null,
          new Date('2025-11-15')
        );
        const item3 = new Item(
          'fake-id-holiday-3',
          'holiday',
          'title',
          '',
          'description',
          null,
          null,
          new Date('2025-11-15')
        );
        item3.addSubItem('description', null, null, new Date('2025-11-14'));

        // When
        const endDate1 = item1.endDate;
        const endDate2 = item2.endDate;
        const endDate3 = item3.endDate;

        // Then
        expect(endDate1).equal(null);
        expect(endDate2?.getTime()).equal(new Date('2025-11-15').getTime());
        expect(endDate3?.getTime()).equal(new Date('2025-11-15').getTime());
      });
    });
    describe('period', () => {
      describe('personal item', () => {
        test('should call getPeriod', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-personal',
            'personal',
            'title',
            '',
            'description',
            null,
            new Date(),
            new Date()
          );

          // When
          const result = item.period;

          // Then
          expect(result).toEqual('A Period');
          expect(spy).toHaveBeenCalledWith(item.startDate, item.endDate);
        });
      });
      describe('non personal item', () => {
        test('should not mention start date year', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-holiday',
            'holiday',
            'title',
            '',
            'description',
            null,
            new Date('2025-10-15'),
            new Date('2025-11-15')
          );

          // When
          const period = item.period;

          // Then
          expect(period).equal('Du 15 octobre au 15 novembre 2025');
          expect(spy).not.toHaveBeenCalled();
        });
        test('should not mention start date year and month', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-holiday',
            'holiday',
            'title',
            '',
            'description',
            null,
            new Date('2025-10-15'),
            new Date('2025-10-20')
          );

          // When
          const period = item.period;

          // Then
          expect(period).equal('Du 15 au 20 octobre 2025');
          expect(spy).not.toHaveBeenCalled();
        });
        test('should mention start date year and month', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-holiday',
            'holiday',
            'title',
            '',
            'description',
            null,
            new Date('2025-12-20'),
            new Date('2026-01-02')
          );

          // When
          const period = item.period;

          // Then
          expect(period).equal('Du 20 décembre 2025 au 2 janvier 2026');
          expect(spy).not.toHaveBeenCalled();
        });
        test('should mention only start date and not "Du .. au .."', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-holiday',
            'holiday',
            'title',
            '',
            'description',
            null,
            new Date('2027-05-07'),
            new Date('2027-05-07')
          );

          // When
          const period = item.period;

          // Then
          expect(period).equal('7 mai 2027');
          expect(spy).not.toHaveBeenCalled();
        });
        test('should mention "À partir de"', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-holiday',
            'holiday',
            'title',
            '',
            'description',
            null,
            new Date('2025-12-20'),
            null
          );

          // When
          const period = item.period;

          // Then
          expect(period).equal('À partir du 20 décembre 2025');
          expect(spy).not.toHaveBeenCalled();
        });
        test('should mention only the date', async () => {
          // Given
          const spy = vi
            .spyOn(followupMethods, 'getPeriod')
            .mockReturnValue('A Period');
          const item = new Item(
            'fake-id-holiday',
            'holiday',
            'title',
            '',
            'description',
            new Date('2025-12-20'),
            null,
            null
          );

          // When
          const period = item.period;

          // Then
          expect(period).equal('20 décembre 2025');
          expect(spy).not.toHaveBeenCalled();
        });
      });
    });
    describe('label', () => {
      test('should return a label depending on kind', async () => {
        // Given
        const item1 = new Item(
          'fake-id-item-1',
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item(
          'fake-id-election-3',
          'election',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item4 = new Item(
          'fake-id-personal-4',
          'personal',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );

        // When
        const label1 = item1.label;
        const label2 = item2.label;
        const label3 = item3.label;
        const label4 = item4.label;

        // Then
        expect(label1).equal('');
        expect(label2).equal('Vacances et jours fériés');
        expect(label3).equal('Élections');
        expect(label4).equal('Personnel');
      });
    });
    describe('icon', () => {
      test('should return an icon depending on kind', async () => {
        // Given
        const item1 = new Item(
          'fake-id-item-1',
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item(
          'fake-id-election-3',
          'election',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item4 = new Item(
          'fake-id-personal-4',
          'personal',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );

        // When
        const icon1 = item1.icon;
        const icon2 = item2.icon;
        const icon3 = item3.icon;
        const icon4 = item4.icon;

        // Then
        expect(icon1).equal('');
        expect(icon2).equal('fr-icon-calendar-event-fill');
        expect(icon3).equal('fr-icon-chat-check-fill');
        expect(icon4).equal('fr-icon-user-fill');
      });
    });
    describe('key', () => {
      test('should return a key depending on kind, date and title', async () => {
        // Given
        const item1 = new Item(
          'fake-id-item-1',
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title 1',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title 2',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item(
          'fake-id-election-3',
          'election',
          'title 3',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item4 = new Item(
          'fake-id-personal-4',
          'personal',
          'title 4',
          '',
          'description',
          new Date('2025-12-20')
        );

        // When
        const key1 = item1.key;
        const key2 = item2.key;
        const key3 = item3.key;
        const key4 = item4.key;

        // Then
        expect(key1).equal('ami-incorrect:1766188800:title-1');
        expect(key2).equal('ami-holiday:1766188800:title-2');
        expect(key3).equal('ami-election:1766188800:title-3');
        expect(key4).equal('ami-personal:1766188800:title-4');
      });
    });
    describe('badgeClassName', () => {
      test('should return an badgeClassName depending on kind', async () => {
        // Given
        const item1 = new Item(
          'fake-id-item-1',
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'fake-id-holiday-2',
          'holiday',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item(
          'fake-id-election-3',
          'election',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );
        const item4 = new Item(
          'fake-id-personal-4',
          'personal',
          'title',
          '',
          'description',
          new Date('2025-12-20')
        );

        // When
        const badgeClassName1 = item1.badgeClassName;
        const badgeClassName2 = item2.badgeClassName;
        const badgeClassName3 = item3.badgeClassName;
        const badgeClassName4 = item4.badgeClassName;

        // Then
        expect(badgeClassName1).equal('');
        expect(badgeClassName2).equal('fr-badge--blue-cumulus');
        expect(badgeClassName3).equal('fr-badge--green-tilleul-verveine');
        expect(badgeClassName4).equal('am-badge--user');
      });
    });
  });
  describe('Agenda', () => {
    describe('Now/Next', () => {
      beforeEach(() => {
        vi.spyOn(
          scheduledNotificationsMethods,
          'createScheduledNotification'
        ).mockResolvedValue(true);
      });
      test('should organize items in now and next', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday 1',
          description: '',
          date: null,
          start_date: parseISODate('2025-09-21'),
          end_date: parseISODate('2025-12-16'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday 2',
          description: '',
          date: null,
          start_date: parseISODate('2025-10-21'),
          end_date: parseISODate('2025-11-16'),
          zones: ['Zone B'],
          emoji: '',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Holiday 3',
          description: '',
          date: null,
          start_date: parseISODate('2025-11-21'),
          end_date: parseISODate('2025-12-16'),
          zones: ['Corse'],
          emoji: 'foo',
        };
        const holiday4 = {
          kind: 'holiday',
          title: 'Holiday 4',
          description: '',
          date: null,
          start_date: parseISODate('2025-12-01'),
          end_date: parseISODate('2025-12-17'),
          zones: ['Zone A'],
          emoji: '',
        };
        const holiday5 = {
          kind: 'holiday',
          title: 'Holiday 5',
          description: '',
          date: null,
          start_date: parseISODate('2025-12-21'),
          end_date: parseISODate('2025-12-25'),
          zones: ['Zone C'],
          emoji: '',
        };
        const holiday6 = {
          kind: 'holiday',
          title: 'Day 6',
          description: '',
          date: parseISODate('2025-11-12'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const holiday7 = {
          kind: 'holiday',
          title: 'Day 7',
          description: '',
          date: parseISODate('2025-12-11'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        const election1 = {
          kind: 'election',
          title: 'Election1',
          description: 'description',
          date: parseISODate('2025-11-12'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const election2 = {
          kind: 'election',
          title: 'Election2',
          description: 'description',
          date: parseISODate('2025-12-11'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3, holiday4, holiday5],
            public_holidays: [holiday6, holiday7],
            elections: [election1, election2],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(5);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday 1 foo',
              '',
              'Zone A',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.now[1].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday 2',
              '',
              'Zone B',
              null,
              holiday2.start_date,
              holiday2.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.now[2].equals(
            new Item(
              'fake-id',
              'holiday',
              'Day 6 bar',
              '',
              null,
              holiday6.date,
              null,
              null
            )
          )
        ).toBe(true);
        expect(
          agenda.now[3].equals(
            new Item(
              'fake-id',
              'election',
              'Election1 bar',
              '',
              'description',
              election1.date,
              null,
              null
            )
          )
        ).toBe(true);
        expect(
          agenda.now[4].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday 3 foo',
              '',
              'Corse',
              null,
              holiday3.start_date,
              holiday3.end_date
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(4);
        expect(
          agenda.next[0].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday 4',
              '',
              'Zone A',
              null,
              holiday4.start_date,
              holiday4.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.next[1].equals(
            new Item('fake-id', 'holiday', 'Day 7', '', null, holiday7.date, null, null)
          )
        ).toBe(true);
        expect(
          agenda.next[2].equals(
            new Item(
              'fake-id',
              'election',
              'Election2',
              '',
              'description',
              election2.date,
              null,
              null
            )
          )
        ).toBe(true);
        const item = new Item(
          'fake-id',
          'holiday',
          'Holiday 5',
          '',
          'Zone C&nbsp;: <strong>Paris (75) 🏠</strong>',
          null,
          holiday5.start_date,
          holiday5.end_date
        );
        item.subitems[0].isPersonal = true;
        expect(agenda.next[3].equals(item)).toBe(true);
      });
    });
    describe('Zones', () => {
      test('should ignore some zones', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2026-02-07'),
          end_date: parseISODate('2026-02-23'),
          zones: ['Zone A', 'Zone foo'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2026-02-14'),
          end_date: parseISODate('2026-03-02'),
          zones: ['Zone foo'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);
        const spyIsConcerned = vi
          .spyOn(Preferences.prototype, 'isSchoolHolidayConcerned')
          .mockReturnValueOnce(true)
          .mockReturnValueOnce(false);
        const spyGetDescription = vi
          .spyOn(Preferences.prototype, 'getSchoolHolidayDescription')
          .mockReturnValueOnce('desc 1');
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2],
            public_holidays: [],
            elections: [],
          },
          null,
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday foo',
              '',
              'desc 1',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(0);
        expect(spyIsConcerned).toHaveBeenCalledTimes(2);
        expect(spyIsConcerned).toHaveBeenCalledWith(holiday1);
        expect(spyIsConcerned).toHaveBeenCalledWith(holiday2);
        expect(spyGetDescription).toHaveBeenCalledTimes(1);
        expect(spyGetDescription).toHaveBeenCalledWith(
          holiday1,
          userStore.connected?.identity.address
        );

        // Cleanup
        spyIsConcerned.mockRestore();
        spyGetDescription.mockRestore();
      });
    });
    describe('Multitiles', () => {
      test('should stack holidays with the same title - but only for the same year', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2026-02-07'),
          end_date: parseISODate('2026-02-23'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2026-02-14'),
          end_date: parseISODate('2026-03-02'),
          zones: ['Zone B'],
          emoji: 'foo',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2027-02-07'),
          end_date: parseISODate('2027-02-23'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday4 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2027-02-14'),
          end_date: parseISODate('2027-03-02'),
          zones: ['Zone B'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3, holiday4],
            public_holidays: [],
            elections: [],
          },
          null,
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        const item1 = new Item(
          'fake-id',
          'holiday',
          'Holiday foo',
          '',
          'Zone A',
          null,
          holiday1.start_date,
          holiday1.end_date
        );
        item1.addSubItem('Zone B', null, holiday2.start_date, holiday2.end_date);
        expect(agenda.now[0].equals(item1)).toBe(true);
        expect(agenda.now[0].subitems[0].period).toEqual('Du 7 au 23 février 2026');
        expect(agenda.now[0].subitems[1].period).toEqual(
          'Du 14 février au 2 mars 2026'
        );
        expect(agenda.next.length).equal(1);
        const item2 = new Item(
          'fake-id',
          'holiday',
          'Holiday foo',
          '',
          'Zone A',
          null,
          holiday3.start_date,
          holiday3.end_date
        );
        item2.addSubItem('Zone B', null, holiday4.start_date, holiday4.end_date);
        expect(agenda.next[0].equals(item2)).toBe(true);
        expect(agenda.next[0].subitems[0].period).toEqual('Du 7 au 23 février 2027');
        expect(agenda.next[0].subitems[1].period).toEqual(
          'Du 14 février au 2 mars 2027'
        );
      });
      test('should mark user tile as personal', async () => {
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2026-02-07'),
          end_date: parseISODate('2026-02-23'),
          zones: ['Zone C'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2026-02-14'),
          end_date: parseISODate('2026-03-02'),
          zones: ['Zone B'],
          emoji: 'foo',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2027-02-07'),
          end_date: parseISODate('2027-02-23'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday4 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: parseISODate('2027-02-14'),
          end_date: parseISODate('2027-03-02'),
          zones: ['Zone C'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3, holiday4],
            public_holidays: [],
            elections: [],
          },
          null,
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        const item1 = new Item(
          'fake-id',
          'holiday',
          'Holiday foo',
          '',
          'Zone C&nbsp;: <strong>Paris (75) 🏠</strong>',
          null,
          holiday1.start_date,
          holiday1.end_date
        );
        item1.addSubItem('Zone B', null, holiday2.start_date, holiday2.end_date);
        item1.subitems[0].isPersonal = true;
        expect(agenda.now[0].equals(item1)).toBe(true);
        expect(agenda.now[0].subitems[0].period).toEqual('Du 7 au 23 février 2026');
        expect(agenda.now[0].subitems[1].period).toEqual(
          'Du 14 février au 2 mars 2026'
        );
        expect(agenda.next.length).equal(1);
        const item2 = new Item(
          'fake-id',
          'holiday',
          'Holiday foo',
          '',
          'Zone A',
          null,
          holiday3.start_date,
          holiday3.end_date
        );
        item2.addSubItem(
          'Zone C&nbsp;: <strong>Paris (75) 🏠</strong>',
          null,
          holiday4.start_date,
          holiday4.end_date
        );
        item2.subitems[1].isPersonal = true;
        expect(agenda.next[0].equals(item2)).toBe(true);
        expect(agenda.next[0].subitems[0].period).toEqual('Du 7 au 23 février 2027');
        expect(agenda.next[0].subitems[1].period).toEqual(
          'Du 14 février au 2 mars 2027'
        );
      });
    });
    describe('School holiday', () => {
      test('should organize items in now and next', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday 1',
          description: '',
          date: null,
          start_date: parseISODate('2025-09-21'),
          end_date: parseISODate('2025-12-16'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday 2',
          description: '',
          date: null,
          start_date: parseISODate('2025-10-21'),
          end_date: parseISODate('2025-11-16'),
          zones: ['Zone B'],
          emoji: '',
        };
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2],
            public_holidays: [],
            elections: [],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(2);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday 1 foo',
              '',
              'Zone A',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.now[1].equals(
            new Item(
              'fake-id',
              'holiday',
              'Holiday 2',
              '',
              'Zone B',
              null,
              holiday2.start_date,
              holiday2.end_date
            )
          )
        ).toBe(true);
      });
      test('should not display school holiday if is listed in hidden items', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday 1',
          description: '',
          date: null,
          start_date: parseISODate('2025-09-21'),
          end_date: parseISODate('2025-12-16'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday 2',
          description: '',
          date: null,
          start_date: parseISODate('2025-10-21'),
          end_date: parseISODate('2025-11-16'),
          zones: ['Zone B'],
          emoji: '',
        };
        await userStore.login(mockUserInfo);

        const existing = [];
        const itemKey = `ami-holiday:${getTimestamp(holiday2.start_date)}:${slugify(holiday2.title)}`;
        existing.push(itemKey);
        localStorage.setItem('hidden_agenda_items_holiday', JSON.stringify(existing));
        vi.spyOn(utilsMethods, 'uniqueId')
          .mockReturnValueOnce('fake-id-1')
          .mockReturnValueOnce('fake-id-2');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2],
            public_holidays: [],
            elections: [],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id-1',
              'holiday',
              'Holiday 1 foo',
              '',
              'Zone A',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
      });
    });
    describe('Public holiday', () => {
      test('should organize items in now and next', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday6 = {
          kind: 'holiday',
          title: 'Day 6',
          description: '',
          date: parseISODate('2025-11-12'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const holiday7 = {
          kind: 'holiday',
          title: 'Day 7',
          description: '',
          date: parseISODate('2025-12-11'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [],
            public_holidays: [holiday6, holiday7],
            elections: [],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'holiday',
              'Day 6 bar',
              '',
              null,
              holiday6.date,
              null,
              null
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(1);
        expect(
          agenda.next[0].equals(
            new Item('fake-id', 'holiday', 'Day 7', '', null, holiday7.date, null, null)
          )
        ).toBe(true);
      });
      test('should not display public holiday if is listed in hidden items', async () => {
        // Given
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday6 = {
          kind: 'holiday',
          title: 'Day 6',
          description: '',
          date: parseISODate('2025-11-12'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const holiday7 = {
          kind: 'holiday',
          title: 'Day 7',
          description: '',
          date: parseISODate('2025-12-11'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        const itemHoliday6 = new Item(
          'fake-id-6',
          'holiday',
          'Day 6 bar',
          '',
          null,
          new Date('2025-11-11T23:00:00Z'),
          null,
          null
        );
        const itemHoliday7 = new Item(
          'fake-id-7',
          'holiday',
          'Day 7',
          '',
          null,
          new Date('2025-12-10T23:00:00Z'),
          null,
          null
        );
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId')
          .mockReturnValueOnce('fake-id-6')
          .mockReturnValueOnce('fake-id-7');

        const existing = [];
        const itemKey = `ami-holiday:${getTimestamp(itemHoliday6.date)}:${slugify(itemHoliday6.title)}`;
        existing.push(itemKey);
        localStorage.setItem('hidden_agenda_items_holiday', JSON.stringify(existing));

        // When
        const agenda = new Agenda(
          {
            school_holidays: [],
            public_holidays: [holiday6, holiday7],
            elections: [],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(0);
        expect(agenda.next.length).equal(1);
        expect(agenda.next[0].equals(itemHoliday7)).toBe(true);
      });
    });
    describe('Scheduled notifications', () => {
      describe('User has no address', () => {
        test('should not create scheduled notifications for otv', async () => {
          // Given
          const spy = vi
            .spyOn(User.prototype, 'createScheduledNotification')
            .mockResolvedValue();
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-02-01T12:00:00Z')
          );

          // Then
          expect(agenda.now.length).equal(1);
          expect(agenda.next.length).equal(1);
          expect(spy).toHaveBeenCalledTimes(0);
        });
      });
      describe('User has an address', () => {
        test('should create scheduled notifications for otv as user has address - holidays are displayed', async () => {
          // Given
          const spy = vi
            .spyOn(User.prototype, 'createScheduledNotification')
            .mockResolvedValue();
          localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'],
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'], // matches user's zone
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-02-01T12:00:00Z')
          );

          // Then
          expect(agenda.now.length).equal(1);
          expect(agenda.next.length).equal(1);
          expect(spy).toHaveBeenCalledTimes(2);
          expect(spy).toHaveBeenNthCalledWith(1, {
            content_body:
              'Demandez l’Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.',
            content_icon: 'fr-icon-megaphone-line',
            content_title: 'Et si on veillait sur votre logement ? 👮',
            reference: 'ami-otv:d-3w:2026:holiday',
            internal_url: '/#/procedure?date=2026-01-24',
            scheduled_at: new Date('2026-01-23T23:00:00Z'),
          });
          expect(spy).toHaveBeenNthCalledWith(2, {
            content_body:
              'Demandez l’Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.',
            content_icon: 'fr-icon-megaphone-line',
            content_title: 'Et si on veillait sur votre logement ? 👮',
            reference: 'ami-otv:d-3w:2026:summer-holiday',
            internal_url: '/#/procedure?date=2026-06-11',
            scheduled_at: new Date('2026-06-10T22:00:00Z'),
          });
        });
        test('should create scheduled notifications for otv as user has address - holidays are not displayed but otv have to be sent', async () => {
          // Given
          const spy = vi
            .spyOn(User.prototype, 'createScheduledNotification')
            .mockResolvedValue();
          const preferences = new Preferences(['Réunion'], []); // preferences are not matching holidays
          const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
          newMockUserIdentity.preferences = preferences;
          localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'],
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'], // matches user's zone
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-02-01T12:00:00Z')
          );

          // Then
          expect(agenda.now.length).equal(0);
          expect(agenda.next.length).equal(0);
          expect(spy).toHaveBeenCalledTimes(2);
          expect(spy).toHaveBeenNthCalledWith(1, {
            content_body:
              'Demandez l’Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.',
            content_icon: 'fr-icon-megaphone-line',
            content_title: 'Et si on veillait sur votre logement ? 👮',
            reference: 'ami-otv:d-3w:2026:holiday',
            internal_url: '/#/procedure?date=2026-01-24',
            scheduled_at: new Date('2026-01-23T23:00:00Z'),
          });
          expect(spy).toHaveBeenNthCalledWith(2, {
            content_body:
              'Demandez l’Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.',
            content_icon: 'fr-icon-megaphone-line',
            content_title: 'Et si on veillait sur votre logement ? 👮',
            reference: 'ami-otv:d-3w:2026:summer-holiday',
            internal_url: '/#/procedure?date=2026-06-11',
            scheduled_at: new Date('2026-06-10T22:00:00Z'),
          });
        });
      });
    });
    describe('School holiday for otv', () => {
      beforeEach(() => {
        vi.spyOn(
          scheduledNotificationsMethods,
          'createScheduledNotification'
        ).mockResolvedValue(true);
      });
      describe('User has no address', () => {
        test('should be defined to first school holiday matching user zone', async () => {
          // Given
          const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C'], []);
          const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
          newMockUserIdentity.preferences = preferences;
          newMockUserIdentity.address = undefined;
          localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-01-17T12:00:00Z')
          );

          // Then
          expect(agenda.holidayForOTV).equal(holiday1);
        });
        test('should be null as there is no holiday displayed', async () => {
          // Given
          const preferences = new Preferences(['Réunion'], []);
          const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
          newMockUserIdentity.preferences = preferences;
          newMockUserIdentity.address = undefined;
          localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-01-17T12:00:00Z')
          );

          // Then
          expect(agenda.holidayForOTV).equal(null);
        });
        test('should be null as first school holiday is in more than 3 weeks', async () => {
          // Given
          const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C'], []);
          const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
          newMockUserIdentity.preferences = preferences;
          newMockUserIdentity.address = undefined;
          localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-01-16T12:00:00Z')
          );

          // Then
          expect(agenda.holidayForOTV).equal(null);
        });
      });
      describe('User has an address', () => {
        test('should be defined to first school holiday matching user zone', async () => {
          // Given
          localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-01-17T12:00:00Z')
          );

          // Then
          expect(agenda.holidayForOTV).equal(holiday1);
        });
        test('should be null as there is no holiday displayed', async () => {
          // Given
          const preferences = new Preferences(['Réunion'], []);
          const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
          newMockUserIdentity.preferences = preferences;
          localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-01-17T12:00:00Z')
          );

          // Then
          expect(agenda.holidayForOTV).equal(null);
        });
        test('should be null as first school holiday is in more than 3 weeks', async () => {
          // Given
          localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
          const holiday1 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-07'),
            end_date: parseISODate('2026-02-23'),
            zones: ['Zone A'], // first date
            emoji: 'foo',
          };
          const holiday2 = {
            kind: 'holiday',
            title: 'Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-02-14'),
            end_date: parseISODate('2026-03-02'),
            zones: ['Zone C'],
            emoji: 'foo',
          };
          const holiday3 = {
            kind: 'holiday',
            title: 'Summer Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2026-07-02'),
            end_date: parseISODate('2026-09-01'),
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          const holiday4 = {
            kind: 'holiday',
            title: 'Past Holiday',
            description: '',
            date: null,
            start_date: parseISODate('2025-07-02'),
            end_date: parseISODate('2025-09-01'), // past holiday
            zones: ['Zone A', 'Zone B', 'Zone C'],
            emoji: 'bar',
          };
          await userStore.login(mockUserInfo);

          // When
          const agenda = new Agenda(
            {
              school_holidays: [holiday1, holiday2, holiday3, holiday4],
              public_holidays: [],
              elections: [],
            },
            null,
            new Date('2026-01-16T12:00:00Z')
          );

          // Then
          expect(agenda.holidayForOTV).equal(null);
        });
      });
    });
    describe('Election', () => {
      test('should organize items in now and next', async () => {
        // Given
        const election1 = {
          kind: 'election',
          title: 'Election1',
          description: 'description',
          date: parseISODate('2025-11-12'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const election2 = {
          kind: 'election',
          title: 'Election2',
          description: 'description',
          date: parseISODate('2025-12-11'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(
          {
            school_holidays: [],
            public_holidays: [],
            elections: [election1, election2],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'election',
              'Election1 bar',
              '',
              'description',
              election1.date,
              null,
              null
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(1);
        expect(
          agenda.next[0].equals(
            new Item(
              'fake-id',
              'election',
              'Election2',
              '',
              'description',
              election2.date,
              null,
              null
            )
          )
        ).toBe(true);
      });
      test('should not display election if is listed in hidden items', async () => {
        // Given
        const election1 = {
          kind: 'election',
          title: 'Election1',
          description: 'description',
          date: parseISODate('2025-11-12'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const election2 = {
          kind: 'election',
          title: 'Election2',
          description: 'description',
          date: parseISODate('2025-12-11'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        const itemElection1 = new Item(
          'fake-id-1',
          'election',
          'Election1 bar',
          '',
          'description',
          parseISODate('2025-11-12'),
          null,
          null
        );
        const itemElection2 = new Item(
          'fake-id-2',
          'election',
          'Election2',
          '',
          'description',
          parseISODate('2025-12-11'),
          null,
          null
        );
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId')
          .mockReturnValueOnce('fake-id-1')
          .mockReturnValueOnce('fake-id-2');

        const existing = [];
        const itemKey = `ami-election:${getTimestamp(itemElection2.date)}:${slugify(itemElection2.title)}`;
        existing.push(itemKey);
        localStorage.setItem('hidden_agenda_items_election', JSON.stringify(existing));

        // When
        const agenda = new Agenda(
          {
            school_holidays: [],
            public_holidays: [],
            elections: [election1, election2],
          },
          null,
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(agenda.now[0].equals(itemElection1)).toBe(true);
        expect(agenda.next.length).equal(0);
      });
    });
    describe('Personal', () => {
      test('should organize items in now and next', async () => {
        // Given
        const followup = new Followup();
        const followupItem1 = new FollowupItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
        );
        const followupItem2 = new FollowupItem(
          'partner',
          'type',
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
          true,
          null,
          []
        );
        const followupItem3 = new FollowupItem(
          'partner',
          'type',
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
          true,
          null,
          []
        );
        const followupItem4 = new FollowupItem(
          'partner',
          'type',
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
          true,
          null,
          []
        );
        const followupItem5 = new FollowupItem(
          'partner',
          'type',
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
          true,
          null,
          []
        );
        const followupItem6 = new FollowupItem(
          'partner',
          'type',
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
          true,
          null,
          []
        );
        vi.spyOn(followup, 'items', 'get').mockReturnValue([
          followupItem1,
          followupItem2,
          followupItem3,
          followupItem4,
          followupItem5,
          followupItem6,
        ]);
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
        vi.spyOn(followupItem1, 'buildAgendaItem').mockReturnValue(null);
        vi.spyOn(followupItem2, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link1',
            null,
            null,
            parseISODate('2025-10-31'), // start date is past but it is displayed anyway
            null
          )
        );
        vi.spyOn(followupItem3, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link2',
            null,
            null,
            null,
            parseISODate('2025-12-23')
          )
        );
        vi.spyOn(followupItem4, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link3',
            null,
            null,
            null,
            parseISODate('2025-10-31') // end date is past
          )
        );
        vi.spyOn(followupItem5, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link4',
            null,
            null,
            parseISODate('2025-11-01'),
            null
          )
        );
        vi.spyOn(followupItem6, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link5',
            null,
            null,
            // item is past
            parseISODate('2025-10-30'),
            parseISODate('2025-10-31')
          )
        );
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(null, followup, new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(agenda.now.length).equal(2);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'personal',
              'Rendez-vous',
              'link1',
              null,
              null,
              parseISODate('2025-10-31'),
              null
            )
          )
        ).toBe(true);
        expect(
          agenda.now[1].equals(
            new Item(
              'fake-id',
              'personal',
              'Rendez-vous',
              'link4',
              null,
              null,
              parseISODate('2025-11-01'),
              null
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(1);
        expect(
          agenda.next[0].equals(
            new Item(
              'fake-id',
              'personal',
              'Rendez-vous',
              'link2',
              null,
              null,
              null,
              parseISODate('2025-12-23')
            )
          )
        ).toBe(true);
      });
      test('should organize subitems in now and next', async () => {
        // Given
        const followup = new Followup();
        const followupSubItem1 = new FollowupSubItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
          null
        );
        const followupSubItem2 = new FollowupSubItem(
          'partner',
          'type',
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
          true,
          null
        );
        const followupSubItem3 = new FollowupSubItem(
          'partner',
          'type',
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
          true,
          null
        );
        const followupSubItem4 = new FollowupSubItem(
          'partner',
          'type',
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
          true,
          null
        );
        const followupSubItem5 = new FollowupSubItem(
          'partner',
          'type',
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
          true,
          null
        );
        const followupSubItem6 = new FollowupSubItem(
          'partner',
          'type',
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
          true,
          null
        );
        const followupItem = new FollowupItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
        );
        vi.spyOn(followupItem, 'futureSubItemWithMilestone', 'get').mockReturnValue([
          followupSubItem1,
          followupSubItem2,
          followupSubItem3,
          followupSubItem4,
          followupSubItem5,
          followupSubItem6,
        ]);
        vi.spyOn(followup, 'items', 'get').mockReturnValue([followupItem]);
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
        vi.spyOn(followupSubItem1, 'buildAgendaItem').mockReturnValue(null);
        vi.spyOn(followupSubItem2, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link1',
            null,
            null,
            parseISODate('2025-10-31'), // start date is past but it is displayed anyway
            null
          )
        );
        vi.spyOn(followupSubItem3, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link2',
            null,
            null,
            null,
            parseISODate('2025-12-23')
          )
        );
        vi.spyOn(followupSubItem4, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link3',
            null,
            null,
            null,
            parseISODate('2025-10-31') // end date is past
          )
        );
        vi.spyOn(followupSubItem5, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link4',
            null,
            null,
            parseISODate('2025-11-01'),
            null
          )
        );
        vi.spyOn(followupSubItem6, 'buildAgendaItem').mockReturnValue(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link5',
            null,
            null,
            // item is past
            parseISODate('2025-10-30'),
            parseISODate('2025-10-31')
          )
        );
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId').mockReturnValue('fake-id');

        // When
        const agenda = new Agenda(null, followup, new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(agenda.now.length).equal(2);
        expect(
          agenda.now[0].equals(
            new Item(
              'fake-id',
              'personal',
              'Rendez-vous',
              'link1',
              null,
              null,
              parseISODate('2025-10-31'),
              null
            )
          )
        ).toBe(true);
        expect(
          agenda.now[1].equals(
            new Item(
              'fake-id',
              'personal',
              'Rendez-vous',
              'link4',
              null,
              null,
              parseISODate('2025-11-01'),
              null
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(1);
        expect(
          agenda.next[0].equals(
            new Item(
              'fake-id',
              'personal',
              'Rendez-vous',
              'link2',
              null,
              null,
              null,
              parseISODate('2025-12-23')
            )
          )
        ).toBe(true);
      });
      test('should not display personal item if is listed in hidden items', async () => {
        // Given
        const followup = new Followup();
        const followupItem1 = new FollowupItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
        );
        const followupItem2 = new FollowupItem(
          'partner',
          'type',
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
          true,
          null,
          []
        );
        vi.spyOn(followup, 'items', 'get').mockReturnValue([
          followupItem1,
          followupItem2,
        ]);
        const item1 = new Item(
          'fake-id-1',
          'personal',
          'Rendez-vous',
          'link1',
          null,
          null,
          parseISODate('2025-09-22'),
          null
        );
        const item2 = new Item(
          'fake-id-2',
          'personal',
          'Rendez-vous',
          'link2',
          null,
          null,
          null,
          parseISODate('2025-12-23')
        );
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
        vi.spyOn(followupItem1, 'buildAgendaItem').mockReturnValue(item1);
        vi.spyOn(followupItem2, 'buildAgendaItem').mockReturnValue(item2);
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId')
          .mockReturnValueOnce('fake-id-1')
          .mockReturnValueOnce('fake-id-2');

        const existing = [];
        const itemKey = `ami-personal:${getTimestamp(item2.date)}:${slugify(item2.title)}`;
        existing.push(itemKey);
        localStorage.setItem('hidden_agenda_items_personal', JSON.stringify(existing));

        // When
        const agenda = new Agenda(null, followup, new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(agenda.now.length).equal(1);
        expect(agenda.now[0].equals(item1)).toBe(true);
        expect(agenda.next.length).equal(0);
      });
      test('should not display personal sub item if is listed in hidden items', async () => {
        // Given
        const followup = new Followup();
        const followupSubItem1 = new FollowupSubItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
          null
        );
        const followupSubItem2 = new FollowupSubItem(
          'partner',
          'type',
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
          true,
          null
        );
        const followupItem = new FollowupItem(
          'partner',
          'type',
          'id1',
          'ref1',
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
        );
        vi.spyOn(followupItem, 'futureSubItemWithMilestone', 'get').mockReturnValue([
          followupSubItem1,
          followupSubItem2,
        ]);
        vi.spyOn(followup, 'items', 'get').mockReturnValue([followupItem]);
        const item1 = new Item(
          'fake-id-1',
          'personal',
          'Rendez-vous',
          'link1',
          null,
          null,
          parseISODate('2025-09-22'),
          null
        );
        const item2 = new Item(
          'fake-id-2',
          'personal',
          'Rendez-vous',
          'link2',
          null,
          null,
          null,
          parseISODate('2025-12-23')
        );
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
        vi.spyOn(followupSubItem1, 'buildAgendaItem').mockReturnValue(item1);
        vi.spyOn(followupSubItem2, 'buildAgendaItem').mockReturnValue(item2);
        await userStore.login(mockUserInfo);
        vi.spyOn(utilsMethods, 'uniqueId')
          .mockReturnValueOnce('fake-id-1')
          .mockReturnValueOnce('fake-id-2');

        const existing = [];
        const itemKey = `ami-personal:${getTimestamp(item2.date)}:${slugify(item2.title)}`;
        existing.push(itemKey);
        localStorage.setItem('hidden_agenda_items_personal', JSON.stringify(existing));

        // When
        const agenda = new Agenda(null, followup, new Date('2025-11-01T12:00:00Z'));

        // Then
        expect(agenda.now.length).equal(1);
        expect(agenda.now[0].equals(item1)).toBe(true);
        expect(agenda.next.length).equal(0);
      });
    });
  });
  describe('buildAgenda', () => {
    test('should retrieve agenda items, followup items and init agenda with them', async () => {
      // Given
      const followup = new Followup();
      const followupItem1 = new FollowupItem(
        'partner',
        'type',
        'id1',
        'ref1',
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
      );
      const followupItem2 = new FollowupItem(
        'partner',
        'type',
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
        true,
        null,
        []
      );
      const followupSubItem3 = new FollowupSubItem(
        'partner',
        'type',
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
        true,
        null
      );
      const followupItem3 = new FollowupItem(
        'partner',
        'type',
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
        true,
        null,
        []
      );
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        followupItem1,
        followupItem2,
        followupItem3,
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      vi.spyOn(followupItem1, 'buildAgendaItem').mockReturnValue(null);
      vi.spyOn(followupItem2, 'buildAgendaItem').mockReturnValue(
        new Item(
          'fake-id',
          'personal',
          'Rendez-vous',
          'link1',
          null,
          null,
          parseISODate('2025-09-22'),
          null
        )
      );
      vi.spyOn(followupItem3, 'buildAgendaItem').mockReturnValue(
        new Item(
          'fake-id',
          'personal',
          'Rendez-vous',
          'link2',
          null,
          null,
          null,
          parseISODate('2025-12-23')
        )
      );
      vi.spyOn(followupItem3, 'futureSubItemWithMilestone', 'get').mockReturnValue([
        followupSubItem3,
      ]);
      vi.spyOn(followupSubItem3, 'buildAgendaItem').mockReturnValue(
        new Item(
          'fake-id',
          'personal',
          'Rendez-vous',
          'link3',
          null,
          null,
          null,
          parseISODate('2025-12-23')
        )
      );
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      const holiday1 = {
        kind: 'holiday',
        title: 'Holiday 1',
        description: '',
        date: null,
        start_date: parseISODate('2025-09-21'),
        end_date: parseISODate('2025-12-16'),
        zones: ['Zone A'],
        emoji: '',
      };
      const holiday2 = {
        kind: 'holiday',
        title: 'Holiday 2',
        description: '',
        date: null,
        start_date: parseISODate('2025-11-31'),
        end_date: parseISODate('2025-12-17'),
        zones: ['Corse'],
        emoji: '',
      };
      const holiday3 = {
        kind: 'holiday',
        title: 'Day 3',
        description: '',
        date: parseISODate('2025-11-16'),
        start_date: null,
        end_date: null,
        zones: [],
        emoji: '',
      };
      const holiday4 = {
        kind: 'holiday',
        title: 'Day 4',
        description: '',
        date: parseISODate('2025-12-31'),
        start_date: null,
        end_date: null,
        zones: [],
        emoji: '',
      };
      const spy = vi.spyOn(apiAgendaMethods, 'retrieveAgenda').mockResolvedValue({
        school_holidays: [holiday1, holiday2],
        public_holidays: [holiday3, holiday4],
        elections: [],
      });
      await userStore.login(mockUserInfo);
      vi.spyOn(utilsMethods, 'uniqueId').mockReset().mockReturnValue('fake-id');

      // When
      await userStore.login(mockUserInfo);
      const agenda = await buildAgenda(null, new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(agenda).toBeInstanceOf(Agenda);
      expect(agenda.now.length).equal(3);
      expect(
        agenda.now[0].equals(
          new Item(
            'fake-id',
            'holiday',
            'Holiday 1',
            '',
            'Zone A',
            null,
            holiday1.start_date,
            holiday1.end_date
          )
        )
      ).toBe(true);
      expect(
        agenda.now[1].equals(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link1',
            null,
            null,
            parseISODate('2025-09-22'),
            null
          )
        )
      ).toBe(true);
      expect(
        agenda.now[2].equals(
          new Item('fake-id', 'holiday', 'Day 3', '', null, holiday3.date, null, null)
        )
      ).toBe(true);
      expect(agenda.next.length).equal(4);
      expect(
        agenda.next[0].equals(
          new Item(
            'fake-id',
            'holiday',
            'Holiday 2',
            '',
            'Corse',
            null,
            holiday2.start_date,
            holiday2.end_date
          )
        )
      ).toBe(true);
      expect(
        agenda.next[1].equals(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link2',
            null,
            null,
            null,
            parseISODate('2025-12-23')
          )
        )
      ).toBe(true);
      expect(
        agenda.next[2].equals(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link3',
            null,
            null,
            null,
            parseISODate('2025-12-23')
          )
        )
      ).toBe(true);
      expect(
        agenda.next[3].equals(
          new Item('fake-id', 'holiday', 'Day 4', '', null, holiday4.date, null, null)
        )
      ).toBe(true);
    });
    test('should retrieve agenda items and init agenda with them, followup is alreay provided', async () => {
      // Given
      const followup = new Followup();
      const followupItem1 = new FollowupItem(
        'partner',
        'type',
        'id1',
        'ref1',
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
      );
      const followupItem2 = new FollowupItem(
        'partner',
        'type',
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
        true,
        null,
        []
      );
      const followupSubItem3 = new FollowupSubItem(
        'partner',
        'type',
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
        true,
        null
      );
      const followupItem3 = new FollowupItem(
        'partner',
        'type',
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
        true,
        null,
        []
      );
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        followupItem1,
        followupItem2,
        followupItem3,
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      vi.spyOn(followupItem1, 'buildAgendaItem').mockReturnValue(null);
      vi.spyOn(followupItem2, 'buildAgendaItem').mockReturnValue(
        new Item(
          'fake-id',
          'personal',
          'Rendez-vous',
          'link1',
          null,
          null,
          parseISODate('2025-09-22'),
          null
        )
      );
      vi.spyOn(followupItem3, 'buildAgendaItem').mockReturnValue(
        new Item(
          'fake-id',
          'personal',
          'Rendez-vous',
          'link2',
          null,
          null,
          null,
          parseISODate('2025-12-23')
        )
      );
      vi.spyOn(followupItem3, 'futureSubItemWithMilestone', 'get').mockReturnValue([
        followupSubItem3,
      ]);
      vi.spyOn(followupSubItem3, 'buildAgendaItem').mockReturnValue(
        new Item(
          'fake-id',
          'personal',
          'Rendez-vous',
          'link3',
          null,
          null,
          null,
          parseISODate('2025-12-23')
        )
      );
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      const holiday1 = {
        kind: 'holiday',
        title: 'Holiday 1',
        description: '',
        date: null,
        start_date: parseISODate('2025-09-21'),
        end_date: parseISODate('2025-12-16'),
        zones: ['Zone A'],
        emoji: '',
      };
      const holiday2 = {
        kind: 'holiday',
        title: 'Holiday 2',
        description: '',
        date: null,
        start_date: parseISODate('2025-11-31'),
        end_date: parseISODate('2025-12-17'),
        zones: ['Corse'],
        emoji: '',
      };
      const holiday3 = {
        kind: 'holiday',
        title: 'Day 3',
        description: '',
        date: parseISODate('2025-11-16'),
        start_date: null,
        end_date: null,
        zones: [],
        emoji: '',
      };
      const holiday4 = {
        kind: 'holiday',
        title: 'Day 4',
        description: '',
        date: parseISODate('2025-12-31'),
        start_date: null,
        end_date: null,
        zones: [],
        emoji: '',
      };
      const spy = vi.spyOn(apiAgendaMethods, 'retrieveAgenda').mockResolvedValue({
        school_holidays: [holiday1, holiday2],
        public_holidays: [holiday3, holiday4],
        elections: [],
      });
      await userStore.login(mockUserInfo);
      vi.spyOn(utilsMethods, 'uniqueId').mockReset().mockReturnValue('fake-id');

      // When
      await userStore.login(mockUserInfo);
      const agenda = await buildAgenda(followup, new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(agenda).toBeInstanceOf(Agenda);
      expect(agenda.now.length).equal(3);
      expect(
        agenda.now[0].equals(
          new Item(
            'fake-id',
            'holiday',
            'Holiday 1',
            '',
            'Zone A',
            null,
            holiday1.start_date,
            holiday1.end_date
          )
        )
      ).toBe(true);
      expect(
        agenda.now[1].equals(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link1',
            null,
            null,
            parseISODate('2025-09-22'),
            null
          )
        )
      ).toBe(true);
      expect(
        agenda.now[2].equals(
          new Item('fake-id', 'holiday', 'Day 3', '', null, holiday3.date, null, null)
        )
      ).toBe(true);
      expect(agenda.next.length).equal(4);
      expect(
        agenda.next[0].equals(
          new Item(
            'fake-id',
            'holiday',
            'Holiday 2',
            '',
            'Corse',
            null,
            holiday2.start_date,
            holiday2.end_date
          )
        )
      ).toBe(true);
      expect(
        agenda.next[1].equals(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link2',
            null,
            null,
            null,
            parseISODate('2025-12-23')
          )
        )
      ).toBe(true);
      expect(
        agenda.next[2].equals(
          new Item(
            'fake-id',
            'personal',
            'Rendez-vous',
            'link3',
            null,
            null,
            null,
            parseISODate('2025-12-23')
          )
        )
      ).toBe(true);
      expect(
        agenda.next[3].equals(
          new Item('fake-id', 'holiday', 'Day 4', '', null, holiday4.date, null, null)
        )
      ).toBe(true);
    });
  });
});
