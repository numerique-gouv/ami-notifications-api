import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
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
      const closeButton = screen.getByTestId('close-button');
      await fireEvent.click(closeButton);
    });

    // Then
    expect(spy).toHaveBeenCalledWith('id1');
  });
});
