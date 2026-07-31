import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as nativeInfosMethods from '$lib/bridges/nativeInfos';
import { expectBackButtonPresent } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user do not have to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(0);
    });
  });

  test('should import NavWithBackButton component', async () => {
    // When
    render(Page);
    const backButton = screen.getByTestId('back-button');

    // Then
    expect(backButton).toBeInTheDocument();
    expect(screen.getByText('Nous contacter')).toBeInTheDocument();
  });

  test('should render a Back button', async () => {
    // When
    render(Page);

    // Then
    expectBackButtonPresent(screen);
  });

  test('should display contact links', async () => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();

    // When
    render(Page);

    // Then
    const contactUsButton = screen.getByTestId('contact-us-button');
    expect(screen.queryByTestId('contact-us-link-url')).not.toBeInTheDocument();
    await waitFor(() => {
      contactUsButton.click();
      // now the popup is open
      expect(screen.queryByTestId('contact-us-link-url')).toBeInTheDocument();
      expect(screen.queryByTestId('contact-us-link-email')).toBeInTheDocument();
    });
  });

  test('should display plateform infos', async () => {
    vi.spyOn(nativeInfosMethods, 'getPlatform').mockReturnValue('android');
    vi.spyOn(nativeInfosMethods, 'getVersion').mockReturnValue('0.5');
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();

    // When
    render(Page);

    // Then
    const contactUsButton = screen.getByTestId('contact-us-button');
    expect(screen.queryByTestId('contact-us-link-url')).not.toBeInTheDocument();
    await waitFor(() => {
      contactUsButton.click();
      // now the popup is open
      expect(screen.queryByTestId('native-infos')).toHaveTextContent('android - 0.5');
    });
  });
});
