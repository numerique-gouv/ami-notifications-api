import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/svelte';
import { RequestItem as Item } from '$lib/follow-up';
import RequestItem from './RequestItem.svelte';

describe('/AgendaItem.svelte', () => {
  test('should display a link', async () => {
    // Given
    const item = new Item(
      'Opération Tranquillité Vacances',
      'Votre demande est terminée.',
      new Date('2026-02-20T15:55:00.000Z'),
      null,
      'closed',
      'Terminée',
      'url'
    );
    render(RequestItem, { props: { item: item } });

    // When
    const link = screen.getByTestId('request-item-link');

    // Then
    expect(link.getAttribute('href')).toBe('url');
    expect(link).not.toHaveClass('no-link');
  });
  test('should not display a link', async () => {
    // Given
    const item = new Item(
      'Opération Tranquillité Vacances',
      'Votre demande est terminée.',
      new Date('2026-02-20T15:55:00.000Z'),
      null,
      'closed',
      'Terminée',
      null
    );
    render(RequestItem, { props: { item: item } });

    // When
    const link = screen.getByTestId('request-item-link');

    // Then
    expect(link.getAttribute('href')).toBe(null);
    expect(link).toHaveClass('no-link');
  });
});
