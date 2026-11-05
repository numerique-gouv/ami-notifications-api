import { render } from '@testing-library/svelte';
import { afterEach, describe, expect, test, vi } from 'vitest';
import AgendaSkeleton from './AgendaSkeleton.svelte';

describe('/AgendaSkeleton.svelte', () => {
  afterEach(() => {
    // restoring date after each test run
    vi.useRealTimers();
  });

  test('should display skeleton', async () => {
    // Given
    const date = new Date(2026, 9, 13, 13); // (9 = October)
    vi.setSystemTime(date);

    // When
    render(AgendaSkeleton);

    // Then
    expect(document.querySelector('.skeleton')).not.toBeNull();

    expect(
      [...document.querySelectorAll('.current .agenda--events--month')].map(
        (e) => e.textContent
      )
    ).toEqual(['Octobre', 'Novembre']);
    expect(
      [...document.querySelectorAll('.future .agenda--events--month')].map(
        (e) => e.textContent
      )
    ).toEqual(['Décembre', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai']);
  });
  test('should display skeleton with a single current month on 1st', async () => {
    // Given
    const date = new Date(2026, 9, 1, 13); // (9 = October)
    vi.setSystemTime(date);

    // When
    render(AgendaSkeleton);

    // Then
    expect(document.querySelector('.skeleton')).not.toBeNull();

    expect(
      [...document.querySelectorAll('.current .agenda--events--month')].map(
        (e) => e.textContent
      )
    ).toEqual(['Octobre']);
    expect(
      [...document.querySelectorAll('.future .agenda--events--month')].map(
        (e) => e.textContent
      )
    ).toEqual(['Novembre', 'Décembre', 'Janvier', 'Février', 'Mars', 'Avril']);
  });
});
