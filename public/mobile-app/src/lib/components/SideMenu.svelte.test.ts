import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/svelte';
import SideMenu from './SideMenu.svelte';

describe('/SideMenu.svelte', () => {
  test('should display basic items', async () => {
    // Given
    const entries = [
      {
        url: '/#/checklist',
        title: 'Pendant la grossesse',
        id: 'during-pregnancy',
      },
      {
        url: '/#/checklist',
        title: 'Après la naissance',
        id: 'after-birth',
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
      },
    ];

    // When
    render(SideMenu, { sideMenus: entries });

    // Then
    expect(screen.queryByTestId('sidemenu-button-during-pregnancy')).toHaveTextContent(
      '2/8'
    );
  });
});
