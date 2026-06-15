import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import { Address } from '$lib/address';
import * as citiesFromGeoAPIAndBANMethods from '$lib/citiesFromGeoAPIAndBAN';
import * as matomoMethods from '$lib/matomo';
import { Preferences } from '$lib/state/preferences';
import { userStore } from '$lib/state/User.svelte';
import { mockUserIdentity, mockUserInfo } from '$tests/utils';
import ZonePreferences from './ZonePreferences.svelte';

vi.mock('svelte/transition', () => ({
  slide: () => ({
    duration: 0,
    css: () => '',
  }),
}));

describe('/ZonePreferences.svelte', () => {
  beforeEach(async () => {
    vi.resetAllMocks();
  });

  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
    const onClose = vi.fn();

    // When
    render(ZonePreferences, { props: { onClose } });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });

  test('should display zones according to user preferences', async () => {
    // Given
    await userStore.login(mockUserInfo);
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
              id: 'a',
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
              id: 'b',
              label: 'Bastia (20)',
              removable: true,
            },
          ],
          zone: 'Corse',
        },
      ]);
    const onClose = vi.fn();

    // When
    render(ZonePreferences, { props: { onClose } });

    // Then
    expect(screen.getByText('Paris (75) 🏠')).toBeInTheDocument();
    expect(screen.getByText('Bastia (20)')).toBeInTheDocument();
    expect(spyGetZoneInfos).toHaveBeenCalledTimes(1);
    expect(spyGetZoneInfos).toHaveBeenCalledWith(userStore.connected?.identity.address);
  });

  describe('Zone toggle', () => {
    test('should enable zone when user toggles on', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      const spy = vi.spyOn(Preferences.prototype, 'addZone');
      render(ZonePreferences, { props: { onClose } });

      // When
      const toggleInput = screen.getByTestId('Martinique');
      await fireEvent.click(toggleInput);

      // Then
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

    test('should disable zone when user toggles off', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      const spy = vi.spyOn(Preferences.prototype, 'removeZone');
      render(ZonePreferences, { props: { onClose } });

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

  describe('City input focus', () => {
    test('should hide help text when focus is on city search input', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      render(ZonePreferences, { props: { onClose } });
      await waitFor(() => {
        expect(screen.queryByText(/quelles zones scolaires/i)).toBeInTheDocument();
      });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);

      // Then
      await waitFor(() => {
        expect(screen.queryByText(/quelles zones scolaires/i)).not.toBeInTheDocument();
      });
    });

    test('should hide toggles when focus is on city search input', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      render(ZonePreferences, { props: { onClose } });
      await waitFor(() => {
        expect(screen.queryByText(/zone c/i)).toBeInTheDocument();
      });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);

      // Then
      await waitFor(() => {
        expect(screen.queryByText(/zone c/i)).not.toBeInTheDocument();
      });
    });

    test('should display empty text when focus is on city search input', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      render(ZonePreferences, { props: { onClose } });
      await waitFor(() => {
        expect(
          screen.queryByText(/recherchez une commune pour afficher une zone/i)
        ).not.toBeInTheDocument();
      });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);

      // Then
      await waitFor(() => {
        expect(
          screen.queryByText(/recherchez une commune pour afficher une zone/i)
        ).toBeInTheDocument();
      });
    });

    test('should display back button when focus is on city search input', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      render(ZonePreferences, { props: { onClose } });
      await waitFor(() => {
        expect(screen.queryByTestId('back-button')).toBeNull();
      });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);

      // Then
      await waitFor(() => {
        expect(screen.queryByTestId('back-button')).not.toBeNull();
      });
    });
  });

  describe('City selection', () => {
    test('should display results when user enters a city', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const data = [
        {
          nom: 'Arpajon',
          code: '91021',
          departement: { code: '91', nom: 'Essonne' },
        },
        {
          nom: 'Arpavon',
          code: '26013',
          departement: { code: '26', nom: 'Drôme' },
        },
        {
          nom: 'Saint-Germain-lès-Arpajon',
          code: '91552',
          departement: { code: '91', nom: 'Essonne' },
        },
        {
          nom: 'Arpajon-sur-Cère',
          code: '15012',
          departement: { code: '15', nom: 'Cantal' },
        },
        {
          nom: 'Arpaillargues-et-Aureillac',
          code: '30014',
          departement: { code: '30', nom: 'Gard' },
        },
      ];
      const onClose = vi.fn();
      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          results: data,
        });
      render(ZonePreferences, { props: { onClose } });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('Arpa');
        const autocompleteListItem0 = screen.getByTestId('autocomplete-item-0');
        expect(autocompleteListItem0).toHaveTextContent('Arpajon (91)');
        const autocompleteListItem1 = screen.getByTestId('autocomplete-item-1');
        expect(autocompleteListItem1).toHaveTextContent('Arpavon (26)');
        const autocompleteListItem2 = screen.getByTestId('autocomplete-item-2');
        expect(autocompleteListItem2).toHaveTextContent(
          'Saint-Germain-lès-Arpajon (91)'
        );
        const autocompleteListItem3 = screen.getByTestId('autocomplete-item-3');
        expect(autocompleteListItem3).toHaveTextContent('Arpajon-sur-Cère (15)');
        const autocompleteListItem4 = screen.getByTestId('autocomplete-item-4');
        expect(autocompleteListItem4).toHaveTextContent(
          'Arpaillargues-et-Aureillac (30)'
        );
      });
    });

    test('should update preferences and refresh zones when user clicks on a result', async () => {
      // Given
      const data = [
        {
          nom: 'Arpajon',
          code: '91021',
          departement: { code: '91', nom: 'Essonne' },
        },
      ];
      const address = new Address(
        'Arpajon',
        '91, Essonne, Île-de-France',
        '91021',
        'Arpajon',
        'Arpajon',
        '91290'
      );
      const preferences = new Preferences(['Zone A'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);
      const onClose = vi.fn();
      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          results: data,
        });
      const spy2 = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'cityToBAN')
        .mockResolvedValue({
          address: address,
        });
      const spy3 = vi.spyOn(Preferences.prototype, 'addAddress');
      render(ZonePreferences, { props: { onClose } });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });
      await waitFor(async () => {
        const firstCity = screen.getByTestId('autocomplete-item-button-0');
        await fireEvent.click(firstCity);
      });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('Arpa');
        expect(spy2).toHaveBeenCalledTimes(1);
        expect(spy2).toHaveBeenCalledWith(data[0]);
        expect(screen.queryByText(/quelles zones scolaires/i)).toBeInTheDocument();
        expect(screen.queryByText(/zone c/i)).toBeInTheDocument();
        expect(
          screen.queryByText(/recherchez une commune pour afficher une zone/i)
        ).not.toBeInTheDocument();
        expect(screen.queryByTestId('back-button')).toBeNull();
        expect(screen.getByText('Arpajon (91)')).toBeInTheDocument();
        expect(userStore.connected?.identity.preferences.zones).toEqual([
          'Zone A',
          'Zone C',
        ]);
        expect(userStore.connected?.identity.preferences.addresses).toEqual([address]);
        const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
        expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
        expect(spy3).toHaveBeenCalledWith(address);
      });
    });

    test('should display warning block when Geo API is unavailable', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          errorCode: 'geo-api-unavailable',
          errorMessage: 'Geo API unavailable',
        });
      render(ZonePreferences, { props: { onClose } });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        const cityWarning = screen.getByTestId('city-warning');
        expect(cityWarning).toHaveTextContent(
          'Récupération de la commune indisponible'
        );
        expect(cityWarning).toHaveTextContent(
          'Nous rencontrons des difficultés à trouver votre commune dans notre répertoire. Merci de réessayer plus tard.'
        );
      });
    });

    test('should display warning block when BAN is unavailable', async () => {
      // Given
      const data = [
        {
          nom: 'Arpajon',
          code: '91021',
          departement: { code: '91', nom: 'Essonne' },
        },
      ];
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          results: data,
        });
      const spy2 = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'cityToBAN')
        .mockResolvedValue({
          errorCode: 'ban-unavailable',
          errorMessage: 'BAN unavailable',
        });
      render(ZonePreferences, { props: { onClose } });

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });
      await waitFor(async () => {
        const firstCity = screen.getByTestId('autocomplete-item-button-0');
        await fireEvent.click(firstCity);
      });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy2).toHaveBeenCalledTimes(1);
        const cityWarning = screen.getByTestId('city-warning');
        expect(cityWarning).toHaveTextContent(
          'Récupération de la commune indisponible'
        );
        expect(cityWarning).toHaveTextContent(
          'Nous rencontrons des difficultés à trouver votre commune dans notre répertoire. Merci de réessayer plus tard.'
        );
      });
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
      const onClose = vi.fn();
      const spy = vi.spyOn(Preferences.prototype, 'removeAddress');
      render(ZonePreferences, { props: { onClose } });
      await waitFor(async () => {
        expect(screen.getByText('Arpajon (91)')).toBeInTheDocument();

        // When
        const tag = screen.getByTestId(address.idBAN);
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
      const onClose = vi.fn();
      const spy = vi.spyOn(Preferences.prototype, 'clearAddresses');
      render(ZonePreferences, { props: { onClose } });
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
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      const trackZoneCountSpy = vi
        .spyOn(matomoMethods, 'trackZoneCount')
        .mockResolvedValue(undefined);
      const { unmount } = render(ZonePreferences, { props: { onClose } });

      // When
      unmount();

      // Then
      expect(trackZoneCountSpy).toHaveBeenCalledTimes(0);
    });
    test('should not track zones count', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const onClose = vi.fn();
      const trackZoneCountSpy = vi
        .spyOn(matomoMethods, 'trackZoneCount')
        .mockResolvedValue(undefined);
      const { unmount } = render(ZonePreferences, { props: { onClose } });

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
