import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import { Preferences } from '$lib/state/preferences';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import ZonePreferences from './ZonePreferences.svelte';

describe('/ZonePreferences.svelte', () => {
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

  test('should enable zone when user toggles on', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const onClose = vi.fn();
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
  });

  test('should disable zone when user toggles off', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const onClose = vi.fn();
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
  });
});
