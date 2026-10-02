import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { Address } from '$lib/address';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as citiesFromGeoAPIAndBANMethods from '$lib/citiesFromGeoAPIAndBAN';
import { Preferences } from '$lib/state/preferences';
import { userStore } from '$lib/state/User.svelte';
import { mockUserIdentity } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(async () => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  describe('City selection', () => {
    test('should display results when user enters a city', async () => {
      // Given
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

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
      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          results: data,
        });
      render(Page);

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });

      // Then
      vi.advanceTimersByTime(750);
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

    test('should update preferences when user clicks on a result', async () => {
      // Given
      const preferences = new Preferences(['Zone A'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const data = [
        {
          nom: 'Arpajon',
          code: '91021',
          departement: { code: '91', nom: 'Essonne' },
        },
      ];
      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          results: data,
        });
      const address = new Address(
        'Arpajon',
        '91, Essonne, Île-de-France',
        '91021',
        'Arpajon',
        'Arpajon',
        '91290'
      );
      const spy2 = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'cityToBAN')
        .mockResolvedValue({
          address: address,
        });
      const spy3 = vi.spyOn(Preferences.prototype, 'addAddress');
      render(Page);

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });
      vi.advanceTimersByTime(750);
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
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi
        .spyOn(citiesFromGeoAPIAndBANMethods, 'callGeoAPI')
        .mockResolvedValue({
          errorCode: 'geo-api-unavailable',
          errorMessage: 'Geo API unavailable',
        });
      render(Page);

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });

      // Then
      vi.advanceTimersByTime(750);
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
      const preferences = new Preferences(['Zone A', 'Zone B', 'Zone C', 'Corse'], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const data = [
        {
          nom: 'Arpajon',
          code: '91021',
          departement: { code: '91', nom: 'Essonne' },
        },
      ];
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
      render(Page);

      // When
      const cityInput = screen.getByTestId('city-input');
      await fireEvent.focus(cityInput);
      await fireEvent.input(cityInput, {
        target: { value: 'Arpa' },
      });
      vi.advanceTimersByTime(750);
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
});
