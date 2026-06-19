import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import type { WS as WSType } from 'vitest-websocket-mock';
import WS from 'vitest-websocket-mock';
import * as navigationMethods from '$app/navigation';
import * as agendaMethods from '$lib/agenda';
import { Agenda, Item } from '$lib/agenda';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import * as notificationsMethods from '$lib/notifications';
import { PUBLIC_API_WS_URL } from '$lib/notifications';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import { mockAddress, mockUserInfo } from '$tests/utils';
import ConnectedHomepage from './ConnectedHomepage.svelte';

let wss: WSType;

describe('/ConnectedHomepage.svelte', () => {
  beforeEach(async () => {
    await userStore.login(mockUserInfo);

    vi.mock('$lib/notifications', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      const registration = { id: 'fake-registration-id' };
      return {
        ...original,
        enableNotifications: vi.fn(() => Promise.resolve(registration)),
        disableNotifications: vi.fn(() => Promise.resolve()),
        countUnreadNotifications: vi.fn(() => 3),
      };
    });

    vi.mock('$env/static/public', async (importOriginal) => {
      const original = (await importOriginal()) as Record<string, unknown>;
      return Promise.resolve({
        ...original,
        PUBLIC_API_URL: 'https://localhost:8000',
        PUBLIC_MATOMO_ENABLED: 'false',
      });
    });

    vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(new Agenda());

    vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(new FollowUp());

    window.localStorage.setItem('notifications_enabled', 'false');
    window.localStorage.setItem('user_data', 'fake-user-data');
    window.localStorage.setItem('emailLocalStorage', 'test@email.fr');
    window.localStorage.setItem('pushSubscriptionLocalStorage', '{}');

    wss = new WS(`${PUBLIC_API_WS_URL}/api/v1/users/notification/events/stream`);
  });

  afterEach(() => {
    wss.close();
    vi.resetAllMocks();
  });

  test("should display user's initials on menu", async () => {
    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const initials = container.querySelector('.user-profile');
      expect(initials).toHaveTextContent('A');
      expect(initials).not.toHaveTextContent('ACL');
    });
  });

  test("should display user's notification count", async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'countUnreadNotifications')
      .mockResolvedValue(3);

    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      const icon = container.querySelector('#notification-icon');
      expect(icon).toHaveTextContent('3');
    });
  });

  test("should refresh user's notification count", async () => {
    // Given
    const spy = vi
      .spyOn(notificationsMethods, 'countUnreadNotifications')
      .mockResolvedValueOnce(3)
      .mockResolvedValueOnce(4);

    const { container } = render(ConnectedHomepage);
    await waitFor(() => {
      const icon = container.querySelector('#notification-icon');
      expect(icon).toHaveTextContent('3');
    });

    // When
    wss.send('ping');

    // Then
    expect(spy).toHaveBeenCalledTimes(2);
    await waitFor(() => {
      const icon = container.querySelector('#notification-icon');
      expect(icon).toHaveTextContent('4');
    });
  });

  test('should navigate to User profile page when user clicks on Mon profil button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    render(ConnectedHomepage);

    // When
    const button = screen.getByTestId('profile-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenNthCalledWith(1, '/#/profile');
    });
  });

  test('should navigate to Préférences page when user clicks on Préférences button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    render(ConnectedHomepage);

    // When
    const button = screen.getByTestId('preferences-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenNthCalledWith(1, '/#/preferences');
    });
  });

  test('should navigate to Contact page when user clicks on Nous contacter button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    render(ConnectedHomepage);

    // When
    const button = screen.getByTestId('contact-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledWith('/#/contact');
    });
  });

  test('should display address block when user address is not known (empty)', async () => {
    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.address-container');
      expect(addressBlock).toHaveTextContent(
        "Renseignez votre adresse sur l'application pour faciliter vos échanges !"
      );
    });
  });

  test('should display address block when user address is not known (null)', async () => {
    // Given
    delete userStore.connected?.identity?.address;

    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.address-container');
      expect(addressBlock).toHaveTextContent(
        "Renseignez votre adresse sur l'application pour faciliter vos échanges !"
      );
    });
  });

  test('should not display address block when user address is known', async () => {
    // Given
    userStore.connected?.setAddress(mockAddress);

    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const addressBlock = container.querySelector('.first-block-container');
      expect(addressBlock).toBeNull();
    });
  });

  test('Should display first holiday found from API', async () => {
    // Given
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([
      new Item('fake-id-1', 'holiday', 'Holiday 1', null, new Date()),
      new Item('fake-id-2', 'holiday', 'Holiday 2', null, new Date()),
    ]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-3', 'holiday', 'Holiday 3', null, new Date()),
      new Item('fake-id-4', 'holiday', 'Holiday 4', null, new Date()),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const agendaBlock = container.querySelector('.agenda-container');
      expect(spy).toHaveBeenCalledTimes(1);
      expect(agendaBlock).toHaveTextContent('Holiday 1');
      expect(agendaBlock).not.toHaveTextContent('Holiday 2');
      expect(agendaBlock).not.toHaveTextContent('Holiday 3');
      expect(agendaBlock).not.toHaveTextContent('Holiday 4');
      expect(agendaBlock).not.toHaveTextContent(
        'Retrouvez les temps importants de votre vie administrative ici'
      );
    });
  });

  test('Should display first holiday found from API - now is empty', async () => {
    // Given
    const agenda = new Agenda();
    vi.spyOn(agenda, 'now', 'get').mockReturnValue([]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('fake-id-1', 'holiday', 'Holiday 1', null, new Date()),
      new Item('fake-id-2', 'holiday', 'Holiday 2', null, new Date()),
    ]);
    const spy = vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);

    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const agendaBlock = container.querySelector('.agenda-container');
      expect(spy).toHaveBeenCalledTimes(1);
      expect(agendaBlock).toHaveTextContent('Holiday 1');
      expect(agendaBlock).not.toHaveTextContent('Holiday 2');
      expect(agendaBlock).not.toHaveTextContent(
        'Retrouvez les temps importants de votre vie administrative ici'
      );
    });
  });

  test('should display calendar block if agenda is empty', async () => {
    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const agendaBlock = container.querySelector('.agenda-container');
      expect(agendaBlock).toHaveTextContent(
        'Retrouvez les temps importants de votre vie administrative ici'
      );
    });
  });

  describe('Agenda item modal', () => {
    const oneday_in_ms = 24 * 60 * 60 * 1000;
    const today = new Date();
    const in32days = new Date(today.getTime() + 32 * oneday_in_ms); // 32 days, so we are sure that month is different than today's

    test('Should open agenda item modal when clicks on more icon', async () => {
      // Given
      const agenda = new Agenda();
      vi.spyOn(agenda, 'now', 'get').mockReturnValue([
        new Item('fake-id-holiday-1', 'holiday', 'Holiday 1', null, today),
      ]);
      vi.spyOn(agenda, 'next', 'get').mockReturnValue([
        new Item('fake-id-holiday-2', 'holiday', 'Holiday 2', null, in32days),
      ]);
      vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);
      render(ConnectedHomepage);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-holiday-1');
        await fireEvent.click(moreIcon);
      });

      // Then
      const agendaItemModal = screen.getByTestId('item-modal');
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
      vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);
      render(ConnectedHomepage);

      // When
      await waitFor(async () => {
        const moreIcon = screen.getByTestId('open-agenda-item-modal-fake-id-holiday-1');
        await fireEvent.click(moreIcon);

        const agendaItemModal = screen.getByTestId('item-modal');
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
      vi.spyOn(agendaMethods, 'buildAgenda').mockResolvedValue(agenda);
      const spy = vi.spyOn(toastStore, 'addToast');
      render(ConnectedHomepage);

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

  test('Should display first request found from API', async () => {
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
        'icon',
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
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'wip',
        'En cours',
        false,
        null
      ),
      new RequestItem(
        'partner',
        'type',
        'id3',
        'notifications',
        'Opération Tranquillité Vacances 3',
        'Votre demande est terminée.',
        'icon',
        new Date('2026-02-20T15:55:00.000Z'),
        'closed',
        'Terminée',
        false,
        null
      ),
      new RequestItem(
        'partner',
        'type',
        'id4',
        'notifications',
        'Opération Tranquillité Vacances 4',
        'Votre demande est terminée.',
        'icon',
        new Date('2026-02-20T15:55:00.000Z'),
        'closed',
        'Terminée',
        false,
        null
      ),
    ]);
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const followUpBlock = container.querySelector('.requests-container');
      expect(spy).toHaveBeenCalledTimes(1);
      expect(followUpBlock).toHaveTextContent('Opération Tranquillité Vacances 1');
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 2');
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 3');
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 4');
      expect(followUpBlock).not.toHaveTextContent(
        'Retrouvez et suivez vos démarches ici.'
      );
    });
  });

  test('should display requests block if follow-up is empty', async () => {
    // Given
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'items', 'get').mockReturnValue([]);
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const followUpBlock = container.querySelector('.requests-container');
      expect(spy).toHaveBeenCalledTimes(1);
      expect(followUpBlock).toHaveTextContent('Retrouvez et suivez vos démarches ici.');
    });
  });

  describe('Request item modal', () => {
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
          'icon',
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
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      render(ConnectedHomepage);

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
          'icon',
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
          'icon',
          new Date('2026-02-22T15:55:00.000Z'),
          'wip',
          'En cours',
          false,
          null
        ),
      ]);
      vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
      vi.spyOn(RequestItem.prototype, 'archive').mockResolvedValue(true);
      render(ConnectedHomepage);

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
          'icon',
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
          'icon',
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
      render(ConnectedHomepage);

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
          'icon',
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
          'icon',
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
      render(ConnectedHomepage);

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
