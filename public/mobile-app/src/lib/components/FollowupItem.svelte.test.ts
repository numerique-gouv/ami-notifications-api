import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as AMIGotoMethods from '$lib/ami-goto';
import { FollowupItem as Item } from '$lib/followup';
import FollowupItem from './FollowupItem.svelte';

describe('/FollowupItem.svelte', () => {
  test('should display a link', async () => {
    // Given
    const item = new Item(
      'partner',
      'type',
      'id',
      'notifications',
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
    render(FollowupItem, { props: { item: item, onOpen: onOpen } });

    // When
    const link = screen.getByTestId('followup-item-link');

    // Then
    expect(link.getAttribute('href')).toBe('/#/followup/item/partner/type/id');
  });
  describe('"Reprendre ma démarche" button', () => {
    test('Should display "Reprendre ma démarche" button only if item is "new"', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'notifications',
        [],
        'Opération Tranquillité Vacances',
        'subheading',
        'Votre demande est terminée.',
        'icon',
        new Date('2026-02-20T15:55:00.000Z'),
        'new',
        'Terminée',
        false,
        'link1'
      );
      const onOpen = vi.fn();
      const spy = vi
        .spyOn(AMIGotoMethods, 'AMIGoto')
        .mockImplementation(() => Promise.resolve());

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).not.toBeNull();
      });

      // When
      const button = screen.getByTestId('external-item-button-partner:type:id1');
      await fireEvent.click(button);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledWith('/#/followup/item/partner/type/id1');
      });
    });
    test('Should not display "Reprendre ma démarche" button if item has no link', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'notifications',
        [],
        'Opération Tranquillité Vacances',
        'subheading',
        'Votre demande est en cours de traitement 1.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'new',
        'Nouveau',
        false,
        null
      );
      const onOpen = vi.fn();

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).toBeNull();
      });
    });
    test('Should not display "Reprendre ma démarche" button if item is archived', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'notifications',
        [],
        'Opération Tranquillité Vacances',
        'subheading',
        'Votre demande est en cours de traitement 1.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'new',
        'Nouveau',
        true,
        'link1'
      );
      const onOpen = vi.fn();

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).toBeNull();
      });
    });
  });
});
