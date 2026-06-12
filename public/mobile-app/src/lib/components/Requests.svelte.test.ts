import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import Requests from '$lib/components/Requests.svelte';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import { toastStore } from '$lib/state/toast.svelte';

describe('/Requests.svelte', () => {
  describe('Current items', () => {
    test('Should display requests from API', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          null
        ),
      ]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id3',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id4',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 4.',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          true,
          null
        ),
      ]);
      const spy = vi
        .spyOn(followUpMethods, 'buildFollowUp')
        .mockResolvedValue(followUp);

      // When
      render(Requests);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('requests')).toHaveTextContent(
          'Votre demande est en cours de traitement 1.'
        );
        expect(screen.getByTestId('requests')).toHaveTextContent(
          'Votre demande est terminée 2.'
        );
        expect(screen.getByTestId('requests')).not.toHaveTextContent(
          'Votre demande est en cours de traitement 3.'
        );
        expect(screen.getByTestId('requests')).not.toHaveTextContent(
          'Votre demande est terminée 4.'
        );
        expect(screen.getByTestId('requests')).not.toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should display empty followup', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id3',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
      ]);
      const spy = vi
        .spyOn(followUpMethods, 'buildFollowUp')
        .mockResolvedValue(followUp);

      // When
      render(Requests);

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('requests')).toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should display "Reprendre ma démarche" button only if item is "new"', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          false,
          'link1'
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          new Date('2026-02-20T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          'link2'
        ),
        new RequestItem(
          'partner',
          'type',
          'id3',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          new Date('2026-02-22T15:55:00.000Z'),
          'closed',
          'Terminé',
          false,
          'link3'
        ),
      ]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      vi.stubGlobal('location', { href: 'fake-link' });

      // When
      render(Requests);

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
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          false,
          null
        ),
      ]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

      // When
      render(Requests);

      // Then
      await waitFor(async () => {
        expect(
          screen.queryByTestId('external-item-button-partner:type:id1')
        ).toBeNull();
      });
    });
  });
  describe('Archived items', () => {
    test('Should display requests from API', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          null
        ),
      ]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id3',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id4',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 4.',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          true,
          null
        ),
      ]);
      const spy = vi
        .spyOn(followUpMethods, 'buildFollowUp')
        .mockResolvedValue(followUp);

      // When
      render(Requests, { archived: true });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('requests')).not.toHaveTextContent(
          'Votre demande est en cours de traitement 1.'
        );
        expect(screen.getByTestId('requests')).not.toHaveTextContent(
          'Votre demande est terminée 2.'
        );
        expect(screen.getByTestId('requests')).toHaveTextContent(
          'Votre demande est en cours de traitement 3.'
        );
        expect(screen.getByTestId('requests')).toHaveTextContent(
          'Votre demande est terminée 4.'
        );
        expect(screen.getByTestId('requests')).not.toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should display empty followup', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([]);
      const spy = vi
        .spyOn(followUpMethods, 'buildFollowUp')
        .mockResolvedValue(followUp);

      // When
      render(Requests, { archived: true });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('requests')).toHaveTextContent(
          'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
        );
      });
    });
    test('Should not display "Reprendre ma démarche" button as items are archived', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 1.',
          new Date('2026-02-22T15:55:00.000Z'),
          'new',
          'Nouveau',
          true,
          'link1'
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est terminée 2.',
          new Date('2026-02-20T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          'link2'
        ),
        new RequestItem(
          'partner',
          'type',
          'id3',
          'notifications',
          'Opération Tranquillité Vacances',
          'Votre demande est en cours de traitement 3.',
          new Date('2026-02-22T15:55:00.000Z'),
          'closed',
          'Terminé',
          true,
          'link3'
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

      // When
      render(Requests);

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
    test('No "more" button for archived request items', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

      // When
      render(Requests, { archived: true });

      // Then
      await waitFor(async () => {
        const button = screen.queryByTestId('more-button');
        expect(button).toBeNull();
      });
    });
    test('Should open more menu when user clicks on "more" button', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      render(Requests);

      // When
      await waitFor(async () => {
        const button = screen.getByTestId('more-button');
        await fireEvent.click(button);
      });

      // Then
      const moreMenu = screen.getByTestId('more-menu');
      expect(moreMenu).toBeInTheDocument();
    });
    test('Should redirect to archived requests page when user clicks on "Démarches archivées" button', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      render(Requests);
      const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
      await waitFor(async () => {
        const button = screen.getByTestId('more-button');
        await fireEvent.click(button);
      });

      // When
      await waitFor(async () => {
        const button = screen.getByTestId('archived-requests-button');
        await fireEvent.click(button);
      });

      // Then
      await waitFor(() => {
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('/#/requests/archived');
      });
    });
  });
  describe('Request item modal', () => {
    test('No more icon for archived request item', async () => {
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

      // When
      render(Requests, { archived: true });

      // Then
      await waitFor(async () => {
        const moreIcon = screen.queryByTestId(
          'open-request-item-modal-partner:type:id1'
        );
        expect(moreIcon).toBeNull();
      });
    });
    test('Should open request item modal when clicks on more icon', async () => {
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      render(Requests);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-partner:type:id1');
        await fireEvent.click(moreIcon);
      });

      // Then
      const requestItemModal = screen.getByTestId('item-modal');
      expect(requestItemModal).toBeInTheDocument();
    });
    test('Should close request item modal when clicks on "Archiver" button', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      vi.spyOn(RequestItem.prototype, 'archive').mockResolvedValue(true);
      render(Requests);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-partner:type:id1');
        await fireEvent.click(moreIcon);
        const requestItemModal = screen.getByTestId('item-modal');
        expect(requestItemModal).toBeInTheDocument();
        const archiveButton = screen.getByTestId('archive-request-item-button');
        await fireEvent.click(archiveButton);
      });

      // Then
      expect(screen.queryByTestId('item-modal')).not.toBeInTheDocument();
    });
    test('should add toast when user clicks on "Archiver" button - archive success', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      const spy = vi.spyOn(RequestItem.prototype, 'archive').mockResolvedValue(true);
      const spy2 = vi.spyOn(toastStore, 'addToast');
      render(Requests);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-partner:type:id1');
        await fireEvent.click(moreIcon);
        const archiveButton = screen.getByTestId('archive-request-item-button');
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
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
          'partner',
          'type',
          'id1',
          'notifications',
          'Opération Tranquillité Vacances 1',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
        new RequestItem(
          'partner',
          'type',
          'id2',
          'notifications',
          'Opération Tranquillité Vacances 2',
          'Votre demande est en cours de traitement.',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      const spy = vi.spyOn(RequestItem.prototype, 'archive').mockResolvedValue(false);
      const spy2 = vi.spyOn(toastStore, 'addToast');
      render(Requests);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-partner:type:id1');
        await fireEvent.click(moreIcon);
        const archiveButton = screen.getByTestId('archive-request-item-button');
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
