import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { Agenda, Item } from '$lib/agenda';
import { toastStore } from '$lib/state/toast.svelte';
import AgendaItemModal from './AgendaItemModal.svelte';

const oneday_in_ms = 24 * 60 * 60 * 1000;
const today = new Date();
const in32days = new Date(today.getTime() + 32 * oneday_in_ms); // 32 days, so we are sure that month is different than today's

describe('/AgendaItemModal.svelte', () => {
  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();
  });

  test('should display item title', async () => {
    // Given
    const item = new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today);
    const agenda = new Agenda();

    // When
    render(AgendaItemModal, { props: { item, agenda } });

    // Then
    const title = screen.getByTestId('agenda-item-modal-header');
    expect(title).toHaveTextContent('Holiday 1');
  });

  test('should add toast when user clicks on "Supprimer" button', async () => {
    // Given
    const item = new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today);
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([item]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
    ]);
    const spy = vi.spyOn(toastStore, 'addToast');
    render(AgendaItemModal, { props: { item, agenda } });

    // When
    await waitFor(async () => {
      const deleteButton = screen.getByTestId('hide-agenda-item-button');
      await fireEvent.click(deleteButton);
    });

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        "L'élément a bien été supprimé",
        'success',
        3000,
        true
      );
    });
  });
});
