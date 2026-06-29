import { afterEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { Address } from '$lib/address';
import type { APIAgendaItem } from '$lib/api-agenda';
import * as matomoMethods from '$lib/matomo';
import { Preferences } from '$lib/state/preferences';

describe('/preferences.ts', () => {
  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Preferences', () => {
    describe('fromJSON', () => {
      test('should init with values - empty values', async () => {
        // Given
        const preferences_data = { _zones: [], _addresses: [] };

        // When
        const preferences = Preferences.fromJSON(preferences_data);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual([]);
        expect(preferences.addresses).toEqual([]);
      });
      test('should init with values - not empty values', async () => {
        // Given
        const address1 = new Address('some random city');
        const address2 = new Address('some other random city');
        const preferences_data = {
          _zones: ['Zone A', 'Martinique'],
          _addresses: [address1, address2],
        };

        // When
        const preferences = Preferences.fromJSON(preferences_data);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Martinique']);
        expect(preferences.addresses).toEqual([address1, address2]);
      });
    });

    describe('getDefault', () => {
      test('no address: should init zones with A, B, C and Corse', async () => {
        // When
        const preferences = Preferences.getDefault(undefined);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Corse']);
        expect(preferences.addresses).toEqual([]);
      });
      test('with address in hexagone: should init zones with A, B, C and Corse', async () => {
        // Given
        const address = new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        );

        // When
        const preferences = Preferences.getDefault(address);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Corse']);
        expect(preferences.addresses).toEqual([]);
      });
      test('with address in Corse: should init zones with A, B, C and Corse', async () => {
        // Given
        const address = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );

        // When
        const preferences = Preferences.getDefault(address);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Corse']);
        expect(preferences.addresses).toEqual([]);
      });
      test('with address out of hexagone and Corse: should init zones with the corresponding zone', async () => {
        // Given
        const address = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00002',
          '2 Rue de Paris 97400 Saint-Denis',
          '2 Rue de Paris',
          '97400'
        );

        // When
        const preferences = Preferences.getDefault(address);

        // Then
        expect(preferences instanceof Preferences).toBe(true);
        expect(preferences.zones).toEqual(['Réunion']);
        expect(preferences.addresses).toEqual([]);
      });
    });

    describe('isSchoolHolidayConcerned', () => {
      test('should return true as holiday zones match user preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone A', 'Zone C'], []);

        // When
        const result = preferences.isSchoolHolidayConcerned(item);

        // Then
        expect(result).toEqual(true);
      });
      test('should return false as holiday zones do not match user preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone C', 'Corse'], []);

        // When
        const result = preferences.isSchoolHolidayConcerned(item);

        // Then
        expect(result).toEqual(false);
      });
      test('should return false as user preferences zones are empty', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences([], []);

        // When
        const result = preferences.isSchoolHolidayConcerned(item);

        // Then
        expect(result).toEqual(false);
      });
      test('should return false as holiday zones are empty', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: [],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone C', 'Corse'], []);

        // When
        const result = preferences.isSchoolHolidayConcerned(item);

        // Then
        expect(result).toEqual(false);
      });
    });

    describe('getSchoolHolidayDescription', () => {
      test('should return "Zone A" as holiday zones match user preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone A', 'Zone C'], []);

        // When
        const result = preferences.getSchoolHolidayDescription(item, undefined);

        // Then
        expect(result).toEqual('Zone A');
      });
      test('should return empty string as holiday zones match all zones of user preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Zone C'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone A', 'Zone C'], []);

        // When
        const result = preferences.getSchoolHolidayDescription(item, undefined);

        // Then
        expect(result).toEqual('');
      });
      test('should return only user city as holiday zones match all zones of user preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Zone C'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone A', 'Zone C'], []);
        const userAddress = new Address('Paris', '', '', 'Paris', 'Paris', '75000');

        // When
        const result = preferences.getSchoolHolidayDescription(item, userAddress);

        // Then
        expect(result).toEqual('');
      });
      test('should return "Zone A" and city as holiday zones match user preferences - with city preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const address1 = new Address(
          'Périgueux',
          '',
          '',
          'Périgueux',
          'Périgueux',
          '24000'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const preferences = new Preferences(['Zone A', 'Zone C'], [address1, address2]);

        // When
        const result = preferences.getSchoolHolidayDescription(item, undefined);

        // Then
        expect(result).toEqual('Zone A&nbsp;: <strong>Périgueux (24)</strong>');
      });
      test('should mention cities from user address and preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Zone C', 'Corse', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const address1 = new Address(
          'Périgueux',
          '',
          '',
          'Périgueux',
          'Périgueux',
          '24000'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const address3 = new Address('Limoges', '', '', 'Limoges', 'Limoges', '87000');
        const address4 = new Address('Arpajon', '', '', 'Arpajon', 'Arpajon', '91290');
        const preferences = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Corse', 'Réunion'],
          [address1, address2, address3, address4]
        );
        const userAddress = new Address('Paris', '', '', 'Paris', 'Paris', '75000');

        // When
        const result = preferences.getSchoolHolidayDescription(item, userAddress);

        // Then
        expect(result).toEqual(
          'Zone A&nbsp;: <strong>Limoges (87), Périgueux (24)</strong>, Zone B, Zone C&nbsp;: <strong>Arpajon (91), Paris (75) 🏠</strong>, Corse&nbsp;: <strong>Bastia (20)</strong>'
        );
      });
      test('should return only user city as holiday zones match all zones of user preferences - with addresses in preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Zone C', 'Corse', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const address1 = new Address(
          'Périgueux',
          '',
          '',
          'Périgueux',
          'Périgueux',
          '24000'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const address3 = new Address('Limoges', '', '', 'Limoges', 'Limoges', '87000');
        const address4 = new Address('Arpajon', '', '', 'Arpajon', 'Arpajon', '91290');
        const preferences = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Corse'],
          [address1, address2, address3, address4]
        );
        const userAddress = new Address('Paris', '', '', 'Paris', 'Paris', '75000');

        // When
        const result = preferences.getSchoolHolidayDescription(item, userAddress);

        // Then
        expect(result).toEqual('');
      });
      test('should return empty string as holiday zones do not match user preferences', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone C', 'Corse'], []);

        // When
        const result = preferences.getSchoolHolidayDescription(item, undefined);

        // Then
        expect(result).toEqual('');
      });
      test('should return empty string as user preferences zones are empty', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: ['Zone A', 'Zone B', 'Martinique'],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences([], []);

        // When
        const result = preferences.getSchoolHolidayDescription(item, undefined);

        // Then
        expect(result).toEqual('');
      });
      test('should return empty string as holiday zones are empty', async () => {
        // Given
        const item = {
          kind: 'holiday',
          title: 'Holiday',
          description: '',
          date: null,
          start_date: new Date('2026-02-06T23:00:00Z'),
          end_date: new Date('2026-02-22T23:00:00Z'),
          zones: [],
          emoji: 'foo',
        } as APIAgendaItem;
        const preferences = new Preferences(['Zone C', 'Corse'], []);

        // When
        const result = preferences.getSchoolHolidayDescription(item, undefined);

        // Then
        expect(result).toEqual('');
      });
    });

    describe('addZone', () => {
      test('should add zone', async () => {
        // Given
        const preferences1 = new Preferences([], []);
        const preferences2 = new Preferences(['Foo'], []);
        const preferences3 = new Preferences(['Foo', 'Bar'], []);
        const trackZoneSpy = vi
          .spyOn(matomoMethods, 'trackZone')
          .mockResolvedValue(undefined);

        // When
        preferences1.addZone('Bar');
        preferences2.addZone('Bar');
        preferences3.addZone('Bar');

        // Then
        expect(preferences1.zones).toEqual(['Bar']);
        expect(preferences2.zones).toEqual(['Foo', 'Bar']);
        expect(preferences3.zones).toEqual(['Foo', 'Bar']);
        expect(trackZoneSpy).toHaveBeenCalledTimes(2);
        expect(trackZoneSpy).toHaveBeenNthCalledWith(1, 'Bar', true);
        expect(trackZoneSpy).toHaveBeenNthCalledWith(2, 'Bar', true);
      });
    });

    describe('removeZone', () => {
      test('should remove zone', async () => {
        // Given
        const preferences1 = new Preferences([], []);
        const preferences2 = new Preferences(['Foo'], []);
        const preferences3 = new Preferences(['Foo', 'Bar'], []);
        const trackZoneSpy = vi
          .spyOn(matomoMethods, 'trackZone')
          .mockResolvedValue(undefined);

        // When
        preferences1.removeZone('Bar');
        preferences2.removeZone('Bar');
        preferences3.removeZone('Bar');

        // Then
        expect(preferences1.zones).toEqual([]);
        expect(preferences2.zones).toEqual(['Foo']);
        expect(preferences3.zones).toEqual(['Foo']);
        expect(trackZoneSpy).toHaveBeenCalledTimes(1);
        expect(trackZoneSpy).toHaveBeenNthCalledWith(1, 'Bar', false);
      });
    });

    describe('addAddress', () => {
      test('should add address', async () => {
        // Given
        const address1 = new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const address3 = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00002',
          '2 Rue de Paris 97400 Saint-Denis',
          '2 Rue de Paris',
          '97400'
        );
        const address3bis = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00003', // other id
          '3 Rue de Paris 97400 Saint-Denis',
          '3 Rue de Paris',
          '97400'
        );
        const preferences1 = new Preferences([], []);
        const preferences2 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C'],
          [address1, address2]
        );
        const preferences3 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Réunion'],
          [address1, address2]
        );
        const preferences4 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Réunion'],
          [address1, address2, address3bis]
        );
        const trackZoneSpy = vi
          .spyOn(matomoMethods, 'trackZone')
          .mockResolvedValue(undefined);

        // When
        preferences1.addAddress(address3);
        preferences2.addAddress(address3);
        preferences3.addAddress(address3);
        preferences4.addAddress(address3);

        // Then
        expect(preferences1.zones).toEqual(['Réunion']);
        expect(preferences1.addresses).toEqual([address3]);
        expect(preferences2.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Réunion']);
        expect(preferences2.addresses).toEqual([address1, address2, address3]);
        expect(preferences3.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Réunion']);
        expect(preferences3.addresses).toEqual([address1, address2, address3]);
        expect(preferences4.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Réunion']);
        expect(preferences4.addresses).toEqual([address1, address2, address3bis]);
        expect(trackZoneSpy).toHaveBeenCalledTimes(2);
        expect(trackZoneSpy).toHaveBeenNthCalledWith(1, 'Réunion', true);
        expect(trackZoneSpy).toHaveBeenNthCalledWith(2, 'Réunion', true);
      });
    });

    describe('removeAddress', () => {
      test('should remove address', async () => {
        // Given
        const address1 = new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const address3 = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00002',
          '2 Rue de Paris 97400 Saint-Denis',
          '2 Rue de Paris',
          '97400'
        );
        const address3bis = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00003', // other id
          '3 Rue de Paris 97400 Saint-Denis',
          '3 Rue de Paris',
          '97400'
        );
        const address4 = new Address(
          'Saint-Paul',
          '974, La Réunion',
          '97411_1060_00003',
          '97460 Saint-Denis',
          '',
          '97460'
        );
        const preferences1 = new Preferences([], []);
        const preferences2 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C'],
          [address1, address2]
        );
        const preferences3 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Réunion'],
          [address1, address2]
        );
        const preferences4 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Réunion'],
          [address1, address2, address3bis]
        );
        const preferences5 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C', 'Réunion'],
          [address1, address2, address3bis, address4]
        );
        const trackZoneSpy = vi
          .spyOn(matomoMethods, 'trackZone')
          .mockResolvedValue(undefined);

        // When
        preferences1.removeAddress(address3);
        preferences2.removeAddress(address3);
        preferences3.removeAddress(address3);
        preferences4.removeAddress(address3);
        preferences5.removeAddress(address3);

        // Then
        expect(preferences1.zones).toEqual([]);
        expect(preferences1.addresses).toEqual([]);
        expect(preferences2.zones).toEqual(['Zone A', 'Zone B', 'Zone C']);
        expect(preferences2.addresses).toEqual([address1, address2]);
        expect(preferences3.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Réunion']);
        expect(preferences3.addresses).toEqual([address1, address2]);
        expect(preferences4.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Réunion']);
        expect(preferences4.addresses).toEqual([address1, address2]);
        expect(preferences5.zones).toEqual(['Zone A', 'Zone B', 'Zone C', 'Réunion']);
        expect(preferences5.addresses).toEqual([address1, address2, address4]);
        expect(trackZoneSpy).toHaveBeenCalledTimes(0);
      });
    });

    describe('clearAddresses', () => {
      test('should clear addresses', async () => {
        // Given
        const address1 = new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const preferences1 = new Preferences([], []);
        const preferences2 = new Preferences(
          ['Zone A', 'Zone B', 'Zone C'],
          [address1, address2]
        );

        const trackZoneSpy = vi
          .spyOn(matomoMethods, 'trackZone')
          .mockResolvedValue(undefined);

        // When
        preferences1.clearAddresses();
        preferences2.clearAddresses();

        // Then
        expect(preferences1.zones).toEqual([]);
        expect(preferences1.addresses).toEqual([]);
        expect(preferences2.zones).toEqual(['Zone A', 'Zone B', 'Zone C']);
        expect(preferences2.addresses).toEqual([]);
        expect(trackZoneSpy).toHaveBeenCalledTimes(0);
      });
    });

    describe('getZoneInfos', () => {
      test('user has no address and no preferences', async () => {
        // Given
        const preferences = new Preferences([], []);

        // When
        const result = preferences.getZoneInfos(undefined);

        // Then
        expect(result).toEqual([
          {
            selected: false,
            tags: [],
            zone: 'Zone A',
          },
          {
            selected: false,
            tags: [],
            zone: 'Zone B',
          },
          {
            selected: false,
            tags: [],
            zone: 'Zone C',
          },
          {
            selected: false,
            tags: [],
            zone: 'Corse',
          },
          {
            selected: false,
            tags: [],
            zone: 'Guadeloupe',
          },
          {
            selected: false,
            tags: [],
            zone: 'Guyane',
          },
          {
            selected: false,
            tags: [],
            zone: 'Martinique',
          },
          {
            selected: false,
            tags: [],
            zone: 'Mayotte',
          },
          {
            selected: false,
            tags: [],
            zone: 'Nouvelle Calédonie',
          },
          {
            selected: false,
            tags: [],
            zone: 'Polynésie',
          },
          {
            selected: false,
            tags: [],
            zone: 'Réunion',
          },
          {
            selected: false,
            tags: [],
            zone: 'Saint Pierre et Miquelon',
          },
          {
            selected: false,
            tags: [],
            zone: 'Wallis et Futuna',
          },
        ]);
      });
      test('user has preferences but no address', async () => {
        // Given
        const preferences = new Preferences(['Zone A', 'Zone B'], []);

        // When
        const result = preferences.getZoneInfos(undefined);

        // Then
        expect(result).toEqual([
          {
            selected: true,
            tags: [],
            zone: 'Zone A',
          },
          {
            selected: true,
            tags: [],
            zone: 'Zone B',
          },
          {
            selected: false,
            tags: [],
            zone: 'Zone C',
          },
          {
            selected: false,
            tags: [],
            zone: 'Corse',
          },
          {
            selected: false,
            tags: [],
            zone: 'Guadeloupe',
          },
          {
            selected: false,
            tags: [],
            zone: 'Guyane',
          },
          {
            selected: false,
            tags: [],
            zone: 'Martinique',
          },
          {
            selected: false,
            tags: [],
            zone: 'Mayotte',
          },
          {
            selected: false,
            tags: [],
            zone: 'Nouvelle Calédonie',
          },
          {
            selected: false,
            tags: [],
            zone: 'Polynésie',
          },
          {
            selected: false,
            tags: [],
            zone: 'Réunion',
          },
          {
            selected: false,
            tags: [],
            zone: 'Saint Pierre et Miquelon',
          },
          {
            selected: false,
            tags: [],
            zone: 'Wallis et Futuna',
          },
        ]);
      });
      test('user has preferences and address', async () => {
        // Given
        const address1 = new Address(
          'Orly',
          '94, Val-de-Marne, Île-de-France',
          '94054_0070_00023',
          '23 Rue des Aubépines 94310 Orly',
          '23 Rue des Aubépines',
          '94310'
        );
        const address2 = new Address(
          'Bastia',
          '2B, Haute-Corse, Corse',
          '2B033',
          'Bastia',
          'Bastia',
          '20200'
        );
        const address3 = new Address(
          'Saint-Denis',
          '974, La Réunion',
          '97411_1060_00002',
          '2 Rue de Paris 97400 Saint-Denis',
          '2 Rue de Paris',
          '97400'
        );
        const address4 = new Address(
          'Arpajon',
          '91, Essonne, Île-de-France',
          '91021',
          'Arpajon',
          'Arpajon',
          '91290'
        );
        const preferences = new Preferences(
          ['Zone A', 'Zone B', 'Zone C'],
          [address1, address2, address4]
        );

        // When
        const result = preferences.getZoneInfos(address3);

        // Then
        expect(result).toEqual([
          {
            selected: true,
            tags: [],
            zone: 'Zone A',
          },
          {
            selected: true,
            tags: [],
            zone: 'Zone B',
          },
          {
            selected: true,
            tags: [
              {
                id: '91021',
                label: 'Arpajon (91)',
                removable: true,
              },
              {
                id: '94054_0070_00023',
                label: 'Orly (94)',
                removable: true,
              },
            ],
            zone: 'Zone C',
          },
          {
            selected: false,
            tags: [
              {
                id: '2B033',
                label: 'Bastia (20)',
                removable: true,
              },
            ],
            zone: 'Corse',
          },
          {
            selected: false,
            tags: [],
            zone: 'Guadeloupe',
          },
          {
            selected: false,
            tags: [],
            zone: 'Guyane',
          },
          {
            selected: false,
            tags: [],
            zone: 'Martinique',
          },
          {
            selected: false,
            tags: [],
            zone: 'Mayotte',
          },
          {
            selected: false,
            tags: [],
            zone: 'Nouvelle Calédonie',
          },
          {
            selected: false,
            tags: [],
            zone: 'Polynésie',
          },
          {
            selected: false,
            tags: [
              {
                id: '97411_1060_00002',
                label: 'Saint-Denis (974) 🏠',
                removable: false,
              },
            ],
            zone: 'Réunion',
          },
          {
            selected: false,
            tags: [],
            zone: 'Saint Pierre et Miquelon',
          },
          {
            selected: false,
            tags: [],
            zone: 'Wallis et Futuna',
          },
        ]);
      });
    });
  });
});
