import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/svelte';
import Navigation from './Navigation.svelte';

describe('/Navigation.svelte', () => {
  test('should highlight nothing', async () => {
    // Given
    const { container } = render(Navigation);

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toBeNull();
  });

  test('should highlight home item', async () => {
    // Given
    const { container } = render(Navigation, { currentItem: 'home' });

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toHaveTextContent('Accueil');
  });

  test('should highlight agenda item', async () => {
    // Given
    const { container } = render(Navigation, { currentItem: 'agenda' });

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toHaveTextContent('Agenda');
  });
});
