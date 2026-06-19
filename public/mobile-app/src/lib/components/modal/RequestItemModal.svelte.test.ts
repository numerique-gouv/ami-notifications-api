import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import { toastStore } from '$lib/state/toast.svelte';
import RequestItemModal from './RequestItemModal.svelte';

describe('/RequestItemModal.svelte', () => {
  let item: RequestItem;
  let followUp: FollowUp;
  const isFollowUpEmpty = false;

  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();

    item = new RequestItem(
      'partner',
      'type',
      'id1',
      'notifications',
      'Opération Tranquillité Vacances 1',
      'Votre demande est en cours de traitement.',
      'icon',
      new Date('2026-02-22T15:55:00.000Z'),
      'wip',
      'En cours',
      false,
      null
    );
    followUp = new FollowUp();
    vi.spyOn(followUp, 'items', 'get').mockReturnValue([
      item,
      new RequestItem(
        'partner',
        'type',
        'id2',
        'notifications',
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
    vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
  });

  test('should display item title', async () => {
    // When
    render(RequestItemModal, { props: { item, followUp, isFollowUpEmpty } });

    // Then
    const title = screen.getByTestId('request-item-modal-header');
    expect(title).toHaveTextContent('Opération Tranquillité Vacances 1');
  });
  test('should add toast when user clicks on "Archiver" button - archive success', async () => {
    // Given
    const spy = vi.spyOn(RequestItem.prototype, 'archive').mockResolvedValue(true);
    const spy2 = vi.spyOn(toastStore, 'addToast');
    render(RequestItemModal, { props: { item, followUp, isFollowUpEmpty } });

    // When
    await waitFor(async () => {
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
    const spy = vi.spyOn(RequestItem.prototype, 'archive').mockResolvedValue(false);
    const spy2 = vi.spyOn(toastStore, 'addToast');
    render(RequestItemModal, { props: { item, followUp, isFollowUpEmpty } });

    // When
    await waitFor(async () => {
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
