import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import FollowupComponent from '$lib/components/followup/Followup.svelte';
import * as consentsMethods from '$lib/consents';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import { toastStore } from '$lib/state/toast.svelte.js';

describe('/Followup.svelte', () => {
  describe('Current items', () => {
    beforeEach(async () => {
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(true);
    });

    test('Should display followup from API', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
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
          false,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée 2.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          null,
          []
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'ref3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id4',
          'ref4',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée 4.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          true,
          null,
          []
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
        const accordionButton: HTMLButtonElement =
          screen.getByTestId('accordion-button');
        expect(accordionButton).toHaveAttribute('aria-expanded', 'false');
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
          'ref3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null,
          []
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
          'Votre démarche n’apparaît pas ? Consultez votre compte Service Public CNMSS Démarche numérique Dossier facile Vérifiez que vous suivez bien toutes vos démarches'
        );
        const accordionButton: HTMLButtonElement =
          screen.getByTestId('accordion-button');
        expect(accordionButton).toHaveAttribute('aria-expanded', 'true');
      });
    });
  });
  describe('Archived items', () => {
    beforeEach(async () => {
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(true);
    });

    test('Should display followup from API', async () => {
      // Given
      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([
        new FollowupItem(
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
          false,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée 2.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          false,
          null,
          []
        ),
      ]);
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id3',
          'ref3',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est en cours de traitement 3.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id4',
          'ref4',
          'notifications',
          [],
          'Opération Tranquillité Vacances',
          'subheading',
          'Votre demande est terminée 4.',
          'icon',
          new Date('2026-02-20T15:55:00.000Z'),
          'closed',
          'Terminée',
          true,
          null,
          []
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
        const accordionButton: HTMLButtonElement =
          screen.getByTestId('accordion-button');
        expect(accordionButton).toHaveAttribute('aria-expanded', 'false');
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
          false,
          null,
          []
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
          'Votre démarche n’apparaît pas ? Consultez votre compte Service Public CNMSS Démarche numérique Dossier facile Vérifiez que vous suivez bien toutes vos démarches'
        );
        const accordionButton: HTMLButtonElement =
          screen.getByTestId('accordion-button');
        expect(accordionButton).toHaveAttribute('aria-expanded', 'false');
      });
    });
  });
  describe('More menu', () => {
    beforeEach(async () => {
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(true);
    });

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
      const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();
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

    test('No "more" button when user has not consented', async () => {
      // Given
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(false);

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
  });
  describe('Followup item modal', () => {
    beforeEach(async () => {
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(true);
    });

    test('No more icon for archived followup item', async () => {
      const followup = new Followup();
      vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
        new FollowupItem(
          'partner',
          'type',
          'id1',
          'ref1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          true,
          null,
          []
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
          'ref1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
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
          'ref1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
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
          'ref1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
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
          'L’élément a bien été archivé',
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
          'ref1',
          'notifications',
          [],
          'Opération Tranquillité Vacances 1',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
        ),
        new FollowupItem(
          'partner',
          'type',
          'id2',
          'ref2',
          'notifications',
          [],
          'Opération Tranquillité Vacances 2',
          'subheading',
          'Votre demande est en cours de traitement.',
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null,
          []
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
          "L’élément n'a pas pu être archivé",
          'error',
          3000,
          true
        );
      });
    });
  });

  describe('No consent block', () => {
    beforeEach(async () => {
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(true);
    });

    test('No more icon for archived followup item', async () => {
      // Given
      vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(false);

      const followup = new Followup();
      vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

      // When
      const { container } = render(FollowupComponent);

      // Then
      await waitFor(() => {
        const followupNoConsentBlock = container.querySelector(
          '.followup-no-consent-container'
        );
        expect(followupNoConsentBlock).toHaveTextContent(
          'Suivez vos démarches administratives au même endroit !'
        );
      });
    });
  });
});
