import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
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

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page);
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  test('should navigate to previous page when user clicks on Close button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const backSpy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());

    // When
    render(Page);
    const closeButton = screen.getByTestId('close-button');
    await fireEvent.click(closeButton);

    // Then
    expect(backSpy).toHaveBeenCalledTimes(1);
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });
});
