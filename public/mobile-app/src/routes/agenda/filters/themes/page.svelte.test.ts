import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import { THEMES } from '$lib/agenda';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { Preferences } from '$lib/state/preferences';
import { userStore } from '$lib/state/User.svelte';
import { mockUserIdentity } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
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
  describe('should display themes according to user preferences', async () => {
    test('no theme in preferences', async () => {
      // Given
      const preferences = new Preferences([], [], []);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      // When
      render(Page);

      // Then
      THEMES.forEach((t) => {
        const input: HTMLInputElement = screen.getByTestId(t.id);
        expect(input.checked).toBeFalsy();
      });
    });
    test('with themes in preferences', async () => {
      // Given
      const preferences = new Preferences([], [], ['school-holiday', 'other']);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      // When
      render(Page);

      // Then
      THEMES.forEach((t) => {
        const input: HTMLInputElement = screen.getByTestId(t.id);
        if (['school-holiday', 'other'].includes(t.id)) {
          expect(input.checked).toBeTruthy();
        } else {
          expect(input.checked).toBeFalsy();
        }
      });
    });
  });
  describe('Theme toggle', () => {
    test('should enable theme when user toggles on', async () => {
      // Given
      const preferences = new Preferences([], [], ['school-holiday', 'other']);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'addTheme');
      render(Page);

      // When
      const input = screen.getByTestId('citizenship');
      await fireEvent.click(input);

      // Then
      expect(userStore.connected?.identity.preferences.themes).toEqual([
        'school-holiday',
        'other',
        'citizenship',
      ]);
      const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
      expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
      expect(spy).toHaveBeenCalledWith('citizenship');
    });
    test('should disable theme when user toggles off', async () => {
      // Given
      const preferences = new Preferences([], [], ['school-holiday', 'other']);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'removeTheme');
      render(Page);

      // When
      const input = screen.getByTestId('other');
      await fireEvent.click(input);

      // Then
      expect(userStore.connected?.identity.preferences.themes).toEqual([
        'school-holiday',
      ]);
      const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
      expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
      expect(spy).toHaveBeenCalledWith('other');
    });
  });
  describe('Clear action', () => {
    test('should clear themes in preferences', async () => {
      // Given
      const preferences = new Preferences([], [], ['school-holiday', 'other']);
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.preferences = preferences;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(newMockUserIdentity);

      const spy = vi.spyOn(Preferences.prototype, 'clearThemes');
      render(Page);

      // When
      const button = screen.getByTestId('clear-themes');
      await fireEvent.click(button);

      // Then
      expect(userStore.connected?.identity.preferences.themes).toEqual([]);
      const parsed = JSON.parse(localStorage.getItem('user_identity') || '{}');
      expect(parsed?.preferences).toEqual(userStore.connected?.identity.preferences);
      expect(spy).toHaveBeenCalledWith();
    });
  });
});
