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

  describe('email', async () => {
    test('profile page displays the proper user info', async () => {
      // Given
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.dataDetails.email.origin = 'france-connect';
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(mockUserInfo);

      // When
      render(Page);

      // Then
      await waitFor(() => {
        const profile = screen.getByTestId('profile');
        const profileEmail = profile.querySelector('#profile-email');
        expect(profileEmail).toHaveTextContent('wossewodda-3728@yopmail.com');
        expect(profileEmail).toHaveTextContent(
          'Informations fournies par FranceConnect'
        );
      });
    });

    test('profile page displays the proper user info - with preferred email', async () => {
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
        const profileEmail = profile.querySelector('#profile-email');
        expect(profileEmail).toHaveTextContent('some-other@email.com');
        expect(profileEmail).not.toHaveTextContent(
          'Informations fournies par FranceConnect'
        );
      });
    });

    test('should navigate to the email page when user clicks on "Modifier" button', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());
      render(Page);

      // When
      const button = screen.getByTestId('email-button');
      await fireEvent.click(button);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenNthCalledWith(1, '/#/profile/addresses/edit-email');
      });
    });
  });

  describe('address', async () => {
    test("profile page doesn't display user address", async () => {
      // Given
      await userStore.login(mockUserInfo);

      // Then
      render(Page);

      // When
      await waitFor(() => {
        const profile = screen.getByTestId('profile');
        const profileAddress = profile.querySelector('#profile-address');
        expect(profileAddress).toHaveTextContent('Définir une adresse');
      });
    });

    test('profile page displays user address - from user', async () => {
      // Given
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      await userStore.login(mockUserInfo);

      // When
      render(Page);

      // Then
      await waitFor(() => {
        const profile = screen.getByTestId('profile');
        const profileAddress = profile.querySelector('#profile-address');
        expect(profileAddress).toHaveTextContent(
          'Votre résidence principale Avenue de Ségur 75007 Paris'
        );
        expect(profileAddress).not.toHaveTextContent(
          'Informations fournies par la Caf'
        );
      });
    });

    test('profile page displays user address - from api-particulier', async () => {
      // Given
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.dataDetails.address.origin = 'api-particulier';
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
      await userStore.login(mockUserInfo);

      // When
      render(Page);

      // Then
      await waitFor(() => {
        const profile = screen.getByTestId('profile');
        const profileAddress = profile.querySelector('#profile-address');
        expect(profileAddress).toHaveTextContent(
          'Votre résidence principale Avenue de Ségur 75007 Paris'
        );
        expect(profileAddress).toHaveTextContent('Informations fournies par la Caf');
      });
    });

    test('should navigate to the Address page when user clicks on "Définir une adresse" button', async () => {
      // Given
      await userStore.login(mockUserInfo);
      const spy = vi
        .spyOn(AMINavigationMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());
      render(Page);

      // When
      const button = screen.getByTestId('address-button');
      await fireEvent.click(button);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenNthCalledWith(1, '/#/profile/addresses/edit-address');
      });
    });
  });
});
