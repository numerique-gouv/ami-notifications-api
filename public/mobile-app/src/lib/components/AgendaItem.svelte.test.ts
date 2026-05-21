import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { Item } from '$lib/agenda';
import AgendaItem from './AgendaItem.svelte';

describe('/AgendaItem.svelte', () => {
  test('should add date to url params', async () => {
    // Given
    const item = new Item(
      'fake-id-otv',
      'otv',
      'Opération Tranquillité Vacances 🏠',
      'Inscrivez-vous pour protéger votre domicile pendant votre absence',
      null,
      new Date('2025-12-05'),
      null
    );
    const onOpen = vi.fn();
    render(AgendaItem, { props: { item: item, onOpen: onOpen } });

    // When
    const link = screen.getByTestId('agenda-item-link');

    // Then
    expect(link.getAttribute('href')).toBe('/#/procedure?date=2025-12-05');
  });

  test('should call onOpen when clicks on more icon', async () => {
    // Given
    const item = new Item(
      'fake-id-otv',
      'otv',
      'Opération Tranquillité Vacances 🏠',
      'Inscrivez-vous pour protéger votre domicile pendant votre absence',
      null,
      new Date('2025-12-05'),
      null
    );
    const onOpen = vi.fn();
    render(AgendaItem, { props: { item: item, onOpen: onOpen } });

    // When
    await waitFor(async () => {
      const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-otv');
      await fireEvent.click(moreIcon);
    });

    // Then
    expect(onOpen).toHaveBeenCalledTimes(1);
  });
});
