import { render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as APIAnnuaireSPMethods from '$lib/api-annuaire-sp';
import { userStore } from '$lib/state/User.svelte';
import {
  mockUserIdentity,
  mockUserIdentityWithPreferredUsername,
  mockUserInfo,
  mockUserInfoWithPreferredUsername,
} from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  beforeEach(() => {
    vi.spyOn(APIAnnuaireSPMethods, 'retrieveMairie').mockResolvedValue(null);
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

  test('mairie entry is disabled as user has no address', async () => {
    // Given
    const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
    newMockUserIdentity.address = undefined;
    localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
    await userStore.login(mockUserInfo);
    const spy = vi
      .spyOn(APIAnnuaireSPMethods, 'retrieveMairie')
      .mockResolvedValue(null);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const item = screen.getByTestId('sidemenu-item-city');
      expect(item).toHaveClass('disabled');
      expect(spy).not.toHaveBeenCalled();
    });
  });

  test('mairie entry is disabled as user has address but mairie is not found', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
    await userStore.login(mockUserInfo);
    const spy = vi
      .spyOn(APIAnnuaireSPMethods, 'retrieveMairie')
      .mockResolvedValue(null);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const item = screen.getByTestId('sidemenu-item-city');
      expect(item).toHaveClass('disabled');
      expect(spy).toHaveBeenCalledWith(userStore.connected?.identity.address?.citycode);
    });
  });

  test('mairie entry is enabled as user has address and mairie is found', async () => {
    // Given
    localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
    await userStore.login(mockUserInfo);
    const spy = vi
      .spyOn(APIAnnuaireSPMethods, 'retrieveMairie')
      .mockResolvedValue({ url_service_public: 'url1' });

    // When
    render(Page);

    // Then
    await waitFor(() => {
      const item = screen.getByTestId('sidemenu-item-city');
      expect(item).not.toHaveClass('disabled');
      expect(spy).toHaveBeenCalledWith(userStore.connected?.identity.address?.citycode);
    });
  });
});
