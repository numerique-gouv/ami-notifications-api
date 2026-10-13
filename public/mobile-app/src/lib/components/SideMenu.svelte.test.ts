import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as AMINavigationMethods from '$lib/ami-navigation';
import SideMenu from './SideMenu.svelte';

describe('/SideMenu.svelte', () => {
  test('should display basic items', async () => {
    // Given
    const entries = [
      {
        url: '/#/checklist',
        title: 'Pendant la grossesse',
        id: 'during-pregnancy',
        isEnabled: true,
      },
      {
        url: '/#/checklist',
        title: 'Après la naissance',
        id: 'after-birth',
        isEnabled: true,
      },
    ];

    // When
    render(SideMenu, { sideMenus: entries });

    // Then
    expect(screen.queryByTestId('sidemenu-button-during-pregnancy')).not.toBeNull();
    expect(screen.queryByTestId('sidemenu-button-after-birth')).not.toBeNull();
  });

  test('should display icon on item', async () => {
    // Given
    const entries = [
      {
        url: '/#/checklist',
        title: 'Pendant la grossesse',
        id: 'during-pregnancy',
        iconClass: 'fr-icon-user-line',
        isEnabled: true,
      },
    ];

    // When
    render(SideMenu, { sideMenus: entries });

    // Then
    expect(screen.queryByTestId('sidemenu-button-during-pregnancy')).toHaveClass(
      'fr-icon-user-line'
    );
  });

  test('should display tag on item', async () => {
    // Given
    const entries = [
      {
        url: '/#/checklist',
        title: 'Pendant la grossesse',
        id: 'during-pregnancy',
        tag: '2/8',
        isEnabled: true,
      },
    ];

    // When
    render(SideMenu, { sideMenus: entries });

    // Then
    expect(screen.queryByTestId('sidemenu-button-during-pregnancy')).toHaveTextContent(
      '2/8'
    );
  });

  test('should redirect on click on button', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const entries = [
      {
        url: '/#/checklist',
        title: 'Pendant la grossesse',
        id: 'during-pregnancy',
        isEnabled: true,
      },
    ];
    render(SideMenu, { sideMenus: entries });

    // When
    await waitFor(async () => {
      const button = screen.getByTestId('sidemenu-button-during-pregnancy');
      await fireEvent.click(button);
    });

    // Then
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('/#/checklist');
  });

  test('should not redirect on click on button as item is not enabled', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const entries = [
      {
        url: '/#/checklist',
        title: 'Pendant la grossesse',
        id: 'during-pregnancy',
        isEnabled: false,
      },
    ];
    render(SideMenu, { sideMenus: entries });

    // When
    await waitFor(async () => {
      const button = screen.getByTestId('sidemenu-button-during-pregnancy');
      await fireEvent.click(button);
    });

    // Then
    expect(spy).toHaveBeenCalledTimes(0);
  });
});
