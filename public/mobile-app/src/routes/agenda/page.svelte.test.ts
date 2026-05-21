import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as agendaMethods from '$lib/agenda';
import { Agenda, Item, monthName } from '$lib/agenda';
import { toastStore } from '$lib/state/toast.svelte';
import Page from './+page.svelte';

const oneday_in_ms = 24 * 60 * 60 * 1000;
const today = new Date();
const in32days = new Date(today.getTime() + 32 * oneday_in_ms); // 32 days, so we are sure that month is different than today's

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda());
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
  test('Should display holidays from API', async () => {
    // Given
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([
      new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
    ]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('events-now')).toHaveTextContent('Prochainement');
      expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(today));
      expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1');
      expect(screen.getByTestId('events-next')).toHaveTextContent('Les mois suivants');
      expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days));
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2');
    });
  });
  test('Should not display "next" section if empty', async () => {
    // Given
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.queryByTestId('events-now')).toBeNull();
      expect(screen.getByTestId('events-next')).toHaveTextContent('Les mois suivants');
      expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days));
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2');
    });
  });
  test('Should not display "next" section if empty', async () => {
    // Given
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([
      new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
    ]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('events-now')).toHaveTextContent('Prochainement');
      expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(today));
      expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1');
      expect(screen.queryByTestId('events-next')).toBeNull();
    });
  });
  test('Should not repeat month', async () => {
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([
      new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
      new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, today),
    ]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-holiday-3', 'holiday', 'Holiday 3', null, in32days),
      new Item('fake-id-holiday-4', 'holiday', 'Holiday 4', null, in32days),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('events-now')).toHaveTextContent('Prochainement');
      expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(today));
      const today_month_occurrences = (
        screen
          ?.getByTestId('events-now')
          ?.textContent?.match(new RegExp(monthName(today), 'g')) || []
      ).length;
      expect(today_month_occurrences).toBe(1);
      expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1');
      expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 2');
      expect(screen.getByTestId('events-next')).toHaveTextContent('Les mois suivants');
      expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days));
      const in32days_month_occurrences = (
        screen
          ?.getByTestId('events-now')
          ?.textContent?.match(new RegExp(monthName(today), 'g')) || []
      ).length;
      expect(in32days_month_occurrences).toBe(1);
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 3');
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 4');
    });
  });
  test('Should not repeat month (with "next" part empty)', async () => {
    // Given
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, in32days),
      new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.queryByTestId('events-now')).toBeNull();
      expect(screen.getByTestId('events-next')).toHaveTextContent('Les mois suivants');
      expect(screen.getByTestId('events-next')).toHaveTextContent(monthName(in32days));
      const in32days_month_occurrences = (
        screen
          ?.getByTestId('events-next')
          ?.textContent?.match(new RegExp(monthName(in32days), 'g')) || []
      ).length;
      expect(in32days_month_occurrences).toBe(1);
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 1');
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2');
    });
  });
  test('Should not repeat month (when last "next" event month is the same as first "next" event month)', async () => {
    // Given
    var start1 = today;
    var start2 = new Date(today.getTime() + 1 * oneday_in_ms);
    if (start1.getMonth() !== start2.getMonth()) {
      start1 = new Date(today.getTime() + 1 * oneday_in_ms);
      start2 = new Date(today.getTime() + 2 * oneday_in_ms);
    }
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([
      new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, start1),
    ]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, start2),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    render(Page);

    // Then
    expect(monthName(start1)).toEqual(monthName(start2));
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('events-now')).toHaveTextContent('Prochainement');
      expect(screen.getByTestId('events-now')).toHaveTextContent(monthName(start1));
      expect(screen.getByTestId('events-now')).toHaveTextContent('Holiday 1');
      expect(screen.getByTestId('events-next')).toHaveTextContent('Les mois suivants');
      expect(screen.getByTestId('events-next')).not.toHaveTextContent(
        monthName(start2)
      );
      expect(screen.getByTestId('events-next')).toHaveTextContent('Holiday 2');
    });
  });

  describe('Agenda item modal', () => {
    test('Should open agenda item modal when clicks on more icon', async () => {
      // Given
      const agenda = new Agenda();
      vi.spyOn(agenda, 'now', 'get').mockReturnValue([
        new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
      ]);
      vi.spyOn(agenda, 'next', 'get').mockReturnValue([
        new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
      ]);
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-holiday-1');
        await fireEvent.click(moreIcon);
      });

      // Then
      const agendaItemModal = screen.getByTestId('agenda-item-modal');
      expect(agendaItemModal).toBeInTheDocument();
    });

    test('Should close agenda item modal when clicks on "Supprimer" button', async () => {
      // Given
      const agenda = new Agenda();
      vi.spyOn(agenda, 'now', 'get').mockReturnValue([
        new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
      ]);
      vi.spyOn(agenda, 'next', 'get').mockReturnValue([
        new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
      ]);
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-holiday-1');
        await fireEvent.click(moreIcon);

        const agendaItemModal = screen.getByTestId('agenda-item-modal');
        expect(agendaItemModal).toBeInTheDocument();

        const deleteButton = screen.getByTestId('hide-agenda-item-button');
        await fireEvent.click(deleteButton);
      });

      // Then
      expect(screen.queryByTestId('agenda-item-modal')).not.toBeInTheDocument();
    });

    test('should add toast when user clicks on "Supprimer" button', async () => {
      // Given
      const agenda = new Agenda();
      vi.spyOn(agenda, 'now', 'get').mockReturnValue([
        new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
      ]);
      vi.spyOn(agenda, 'next', 'get').mockReturnValue([
        new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
      ]);
      const spy = vi.spyOn(toastStore, 'addToast');
      render(Page);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-holiday-1');
        await fireEvent.click(moreIcon);

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
});
