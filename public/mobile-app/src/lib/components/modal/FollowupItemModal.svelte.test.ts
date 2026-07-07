import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import { toastStore } from '$lib/state/toast.svelte';
import FollowupItemModal from './FollowupItemModal.svelte';

describe('/FollowupItemModal.svelte', () => {
  let item: FollowupItem;
  let followup: Followup;
  const isFollowupEmpty = false;

  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();

    item = new FollowupItem(
      'partner',
      'partner-name',
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
    );
    followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([
      item,
      new FollowupItem(
        'partner',
        'partner-name',
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
  });

  test('should display item title', async () => {
    // When
    render(FollowupItemModal, { props: { item, followup, isFollowupEmpty } });

    // Then
    const title = screen.getByTestId('followup-item-modal-header');
    expect(title).toHaveTextContent('Opération Tranquillité Vacances 1');
  });
  test('should add toast when user clicks on "Archiver" button - archive success', async () => {
    // Given
    const spy = vi.spyOn(FollowupItem.prototype, 'archive').mockResolvedValue(true);
    const spy2 = vi.spyOn(toastStore, 'addToast');
    render(FollowupItemModal, { props: { item, followup, isFollowupEmpty } });

    // When
    await waitFor(async () => {
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
    const spy = vi.spyOn(FollowupItem.prototype, 'archive').mockResolvedValue(false);
    const spy2 = vi.spyOn(toastStore, 'addToast');
    render(FollowupItemModal, { props: { item, followup, isFollowupEmpty } });

    // When
    await waitFor(async () => {
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
