import { beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import * as agendaMethods from '$lib/agenda';
import { Agenda, Item } from '$lib/agenda';
import { toastStore } from '$lib/state/toast.svelte';
import { getTimestamp } from '$lib/utils';
import AgendaItemModal from './AgendaItemModal.svelte';

const today = new Date();

describe('/AgendaItemModal.svelte', () => {
  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn();
    HTMLDialogElement.prototype.close = vi.fn();
    HTMLDialogElement.prototype.show = vi.fn();
  });

  test('should display item title', async () => {
    // Given
    const item = new Item(
      'fake-id-holiday-1',
      ['public-holiday'],
      'Holiday 1',
      '',
      null,
      today
    );
    const agenda = new Agenda();

    // When
    render(AgendaItemModal, { props: { item, agenda, index: '' } });

    // Then
    const title = screen.getByTestId('agenda-item-modal-header');
    expect(title).toHaveTextContent('Holiday 1');
  });

  test('should mark emojis', async () => {
    // Given
    const item = new Item(
      'fake-id-marronnier',
      ['citizenship'],
      'Elections locales 📆',
      'Inscrivez-vous sur les listes électorales',
      null,
      new Date('2025-12-05'),
      null
    );
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([item]);
    vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda());
    render(AgendaItemModal, { props: { item, agenda, index: '' } });

    // Then
    expect(document.querySelector('[aria-hidden]')).toBeInTheDocument();
  });

  test('should add toast when user clicks on "Supprimer" button', async () => {
    // Given
    const item = new Item(
      'fake-id-holiday-1',
      ['public-holiday'],
      'Holiday 1',
      '',
      null,
      today
    );
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([item]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([]);
    const spy = vi.spyOn(toastStore, 'addToast');
    const spy2 = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda());
    render(AgendaItemModal, { props: { item, agenda, index: '' } });

    // When
    await waitFor(async () => {
      const deleteButton = screen.getByTestId(
        `agenda-item-ami-public-holiday:${getTimestamp(today)}:holiday-1-hide-button`
      );
      await fireEvent.click(deleteButton);
    });

    // Then
    await waitFor(async () => {
      expect(spy).toHaveBeenCalledWith(
        'L’élément a bien été supprimé',
        'success',
        3000,
        true
      );
      expect(spy2).toHaveBeenCalled();
    });
  });
});
