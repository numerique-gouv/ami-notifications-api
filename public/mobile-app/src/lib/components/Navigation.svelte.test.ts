import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render } from '@testing-library/svelte';
import * as envModule from '$env/static/public';
import Navigation from './Navigation.svelte';

describe('/Navigation.svelte', () => {
  beforeEach(async () => {
    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
      });
    });
  });
  afterEach(() => {
    vi.resetAllMocks();
  });

  test('should highlight nothing', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'true';
    const { container } = render(Navigation);

    // Then
    expect(container).toHaveTextContent('Accueil');
    expect(container).toHaveTextContent('Agenda');
    expect(container).toHaveTextContent('Services');
    expect(container).toHaveTextContent('Suivi');
    const highlight = container.querySelector('.highlight');
    expect(highlight).toBeNull();
  });

  test('should highlight nothing - no services', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'false';
    const { container } = render(Navigation);

    // Then
    expect(container).toHaveTextContent('Accueil');
    expect(container).toHaveTextContent('Agenda');
    expect(container).not.toHaveTextContent('Services');
    expect(container).toHaveTextContent('Suivi');
    const highlight = container.querySelector('.highlight');
    expect(highlight).toBeNull();
  });

  test('should highlight home item', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'true';
    const { container } = render(Navigation, { currentItem: 'home' });

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toHaveTextContent('Accueil');
  });

  test('should highlight agenda item', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'true';
    const { container } = render(Navigation, { currentItem: 'agenda' });

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toHaveTextContent('Agenda');
  });

  test('should highlight services item', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'true';
    const { container } = render(Navigation, { currentItem: 'services' });

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toHaveTextContent('Services');
  });

  test('should highlight followup item', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATURE_FLAG_SERVICES_ENABLED = 'true';
    const { container } = render(Navigation, { currentItem: 'followup' });

    // Then
    const highlight = container.querySelector('.highlight');
    expect(highlight).toHaveTextContent('Suivi');
  });
});
