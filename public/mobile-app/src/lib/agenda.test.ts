import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Agenda, buildAgenda, Item } from '$lib/agenda';
import * as catalogMethods from '$lib/api-catalog';
import * as scheduledNotificationsMethods from '$lib/scheduled-notifications';
import { userStore } from '$lib/state/User.svelte';
import { mockUserIdentity, mockUserInfo } from '$tests/utils';

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
        );
        const item2 = new Item(
          'holiday',
          'title',
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
          'holiday',
          'title',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'holiday',
          'title',
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
          'holiday',
          'title',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'holiday',
          'title',
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
          'holiday',
          'title',
          'description',
          new Date('2025-11-11'),
          null,
          null
        );
        const item2 = new Item(
          'holiday',
          'title',
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
        );

        // When
        const period = item.period;

        // Then
        expect(period).equal('Du 15 octobre au 15 novembre 2025');
      });
      test('should not mention start date year and month', async () => {
        // Given
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-10-15'),
          new Date('2025-10-20')
        );

        // When
        const period = item.period;

        // Then
        expect(period).equal('Du 15 au 20 octobre 2025');
      });
      test('should mention start date year and month', async () => {
        // Given
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-12-20'),
          new Date('2026-01-02')
        );

        // When
        const period = item.period;

        // Then
        expect(period).equal('Du 20 décembre 2025 au 2 janvier 2026');
      });
      test('should mention only start date and not "Du .. au .."', async () => {
        // Given
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2027-05-07'),
          new Date('2027-05-07')
        );

        // When
        const period = item.period;

        // Then
        expect(period).equal('7 mai 2027');
      });
      test('should mention "À partir de"', async () => {
        const item = new Item(
          'holiday',
          'title',
          'description',
          null,
          new Date('2025-12-20'),
          null
        );

        // When
        const period = item.period;

        // Then
        expect(period).equal('À partir du 20 décembre 2025');
      });
      test('should mention only the date', async () => {
        const item = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20'),
          null,
          null
        );

        // When
        const period = item.period;

        // Then
        expect(period).equal('20 décembre 2025');
      });
    });
    describe('label', () => {
      test('should return a label depending on kind', async () => {
        // Given
        const item1 = new Item(
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item('otv', 'title', 'description', new Date('2025-12-20'));
        const item4 = new Item(
          'election',
          'title',
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
        expect(label3).equal('Logement');
        expect(label4).equal('Élections');
      });
    });
    describe('icon', () => {
      test('should return an icon depending on kind', async () => {
        // Given
        const item1 = new Item(
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item('otv', 'title', 'description', new Date('2025-12-20'));
        const item4 = new Item(
          'election',
          'title',
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
        expect(icon3).equal('fr-icon-home-4-fill');
        expect(icon4).equal('fr-icon-chat-check-fill');
      });
    });
    describe('link', () => {
      test('should return a link depending on kind', async () => {
        // Given
        const item1 = new Item(
          // @ts-expect-error: `'incorrect'` isn't a proper Kind, so typescript will complain
          'incorrect',
          'title',
          'description',
          new Date('2025-12-20')
        );
        const item2 = new Item(
          'holiday',
          'title',
          'description',
          new Date('2025-12-20')
        );
        const item3 = new Item('otv', 'title', 'description', new Date('2025-12-20'));
        const item4 = new Item(
          'election',
          'title',
          'description',
          new Date('2025-12-20')
        );

        // When
        const link1 = item1.link;
        const link2 = item2.link;
        const link3 = item3.link;
        const link4 = item4.link;

        // Then
        expect(link1).equal('');
        expect(link2).equal('');
        expect(link3).equal('/#/procedure');
        expect(link4).equal('');
      });
    });
  });
  describe('Agenda', () => {
    afterEach(() => {
      localStorage.clear();
      userStore.connected = null;
      vi.resetAllMocks();
    });
    describe('Now/Next', () => {
      test('should organize items in now and next', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday 1',
          description: '',
          date: null,
          start_date: new Date('2025-09-20T23:00:00Z'),
          end_date: new Date('2025-12-15T23:00:00Z'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday 2',
          description: '',
          date: null,
          start_date: new Date('2025-10-20T23:00:00Z'),
          end_date: new Date('2025-11-15T23:00:00Z'),
          zones: ['Zone B'],
          emoji: '',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Holiday 3',
          description: '',
          date: null,
          start_date: new Date('2025-11-20T23:00:00Z'),
          end_date: new Date('2025-12-15T23:00:00Z'),
          zones: [],
          emoji: 'foo',
        };
        const holiday4 = {
          kind: 'holiday',
          title: 'Holiday 4',
          description: '',
          date: null,
          start_date: new Date('2025-11-30T23:00:00Z'),
          end_date: new Date('2025-12-16T23:00:00Z'),
          zones: [],
          emoji: '',
        };
        const holiday5 = {
          kind: 'holiday',
          title: 'Holiday 5',
          description: '',
          date: null,
          start_date: new Date('2025-12-20T23:00:00Z'),
          end_date: new Date('2025-12-24T23:00:00Z'),
          zones: [],
          emoji: '',
        };
        const holiday6 = {
          kind: 'holiday',
          title: 'Day 6',
          description: '',
          date: new Date('2025-11-11T23:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const holiday7 = {
          kind: 'holiday',
          title: 'Day 7',
          description: '',
          date: new Date('2025-12-10T23:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        const election1 = {
          kind: 'election',
          title: 'Election1',
          description: 'description',
          date: new Date('2025-11-11T24:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: 'bar',
        };
        const election2 = {
          kind: 'election',
          title: 'Election2',
          description: 'description',
          date: new Date('2025-12-10T24:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3, holiday4, holiday5],
            public_holidays: [holiday6, holiday7],
            elections: [election1, election2],
          },
          new Date('2025-11-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(5);
        expect(
          agenda.now[0].equals(
            new Item(
              'holiday',
              'Holiday 1 foo',
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
              'holiday',
              'Holiday 2',
              'Zone B',
              null,
              holiday2.start_date,
              holiday2.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.now[2].equals(
            new Item('holiday', 'Day 6 bar', null, holiday6.date, null, null)
          )
        ).toBe(true);
        expect(
          agenda.now[3].equals(
            new Item(
              'election',
              'Election1 bar',
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
              'holiday',
              'Holiday 3 foo',
              null,
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
              'holiday',
              'Holiday 4',
              null,
              null,
              holiday4.start_date,
              holiday4.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.next[1].equals(
            new Item('holiday', 'Day 7', null, holiday7.date, null, null)
          )
        ).toBe(true);
        expect(
          agenda.next[2].equals(
            new Item('election', 'Election2', 'description', election2.date, null, null)
          )
        ).toBe(true);
        expect(
          agenda.next[3].equals(
            new Item(
              'holiday',
              'Holiday 5',
              null,
              null,
              holiday5.start_date,
              holiday5.end_date
            )
          )
        ).toBe(true);
      });
    });
    describe('Zones', () => {
      test('should mark holidays as custom if zones match user zone', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-13T23:00:00Z'),
          end_date: new Date('2026-03-01T23:00:00Z'),
          zones: ['Zone C'],
          emoji: 'foo',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Summer Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-07-01T23:00:00Z'),
          end_date: new Date('2026-08-31T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Zone C'],
          emoji: 'bar',
        };
        const holiday4 = {
          kind: 'holiday',
          title: 'Day',
          description: '',
          date: new Date('2026-02-15T23:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3],
            public_holidays: [holiday4],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(4);
        expect(
          agenda.now[0].equals(
            new Item(
              'otv',
              'Opération Tranquillité Vacances 🏠',
              'Inscrivez-vous pour protéger votre domicile pendant votre absence',
              null,
              new Date('2026-01-23T23:00:00Z'),
              null
            )
          )
        ).toBe(true);
        expect(
          agenda.now[1].equals(
            new Item(
              'holiday',
              'Holiday foo',
              'Zone A',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
        expect(
          agenda.now[2].equals(
            new Item(
              'holiday',
              'Holiday foo',
              'Paris (75) 🏠',
              null,
              holiday2.start_date,
              holiday2.end_date,
              true
            )
          )
        ).toBe(true);
        expect(
          agenda.now[3].equals(
            new Item('holiday', 'Day', null, holiday4.date, null, null)
          )
        ).toBe(true);
        expect(agenda.next.length).equal(1);
        expect(
          agenda.next[0].equals(
            new Item(
              'holiday',
              'Summer Holiday bar',
              'Paris (75) 🏠, Zone A, Zone B',
              null,
              holiday3.start_date,
              holiday3.end_date,
              true
            )
          )
        ).toBe(true);
      });
      test('should ignore some zones (XXX tmp)', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone foo'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-13T23:00:00Z'),
          end_date: new Date('2026-03-01T23:00:00Z'),
          zones: ['Zone foo'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2],
            public_holidays: [],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(
          agenda.now[0].equals(
            new Item(
              'holiday',
              'Holiday foo',
              'Zone A',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(0);
      });
      test('should ignore some zones - user has address (XXX tmp)', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
        newMockUserIdentity.dataDetails.address.postcode = '75000'; // Zone C
        localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone C', 'Zone foo'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1],
            public_holidays: [],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(2);
        expect(
          agenda.now[0].equals(
            new Item(
              'otv',
              'Opération Tranquillité Vacances 🏠',
              'Inscrivez-vous pour protéger votre domicile pendant votre absence',
              null,
              new Date('2026-01-16T23:00:00Z'),
              null
            )
          )
        ).toBe(true);
        expect(
          agenda.now[1].equals(
            new Item(
              'holiday',
              'Holiday foo',
              'Paris (75) 🏠',
              null,
              holiday1.start_date,
              holiday1.end_date,
              true
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(0);
      });
    });
    describe('OTV', () => {
      test('should not display OTV if holiday of user Zone is not displayed', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
        newMockUserIdentity.dataDetails.address.postcode = '20000'; // Corse
        localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1],
            public_holidays: [],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(
          agenda.now[0].equals(
            new Item(
              'holiday',
              'Holiday foo',
              'Zone A',
              null,
              holiday1.start_date,
              holiday1.end_date
            )
          )
        ).toBe(true);
        expect(agenda.next.length).equal(0);
      });
      test('should not display past items or OTV related to past holidays', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-13T23:00:00Z'),
          end_date: new Date('2026-03-01T23:00:00Z'),
          zones: ['Zone B'],
          emoji: 'foo',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Day',
          description: '',
          date: new Date('2026-02-02T23:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        const election = {
          kind: 'election',
          title: 'Election',
          description: '',
          date: new Date('2026-02-02T23:00:00Z'),
          start_date: null,
          end_date: null,
          zones: [],
          emoji: '',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2],
            public_holidays: [holiday3],
            elections: [election],
          },
          new Date('2026-02-24T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(1);
        expect(agenda.now[0].title).toEqual('Holiday foo');
      });
      test('should generate only one OTV per holiday', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone B'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-13T23:00:00Z'),
          end_date: new Date('2026-03-01T23:00:00Z'),
          zones: ['Zone C'],
          emoji: 'foo',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2],
            public_holidays: [],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(3);
      });
    });
    describe('Scheduled notifications', () => {
      test('should create scheduled notifications for otv', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const spy = vi
          .spyOn(scheduledNotificationsMethods, 'createScheduledNotification')
          .mockResolvedValue(true);
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-13T23:00:00Z'),
          end_date: new Date('2026-03-01T23:00:00Z'),
          zones: ['Zone C'],
          emoji: 'foo',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Summer Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-07-01T23:00:00Z'),
          end_date: new Date('2026-08-31T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Zone C'],
          emoji: 'bar',
        };
        await userStore.login(mockUserInfo);

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3],
            public_holidays: [],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(3);
        expect(spy).toHaveBeenCalledTimes(2);
        expect(spy).toHaveBeenCalledWith({
          content_body:
            "Demandez l'Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.",
          content_icon: 'fr-icon-megaphone-line',
          content_title: 'Et si on veillait sur votre logement ? 👮',
          reference: 'ami-otv:d-3w:2026:holiday',
          internal_url: '/#/procedure',
          scheduled_at: new Date('2026-01-23T23:00:00Z'),
        });
        expect(spy).toHaveBeenCalledWith({
          content_body:
            "Demandez l'Opération Tranquillité Vacances afin de partir en vacances l’esprit (plus) tranquille.",
          content_icon: 'fr-icon-megaphone-line',
          content_title: 'Et si on veillait sur votre logement ? 👮',
          reference: 'ami-otv:d-3w:2026:summer-holiday',
          internal_url: '/#/procedure',
          scheduled_at: new Date('2026-06-10T23:00:00Z'),
        });
      });
      test('should create scheduled notifications for otv - scheduled notifications already sent', async () => {
        // Given
        vi.stubEnv('TZ', 'Europe/Paris');
        const spy = vi
          .spyOn(scheduledNotificationsMethods, 'createScheduledNotification')
          .mockResolvedValue(true);
        localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
        const holiday1 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A'],
          emoji: 'foo',
        };
        const holiday2 = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-13T23:00:00Z'),
          end_date: new Date('2026-03-01T23:00:00Z'),
          zones: ['Zone C'],
          emoji: 'foo',
        };
        const holiday3 = {
          kind: 'holiday',
          title: 'Summer Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-07-01T23:00:00Z'),
          end_date: new Date('2026-08-31T23:00:00Z'),
          zones: [],
          emoji: 'bar',
        };
        await userStore.login(mockUserInfo);
        userStore.connected?.addScheduledNotificationCreatedKey(
          'ami-otv:d-3w:2026:holiday'
        );
        userStore.connected?.addScheduledNotificationCreatedKey(
          'ami-otv:d-3w:2026:summer-holiday'
        );

        // When
        const agenda = new Agenda(
          {
            school_holidays: [holiday1, holiday2, holiday3],
            public_holidays: [],
            elections: [],
          },
          new Date('2026-02-01T12:00:00Z')
        );

        // Then
        expect(agenda.now.length).equal(3);
        expect(spy).toHaveBeenCalledTimes(0);
      });
    });
  });
  describe('buildAgenda', () => {
    test('should retrieve catalogs and init agenda with them', async () => {
      // Given
      vi.stubEnv('TZ', 'Europe/Paris');
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      const holiday1 = {
        kind: 'holiday',
        title: 'Holiday 1',
        description: '',
        date: null,
        start_date: new Date('2025-09-20T23:00:00Z'),
        end_date: new Date('2025-12-15T23:00:00Z'),
        zones: ['Zone A'],
        emoji: '',
      };
      const holiday2 = {
        kind: 'holiday',
        title: 'Holiday 2',
        description: '',
        date: null,
        start_date: new Date('2025-11-30T23:00:00Z'),
        end_date: new Date('2025-12-16T23:00:00Z'),
        zones: [],
        emoji: '',
      };
      const holiday3 = {
        kind: 'holiday',
        title: 'Day 3',
        description: '',
        date: new Date('2025-11-15T23:00:00Z'),
        start_date: null,
        end_date: null,
        zones: [],
        emoji: '',
      };
      const holiday4 = {
        kind: 'holiday',
        title: 'Day 4',
        description: '',
        date: new Date('2025-12-30T23:00:00Z'),
        start_date: null,
        end_date: null,
        zones: [],
        emoji: '',
      };
      const spy = vi.spyOn(catalogMethods, 'retrieveCatalog').mockResolvedValue({
        school_holidays: [holiday1, holiday2],
        public_holidays: [holiday3, holiday4],
        elections: [],
      });
      await userStore.login(mockUserInfo);

      // When
      const agenda = await buildAgenda(new Date('2025-11-01T12:00:00Z'));

      // Then
      expect(spy).toHaveBeenCalledTimes(1);
      expect(agenda).toBeInstanceOf(Agenda);
      expect(agenda.now.length).equal(2);
      expect(
        agenda.now[0].equals(
          new Item(
            'holiday',
            'Holiday 1',
            'Zone A',
            null,
            holiday1.start_date,
            holiday1.end_date
          )
        )
      ).toBe(true);
      expect(
        agenda.now[1].equals(
          new Item('holiday', 'Day 3', null, holiday3.date, null, null)
        )
      ).toBe(true);
      expect(agenda.next.length).equal(2);
      expect(
        agenda.next[0].equals(
          new Item(
            'holiday',
            'Holiday 2',
            null,
            null,
            holiday2.start_date,
            holiday2.end_date
          )
        )
      ).toBe(true);
      expect(
        agenda.next[1].equals(
          new Item('holiday', 'Day 4', null, holiday4.date, null, null)
        )
      ).toBe(true);
    });
  });
});
