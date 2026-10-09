import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { userStore } from '$lib/state/User.svelte';
import {
  mockUserIdentity,
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
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
    newMockUserIdentity.dataDetails.preferred_username.origin = 'france-connect';
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
    await userStore.login(mockUserInfo);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const profile = screen.getByTestId('profile');
      const profileIdentity = profile.querySelector('#profile-identity');
      expect(profileIdentity).toHaveTextContent('Angela Claire Louise DUBOIS,');
      expect(profileIdentity).toHaveTextContent('née le 24/08/1962');
      expect(profileIdentity).toHaveTextContent(
        'Informations fournies par FranceConnect'
      );
    });
  });

  test('profile page displays the proper user info - with preferred username', async () => {
    // Given
    localStorage.setItem(
      'user_identity',
      JSON.stringify(mockUserIdentityWithPreferredUsername)
    );
    await userStore.login(mockUserInfoWithPreferredUsername);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const profile = screen.getByTestId('profile');
      const profileIdentity = profile.querySelector('#profile-identity');
      expect(profileIdentity).toHaveTextContent('Pierre DUBOIS,');
      expect(profileIdentity).toHaveTextContent('né MERCIER le 17/03/1969');
      expect(profileIdentity).toHaveTextContent(
        'Informations fournies par FranceConnect'
      );
    });
  });

  test('should navigate to the preferred username page when user clicks on "Modifier" button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    render(Page);

    // When
    const button = screen.getByTestId('preferred-username-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenNthCalledWith(
        1,
        '/#/profile/identity/edit-preferred-username'
      );
    });
  });
});
