import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as APIAnnuaireSPMethods from '$lib/api-annuaire-sp';
import { userStore } from '$lib/state/User.svelte';
import { mockUserIdentity, mockUserInfo } from '$tests/utils';
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

  describe('when user has no address', () => {
    test('edit-address button is displayed', async () => {
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
        const item = screen.getByTestId('address-button');
        expect(item).toHaveTextContent('Renseigner votre adresse');
        expect(spy).not.toHaveBeenCalled();
      });
    });

    test('should navigate to the edit-address page when user clicks on "Renseigner votre adresse" button', async () => {
      // Given
      const newMockUserIdentity = JSON.parse(JSON.stringify(mockUserIdentity));
      newMockUserIdentity.address = undefined;
      localStorage.setItem('user_identity', JSON.stringify(newMockUserIdentity));
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

  describe('when user has address but mairie is not found', () => {
    test('edit-address button is displayed', async () => {
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
        const item = screen.getByTestId('address-button');
        expect(item).toHaveTextContent('Renseigner votre adresse');
        expect(spy).toHaveBeenCalledWith(
          userStore.connected?.identity.address?.citycode
        );
      });
    });

    test('should navigate to the edit-address page when user clicks on "Renseigner votre adresse" button', async () => {
      // Given
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      await userStore.login(mockUserInfo);
      vi.spyOn(APIAnnuaireSPMethods, 'retrieveMairie').mockResolvedValue(null);
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

  describe('when user has address and mairie is found', () => {
    test('mairie is displayed', async () => {
      // Given
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      await userStore.login(mockUserInfo);
      const spy = vi
        .spyOn(APIAnnuaireSPMethods, 'retrieveMairie')
        .mockResolvedValue({ nom: 'mairie 1', url_service_public: 'url1' });

      // When
      render(Page);

      // Then
      await waitFor(() => {
        const item = screen.getByTestId('ma-commune');
        expect(item).toHaveTextContent('mairie 1');
        expect(spy).toHaveBeenCalledWith(
          userStore.connected?.identity.address?.citycode
        );
      });
    });

    test('should navigate to the mairie page when user clicks on mairie-button', async () => {
      // Given
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      await userStore.login(mockUserInfo);
      vi.spyOn(APIAnnuaireSPMethods, 'retrieveMairie').mockResolvedValue({
        nom: 'mairie 1',
        url_service_public: 'url1',
      });
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

    test('edit-address button is not displayed', async () => {
      // Given
      localStorage.setItem('user_identity', JSON.stringify(mockUserIdentity));
      await userStore.login(mockUserInfo);
      vi.spyOn(APIAnnuaireSPMethods, 'retrieveMairie').mockResolvedValue({
        nom: 'mairie 1',
        url_service_public: 'url1',
      });

      // When
      render(Page);

      // Then
      await waitFor(() => {
        const item = screen.getByTestId('ma-commune');
        expect(item).not.toHaveTextContent('Renseigner votre adresse');
      });
    });
  });
});
