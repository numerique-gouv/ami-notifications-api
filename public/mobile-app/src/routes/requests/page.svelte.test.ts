import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(new FollowUp());
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
  test('Should display requests from API', async () => {
    // Given
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'items', 'get').mockReturnValue([
      new RequestItem(
        'id1',
        'notifications',
        'Opération Tranquillité Vacances',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        'wip',
        'En cours',
        false,
        null
      ),
      new RequestItem(
        'id2',
        'notifications',
        'Opération Tranquillité Vacances',
        'Votre demande est terminée.',
        new Date('2026-02-20T15:55:00.000Z'),
        'closed',
        'Terminée',
        false,
        null
      ),
    ]);
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('requests')).toHaveTextContent(
        'Votre demande est en cours de traitement.'
      );
      expect(screen.getByTestId('requests')).toHaveTextContent(
        'Votre demande est terminée.'
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
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('requests')).toHaveTextContent(
        'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
      );
    });
  });
  describe('More menu', () => {
    test('Should open more menu when user clicks on "more" button', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      render(Page);

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
      await userStore.login(mockUserInfo);
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      render(Page);
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
    test('Should open request item modal when clicks on more icon', async () => {
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
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
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-id1');
        await fireEvent.click(moreIcon);
      });

      // Then
      const requestItemModal = screen.getByTestId('request-item-modal');
      expect(requestItemModal).toBeInTheDocument();
    });
    test('Should close request item modal when clicks on "Archiver" button', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
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
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-id1');
        await fireEvent.click(moreIcon);
        const requestItemModal = screen.getByTestId('request-item-modal');
        expect(requestItemModal).toBeInTheDocument();
        const archiveButton = screen.getByTestId('archive-request-item-button');
        await fireEvent.click(archiveButton);
      });

      // Then
      expect(screen.queryByTestId('request-item-modal')).not.toBeInTheDocument();
    });
    test('should add toast when user clicks on "Archiver" button - archive success', async () => {
      // Given
      const followUp = new FollowUp();
      vi.spyOn(followUp, 'items', 'get').mockReturnValue([
        new RequestItem(
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
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-id1');
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
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-request-item-modal-id1');
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
