import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { Item } from '$lib/agenda';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { FollowupSubItem } from '$lib/followup';
import AgendaItem from './AgendaItem.svelte';

describe('/AgendaItem.svelte', () => {
  test('should display a link', async () => {
    // Given
    const item = new Item(
      'fake-id-election',
      'election',
      'Elections locales',
      'link',
      'Inscrivez-vous sur les listes électorales',
      new Date('2025-12-05'),
      null
    );
    const onOpen = vi.fn();
    const spy1 = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const spy2 = vi.spyOn(AMINavigationMethods, 'AMIBackOrGoto').mockResolvedValue();

    // When
    render(AgendaItem, { props: { item: item, onOpen: onOpen } });

    // Then
    const button = screen.getByTestId('agenda-item-link');
    await fireEvent.click(button);
    await waitFor(() => {
      expect(spy1).toHaveBeenCalledWith('link');
      expect(spy2).not.toHaveBeenCalled();
    });
  });
  test('should display a link - with followup sub item', async () => {
    // Given
    const item = new Item(
      'fake-id-election',
      'election',
      'Elections locales',
      'link',
      'Inscrivez-vous sur les listes électorales',
      new Date('2025-12-05'),
      null
    );
    const followupSubItem = new FollowupSubItem(
      'partner',
      'type',
      'id',
      'ref',
      'notifications',
      null,
      null,
      [],
      'Opération Tranquillité Vacances',
      'subheading',
      'Votre demande est terminée.',
      'icon',
      new Date('2026-02-20T15:55:00.000Z'),
      'closed',
      'Terminée',
      false,
      'url'
    );
    const onOpen = vi.fn();
    const spy = vi.spyOn(AMINavigationMethods, 'AMIBackOrGoto').mockResolvedValue();

    // When
    render(AgendaItem, {
      props: {
        item: item,
        onOpen: onOpen,
        followupSubItem: followupSubItem,
        useBackOrGoto: true,
      },
    });

    // Then
    const button = screen.getByTestId('agenda-item-link');
    await fireEvent.click(button);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('link');
    });
  });
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
    const onOpen = vi.fn();

    // When
    render(AgendaItem, { props: { item: item, onOpen: onOpen } });

    // Then
    expect(document.querySelector('[aria-hidden]')).toBeInTheDocument();
  });
});
