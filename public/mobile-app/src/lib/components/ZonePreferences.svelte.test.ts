import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { Address } from '$lib/address';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as matomoMethods from '$lib/matomo';
import { Preferences } from '$lib/state/preferences';
import { userStore } from '$lib/state/User.svelte';
import { mockUserIdentity } from '$tests/utils';
import ZonePreferences from './ZonePreferences.svelte';

describe('/ZonePreferences.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(ZonePreferences, {
      props: { fromPage: 'preferences' },
    });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('should display zones according to user preferences', async () => {
    // Given
    const preferences = new Preferences([], []);
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
    newMockUserIdentity.preferences = preferences;
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
    await userStore.login(newMockUserIdentity);

    const spyGetZoneInfos = vi
      .spyOn(Preferences.prototype, 'getZoneInfos')
      .mockReturnValueOnce([
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
              id: 'user-address-a',
              label: 'Paris (75) 🏠',
              removable: false,
            },
          ],
          zone: 'Zone C',
        },
        {
          selected: false,
          tags: [
            {
              id: 'city-b',
              label: 'Bastia (20)',
              removable: true,
            },
          ],
          zone: 'Corse',
        },
      ]);

    // When
    render(ZonePreferences, {
      props: { fromPage: 'preferences' },
    });

    // Then
    await waitFor(async () => {
      expect(screen.getByText('Paris (75)')).toBeInTheDocument();
      expect(screen.getByText('🏠')).toBeInTheDocument();
      expect(document.querySelectorAll('[aria-hidden]').length).toEqual(1);
      expect(screen.getByText('Bastia (20)')).toBeInTheDocument();
      expect(spyGetZoneInfos).toHaveBeenCalledTimes(1);
      expect(spyGetZoneInfos).toHaveBeenCalledWith(
        userStore.connected?.identity.address
      );
    });
  });

  describe('Zone toggle', () => {
    test('should enable zone when user toggles on', async () => {
      // Given
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'addZone');
      render(ZonePreferences, {
        props: { fromPage: 'preferences' },
      });

      // When
      const toggleInput = screen.getByTestId('Martinique');
      await fireEvent.click(toggleInput);

      // Then
      await waitFor(async () => {
        expect(userStore.connected?.identity.preferences.zones).toEqual([
          'Zone A',
          'Zone B',
          'Zone C',
          'Corse',
          'Martinique',
        ]);
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
        expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
        expect(spy).toHaveBeenCalledWith('Martinique');
      });
    });

    test('should disable zone when user toggles off', async () => {
      // Given
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'removeZone');
      render(ZonePreferences, {
        props: { fromPage: 'preferences' },
      });

      // When
      const toggleInput = screen.getByTestId('Zone C');
      await fireEvent.click(toggleInput);

      // Then
      expect(userStore.connected?.identity.preferences.zones).toEqual([
        'Zone A',
        'Zone B',
        'Corse',
      ]);
      const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
      expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
      expect(spy).toHaveBeenCalledWith('Zone C');
    });
  });

  describe('City remove action', () => {
    test('should remove address in preferences', async () => {
      // Given
      const address = new Address(
        'Arpajon',
        '91, Essonne, Île-de-France',
        '91021',
        'Arpajon',
        'Arpajon',
        '91290'
      );
      const preferences = new Preferences(['Zone C'], [address]);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'removeAddress');
      render(ZonePreferences, {
        props: { fromPage: 'preferences' },
      });
      await waitFor(async () => {
        expect(screen.getByText('Arpajon (91)')).toBeInTheDocument();

        // When
        const tag = screen.getByTestId(`city-${address.idBAN}`);
        await fireEvent.click(tag);
      });

      // Then
      await waitFor(() => {
        expect(screen.queryByText('Arpajon (91)')).not.toBeInTheDocument();
        expect(userStore.connected?.identity.preferences.zones).toEqual(['Zone C']);
        expect(userStore.connected?.identity.preferences.addresses).toEqual([]);
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
        expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
        expect(spy).toHaveBeenCalledWith(address);
      });
    });
  });

  describe('City clear action', () => {
    test('should clear addresses in preferences', async () => {
      // Given
      const address = new Address(
        'Arpajon',
        '91, Essonne, Île-de-France',
        '91021',
        'Arpajon',
        'Arpajon',
        '91290'
      );
      const preferences = new Preferences(['Zone C'], [address]);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'clearAddresses');
      render(ZonePreferences, {
        props: { fromPage: 'preferences' },
      });
      await waitFor(async () => {
        expect(screen.getByText('Arpajon (91)')).toBeInTheDocument();

        // When
        const button = screen.getByTestId('clear-addresses');
        await fireEvent.click(button);
      });

      // Then
      await waitFor(() => {
        expect(screen.queryByText('Arpajon (91)')).not.toBeInTheDocument();
        expect(userStore.connected?.identity.preferences.zones).toEqual(['Zone C']);
        expect(userStore.connected?.identity.preferences.addresses).toEqual([]);
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
        expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
        expect(spy).toHaveBeenCalledWith();
      });
    });
  });

  describe('Zones tracking on unmount', () => {
    test('should not track zones count has there is no change', async () => {
      // Given
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const trackZoneCountSpy = vi
        .spyOn(matomoMethods, 'trackZoneCount')
        .mockResolvedValue(undefined);
      const { unmount } = render(ZonePreferences, {
        props: { fromPage: 'preferences' },
      });

      // When
      unmount();

      // Then
      expect(trackZoneCountSpy).toHaveBeenCalledTimes(0);
    });
    test('should not track zones count', async () => {
      // Given
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const trackZoneCountSpy = vi
        .spyOn(matomoMethods, 'trackZoneCount')
        .mockResolvedValue(undefined);
      const { unmount } = render(ZonePreferences, {
        props: { fromPage: 'preferences' },
      });

      // When
      const toggleInputMartinique = screen.getByTestId('Martinique');
      await fireEvent.click(toggleInputMartinique); // add
      const toggleInputZoneC = screen.getByTestId('Zone C');
      await fireEvent.click(toggleInputZoneC); // remove

      unmount();

      // Then
      expect(userStore.connected?.identity.preferences.zones).toEqual([
        'Zone A',
        'Zone B',
        'Corse',
        'Martinique',
      ]);
      expect(trackZoneCountSpy).toHaveBeenCalledTimes(1);
      expect(trackZoneCountSpy).toHaveBeenCalledWith(4);
    });
  });
});
