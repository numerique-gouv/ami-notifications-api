import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { Item } from '$lib/agenda';
import AgendaItem from './AgendaItem.svelte';

describe('/AgendaItem.svelte', () => {
  test('should call onOpen when clicks on more icon', async () => {
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
    const onOpen = vi.fn();
    render(AgendaItem, { props: { item: item, onOpen: onOpen } });

    // When
    await waitFor(async () => {
      const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-election');
      await fireEvent.click(moreIcon);
    });

    // Then
    expect(onOpen).toHaveBeenCalledTimes(1);
  });
});
