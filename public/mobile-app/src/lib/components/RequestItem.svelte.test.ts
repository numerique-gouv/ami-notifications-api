import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/svelte';
import { RequestItem as Item } from '$lib/follow-up';
import RequestItem from './RequestItem.svelte';

describe('/RequestItem.svelte', () => {
  test('should display a link', async () => {
    // Given
    const item = new Item(
      'id',
      'notifications',
      'Opération Tranquillité Vacances',
      'Votre demande est terminée.',
      new Date('2026-02-20T15:55:00.000Z'),
      'closed',
      'Terminée',
      false,
      'url'
    );
    const onOpen = vi.fn();
    render(RequestItem, { props: { item: item, onOpen: onOpen } });

    // When
    const link = screen.getByTestId('request-item-link');

    // Then
    expect(link.getAttribute('href')).toBe('url');
    expect(link).not.toHaveClass('no-link');
  });
  test('should not display a link', async () => {
    // Given
    const item = new Item(
      'id',
      'notifications',
      'Opération Tranquillité Vacances',
      'Votre demande est terminée.',
      new Date('2026-02-20T15:55:00.000Z'),
      'closed',
      'Terminée',
      false,
      null
    );
    const onOpen = vi.fn();
    render(RequestItem, { props: { item: item, onOpen: onOpen } });

    // When
    const link = screen.getByTestId('request-item-link');

    // Then
    expect(link.getAttribute('href')).toBe(null);
    expect(link).toHaveClass('no-link');
  });
});
