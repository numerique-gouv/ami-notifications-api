import { describe, expect, test } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/svelte';
import { Item } from '$lib/agenda';
import AgendaItem from './AgendaItem.svelte';

describe('/AgendaItem.svelte', () => {
  test('should have more-icon when agenda item has modal', async () => {
    // Given
    const item = new Item(
      'fake-id-election',
      'election',
      'Elections locales',
      'Inscrivez-vous sur les listes électorales',
      null,
      new Date('2025-12-05'),
      null
    );

    // When
    render(AgendaItem, { props: { item: item, hasModal: true } });

    // Then
    const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-election');
    expect(moreIcon).toBeInTheDocument();
  });
  test('should mark emojis', async () => {
    // Given
    const item = new Item(
      'fake-id-election',
      'election',
      'Elections locales',
      'Inscrivez-vous sur les listes électorales 📆',
      null,
      new Date('2025-12-05'),
      null
    );

    // When
    render(AgendaItem, { props: { item: item } });

    // Then
    expect(document.querySelector('[aria-hidden]')).toBeInTheDocument();
  });
});
