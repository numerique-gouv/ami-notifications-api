import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import FollowupComponent from '$lib/components/Followup.svelte';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import { toastStore } from '$lib/state/toast.svelte';

describe('/Followup.svelte', () => {
  describe('Current items', () => {
    test('Should display followup from API', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          null
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id4',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 4.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          true,
          null
        ),
      ]);
      const spy = vi
        .spyOn(followupMethods, 'buildFollowup')
        .mockResolvedValue(followup);

      // When
      render(FollowupComponent);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('followup')).toHaveTextContent(
          'Votre demande est en cours de traitement 1.'
        );
        expect(screen.getByTestId('followup')).toHaveTextContent(
          'Votre demande est terminée 2.'
        );
        expect(screen.getByTestId('followup')).not.toHaveTextContent(
          'Votre demande est en cours de traitement 3.'
        );
        expect(screen.getByTestId('followup')).not.toHaveTextContent(
          'Votre demande est terminée 4.'
        );
        expect(screen.getByTestId('followup')).not.toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should display empty followup', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
      ]);
      const spy = vi
        .spyOn(followupMethods, 'buildFollowup')
        .mockResolvedValue(followup);

      // When
      render(FollowupComponent);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('followup')).toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should display "Reprendre ma démarche" button only if item is "new"', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          false,
          'link1'
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          'link2'
        ),
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'closed',
          'Terminé',
          false,
          'link3'
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      vi.stubGlobal('location', { href: 'fake-link' });

      // When
      render(FollowupComponent);

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).not.toBeNull();
        expect(
          screen.queryByTestId('external-item-button-partner:type:id2')
        ).toBeNull();
        expect(
          screen.queryByTestId('external-item-button-partner:type:id3')
        ).toBeNull();
      });

      // When
      const button = screen.getByTestId('external-item-button-partner:type:id1');
      await fireEvent.click(button);

      // Then
      await waitFor(() => {
        expect(window.location.href).toBe('link1');
      });
    });
    test('Should not display "Reprendre ma démarche" button only if item has no link', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          false,
          null
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      // When
      render(FollowupComponent);

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).toBeNull();
      });
    });
  });
  describe('Archived items', () => {
    test('Should display followup from API', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          null
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id4',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 4.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          true,
          null
        ),
      ]);
      const spy = vi
        .spyOn(followupMethods, 'buildFollowup')
        .mockResolvedValue(followup);

      // When
      render(FollowupComponent, { archived: true });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('followup')).not.toHaveTextContent(
          'Votre demande est en cours de traitement 1.'
        );
        expect(screen.getByTestId('followup')).not.toHaveTextContent(
          'Votre demande est terminée 2.'
        );
        expect(screen.getByTestId('followup')).toHaveTextContent(
          'Votre demande est en cours de traitement 3.'
        );
        expect(screen.getByTestId('followup')).toHaveTextContent(
          'Votre demande est terminée 4.'
        );
        expect(screen.getByTestId('followup')).not.toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should display empty followup', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([]);
      const spy = vi
        .spyOn(followupMethods, 'buildFollowup')
        .mockResolvedValue(followup);

      // When
      render(FollowupComponent, { archived: true });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('followup')).toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should not display "Reprendre ma démarche" button as items are archived', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          true,
          'link1'
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          'link2'
        ),
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'closed',
          'Terminé',
          true,
          'link3'
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      // When
      render(FollowupComponent);

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).toBeNull();
        expect(
          screen.queryByTestId('external-item-button-partner:type:id2')
        ).toBeNull();
        expect(
          screen.queryByTestId('external-item-button-partner:type:id3')
        ).toBeNull();
      });
    });
  });
  describe('More menu', () => {
    test('No "more" button for archived followup items', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      // When
      render(FollowupComponent, { archived: true });

      // Then
      await waitFor(async () => {
        const button = screen.queryByTestId('more-button');
        expect(button).toBeNull();
      });
    });
    test('Should open more menu when user clicks on "more" button', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      render(FollowupComponent);

      // When
      await waitFor(async () => {
        const button = screen.getByTestId('more-button');
        await fireEvent.click(button);
      });

      // Then
      const moreMenu = screen.getByTestId('more-menu');
      expect(moreMenu).toBeInTheDocument();
    });
    test('Should redirect to archived followup page when user clicks on "Démarches archivées" button', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      render(FollowupComponent);
      const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
      await waitFor(async () => {
        const button = screen.getByTestId('more-button');
        await fireEvent.click(button);
      });

      // When
      await waitFor(async () => {
        const button = screen.getByTestId('archived-followup-button');
        await fireEvent.click(button);
      });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('/#/followup/archived');
      });
    });
  });
  describe('Followup item modal', () => {
    test('No more icon for archived followup item', async () => {
      const followup = new Followup();
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      // When
      render(FollowupComponent, { archived: true });

      // Then
      await waitFor(async () => {
        const moreIcon = screen.queryByTestId(
          'open-followup-item-modal-partner:type:id1'
        );
        expect(moreIcon).toBeNull();
      });
    });
    test('Should open followup item modal when clicks on more icon', async () => {
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      render(FollowupComponent);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId(
          'open-followup-item-modal-partner:type:id1'
        );
        await fireEvent.click(moreIcon);
      });

      // Then
      const followupItemModal = screen.getByTestId('item-modal');
      expect(followupItemModal).toBeInTheDocument();
    });
    test('Should close followup item modal when clicks on "Archiver" button', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      vi.spyOn(FollowupItem.prototype, 'archive').mockResolvedValue(true);
      render(FollowupComponent);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId(
          'open-followup-item-modal-partner:type:id1'
        );
        await fireEvent.click(moreIcon);
        const followupItemModal = screen.getByTestId('item-modal');
        expect(followupItemModal).toBeInTheDocument();
        const archiveButton = screen.getByTestId('archive-followup-item-button');
        await fireEvent.click(archiveButton);
      });

      // Then
      expect(screen.queryByTestId('item-modal')).not.toBeInTheDocument();
    });
    test('should add toast when user clicks on "Archiver" button - archive success', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spy = vi.spyOn(FollowupItem.prototype, 'archive').mockResolvedValue(true);
      const spy2 = vi.spyOn(toastStore, 'addToast');
      render(FollowupComponent);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId(
          'open-followup-item-modal-partner:type:id1'
        );
        await fireEvent.click(moreIcon);
        const archiveButton = screen.getByTestId('archive-followup-item-button');
        await fireEvent.click(archiveButton);
      });

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith();
        expect(spy2).toHaveBeenCalledWith(
          "L'élément a bien été archivé",
          'success',
          3000,
          true
        );
      });
    });
    test('should add toast when user clicks on "Archiver" button - archive error', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
      const spy = vi.spyOn(FollowupItem.prototype, 'archive').mockResolvedValue(false);
      const spy2 = vi.spyOn(toastStore, 'addToast');
      render(FollowupComponent);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId(
          'open-followup-item-modal-partner:type:id1'
        );
        await fireEvent.click(moreIcon);
        const archiveButton = screen.getByTestId('archive-followup-item-button');
        await fireEvent.click(archiveButton);
      });

      // Then
      await waitFor(async () => {
        expect(spy).toHaveBeenCalledWith();
        expect(spy2).toHaveBeenCalledWith(
          "L'élément n'a pas pu être archivé",
          'error',
          3000,
          true
        );
      });
    });
  });
});
