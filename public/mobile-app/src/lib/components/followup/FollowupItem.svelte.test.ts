import { describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as navigationMethods from '$app/navigation';
import { FollowupItem as Item, FollowupSubItem as SubItem } from '$lib/followup';
import FollowupItem from './FollowupItem.svelte';

describe('/FollowupItem.svelte', () => {
  test('should display a link', async () => {
    // Given
    const item = new Item(
      'partner',
      'type',
      'id',
      'ref',
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
      'url',
      []
    );
    const onOpen = vi.fn();
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(FollowupItem, { props: { item: item, onOpen: onOpen } });

    // Then
    const button = screen.getByTestId('followup-item-link');
    await fireEvent.click(button);
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/followup/item/partner/type/id');
    });
  });
  describe('Description', () => {
    test('Should display item description if item has no sub items', async () => {
      const item = new Item(
        'partner',
        'type',
        'id1',
        'ref1',
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
        'link1',
        []
      );
      const onOpen = vi.fn();

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('followup-item-detail-partner:type:id1')
        ).toHaveTextContent('Votre demande est terminée.');
      });
    });
    test('Should display sub items progression if item has sub items - wip items', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'ref1',
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
        'link1',
        [
          new SubItem(
            'partner',
            'type',
            'id1',
            'ref1',
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
          ),
        ]
      );
      const onOpen = vi.fn();

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('followup-item-detail-partner:type:id1')
        ).toHaveTextContent('En cours par 1 service');
      });
    });
    test('Should display sub items progression if item has sub items - closed items', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'ref1',
        'notifications',
        [],
        'Opération Tranquillité Vacances',
        'subheading',
        'Votre demande est en cours de traitement 1.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'closed',
        'Terminé',
        true,
        'link1',
        [
          new SubItem(
            'partner',
            'type',
            'id1',
            'ref1',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en cours de traitement 1.',
            'icon',
            new Date('2026-02-22T15:55:00.000Z'),
            'closed',
            'Terminé',
            true,
            'link1'
          ),
        ]
      );
      const onOpen = vi.fn();

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('followup-item-detail-partner:type:id1')
        ).toHaveTextContent('Terminé par 1 service');
      });
    });
    test('Should display sub items progression if item has sub items - wip & closed items', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'ref1',
        'notifications',
        [],
        'Opération Tranquillité Vacances',
        'subheading',
        'Votre demande est en cours de traitement 1.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'wip',
        'En cours',
        true,
        'link1',
        [
          new SubItem(
            'partner',
            'type',
            'id1',
            'ref1',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en cours de traitement 1.',
            'icon',
            new Date('2026-02-22T15:55:00.000Z'),
            'closed',
            'Terminé',
            true,
            'link1'
          ),
          new SubItem(
            'partner',
            'type',
            'id2',
            'ref2',
            'notifications',
            [],
            'Opération Tranquillité Vacances',
            'subheading',
            'Votre demande est en cours de traitement 2.',
            'icon',
            new Date('2026-02-22T15:55:00.000Z'),
            'wip',
            'En cours',
            true,
            'link1'
          ),
        ]
      );
      const onOpen = vi.fn();

      // When
      render(FollowupItem, { props: { item: item, onOpen: onOpen } });

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('followup-item-detail-partner:type:id1')
        ).toHaveTextContent('En cours par 1 service Terminé par 1 service');
      });
    });
  });
  describe('"Reprendre ma démarche" button', () => {
    test('Should display "Reprendre ma démarche" button only if item is "new"', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'ref1',
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
        'link1',
        []
      );
      const onOpen = vi.fn();
      const spy = vi
        .spyOn(navigationMethods, 'goto')
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
        'ref1',
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
        null,
        []
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
        'ref1',
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
        'link1',
        []
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
    test('Should not display "Reprendre ma démarche" button if item has sub items', async () => {
      // Given
      const item = new Item(
        'partner',
        'type',
        'id1',
        'ref1',
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
        'link1',
        [
          new SubItem(
            'partner',
            'type',
            'id1',
            'ref1',
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
          ),
        ]
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
