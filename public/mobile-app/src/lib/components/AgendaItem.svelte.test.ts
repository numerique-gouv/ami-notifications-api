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
    const spy1 = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
    const spy2 = vi.spyOn(AMINavigationMethods, 'AMIBackOrGoto').mockResolvedValue();

    // When
    render(AgendaItem, { props: { item: item } });

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
    const spy = vi.spyOn(AMINavigationMethods, 'AMIBackOrGoto').mockResolvedValue();

    // When
    render(AgendaItem, {
      props: {
        item: item,
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
    const moreIcon = screen.getByTestId(
      'agenda-item-ami-election:1764892800:elections-locales-open-modal-button'
    );
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
