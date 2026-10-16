import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import * as bannerMethods from '$lib/banner';
import Banner from './Banner.svelte';

describe('/Banner.svelte', () => {
  test('should display banner as banner is not hidden', async () => {
    // Given
    const spy = vi.spyOn(bannerMethods, 'isBannerHidden').mockReturnValue(false);

    // When
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
    });

    await waitFor(async () => {
      expect(screen.queryByTestId('banner-id1')).not.toBeNull();
      expect(spy).toHaveBeenCalledWith('id1');
    });
  });
  test('should not display banner as banner is hidden', async () => {
    // Given
    const spy = vi.spyOn(bannerMethods, 'isBannerHidden').mockReturnValue(true);

    // When
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
    });

    await waitFor(async () => {
      expect(screen.queryByTestId('banner-id1')).toBeNull();
      expect(spy).toHaveBeenCalledWith('id1');
    });
  });
  test('should hide banner when user clicks on close button', async () => {
    // Given
    vi.spyOn(bannerMethods, 'isBannerHidden').mockReturnValue(false);
    const spy = vi.spyOn(bannerMethods, 'hideBanner').mockReturnValue();
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
    });

    // When
    await waitFor(async () => {
      const closeButton = screen.getByTestId('banner-id1-close-button');
      await fireEvent.click(closeButton);
    });

    // Then
    expect(spy).toHaveBeenCalledWith('id1');
  });
  test('should not have a close button when option is false', async () => {
    // Given
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
      closeButton: 'false',
    });

    // Then
    expect(screen.queryByTestId('banner-id1-close-button')).toBeNull();
  });
  test('should not have a link button when link is not set', async () => {
    // Given
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
      closeButton: 'false',
    });

    // Then
    expect(screen.queryByTestId('banner-id1-link-button')).toBeNull();
  });
  test('should have a link button when link is set', async () => {
    // Given
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
      closeButton: 'false',
      link: 'url1',
    });

    // Then
    const linkButton = screen.getByTestId('banner-id1-link-button');
    expect(linkButton).toHaveTextContent('url');
  });
  test('should have a link button when link is set - with a label', async () => {
    // Given
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
      closeButton: 'false',
      link: 'url1',
      linkLabel: 'label1',
    });

    // Then
    const linkButton = screen.getByTestId('banner-id1-link-button');
    expect(linkButton).toHaveTextContent('label1');
  });
  test('should call AMIGoto on link button click', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
      closeButton: 'false',
      link: 'url1',
    });

    // When
    await waitFor(async () => {
      const linkButton = screen.getByTestId('banner-id1-link-button');
      await fireEvent.click(linkButton);
    });

    // Then
    expect(spy).toHaveBeenCalledWith('url1', false);
  });
  test('should call AMIGoto on link button click - with silent login', async () => {
    // Given
    const spy = vi
      .spyOn(AMINavigationMethods, 'AMIGoto')
      .mockImplementation(() => Promise.resolve());
    render(Banner, {
      id: 'id1',
      title: 'Modification non transmise',
      description: 'La modification ne sera pas transmise',
      bannerType: 'info',
      closeButton: 'false',
      link: 'url1',
      linkSilentLogin: true,
    });

    // When
    await waitFor(async () => {
      const linkButton = screen.getByTestId('banner-id1-link-button');
      await fireEvent.click(linkButton);
    });

    // Then
    expect(spy).toHaveBeenCalledWith('url1', true);
  });
});
