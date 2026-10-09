import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { userStore } from '$lib/state/User.svelte';
import {
  mockUserIdentityWithPreferredUsername,
  mockUserInfo,
  mockUserInfoWithPreferredUsername,
} from '$tests/utils';
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

  test('profile page displays the proper user info', async () => {
    // Given
    await userStore.login(mockUserInfo);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const initial = screen.getByTestId('initial');
      expect(initial).toHaveTextContent('A');
      const fullName = screen.getByTestId('fullname');
      expect(fullName).toHaveTextContent('Angela Claire Louise DUBOIS');
    });
  });

  test('profile page displays the proper user info - with preferred username and email', async () => {
    // Given
    localStorage.setItem(
      'user_identity',
      JSON.stringify(mockUserIdentityWithPreferredUsername)
    );
    await userStore.login(mockUserInfoWithPreferredUsername);
    expect(userStore.connected).not.toBeNull();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const initial = screen.getByTestId('initial');
      expect(initial).toHaveTextContent('P');
      const fullName = screen.getByTestId('fullname');
      expect(fullName).toHaveTextContent('Pierre DUBOIS');
    });
  });
});
