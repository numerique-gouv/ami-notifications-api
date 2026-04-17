import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import type { WS as WSType } from 'vitest-websocket-mock';
import WS from 'vitest-websocket-mock';
import * as navigationMethods from '$app/navigation';
import * as envModule from '$env/static/public';
import * as agendaMethods from '$lib/agenda';
import { Agenda, Item } from '$lib/agenda';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import * as notificationsMethods from '$lib/notifications';
import { PUBLIC_API_WS_URL } from '$lib/notifications';
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
        PUBLIC_FEATUREFLAG_REQUESTS_ENABLED: 'true',
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

  test('should navigate to Settings page when user clicks on Paramétrer button', async () => {
    // Given
    const spy = vi
      .spyOn(navigationMethods, 'goto')
      .mockImplementation(() => Promise.resolve());
    render(ConnectedHomepage);

    // When
    const button = screen.getByTestId('settings-button');
    await fireEvent.click(button);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenNthCalledWith(1, '/#/settings');
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
      new Item('holiday', 'Holiday 1', null, new Date()),
      new Item('holiday', 'Holiday 2', null, new Date()),
    ]);
    vi.spyOn(agenda, 'next', 'get').mockReturnValue([
      new Item('holiday', 'Holiday 3', null, new Date()),
      new Item('holiday', 'Holiday 4', null, new Date()),
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
      new Item('holiday', 'Holiday 1', null, new Date()),
      new Item('holiday', 'Holiday 2', null, new Date()),
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

  test('Should not display any request if feature flag is not enabled', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATUREFLAG_REQUESTS_ENABLED = 'false';
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'current', 'get').mockReturnValue([
      new RequestItem(
        'Opération Tranquillité Vacances 1',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        null,
        'wip',
        'En cours',
        null
      ),
      new RequestItem(
        'Opération Tranquillité Vacances 2',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        null,
        'wip',
        'En cours',
        null
      ),
    ]);
    vi.spyOn(followUp, 'past', 'get').mockReturnValue([
      new RequestItem(
        'Opération Tranquillité Vacances 3',
        'Votre demande est terminée.',
        new Date('2026-02-20T15:55:00.000Z'),
        null,
        'closed',
        'Terminée',
        null
      ),
      new RequestItem(
        'Opération Tranquillité Vacances 4',
        'Votre demande est terminée.',
        new Date('2026-02-20T15:55:00.000Z'),
        null,
        'closed',
        'Terminée',
        null
      ),
    ]);
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);
    // When
    const { container } = render(ConnectedHomepage);

    // Then
    await waitFor(() => {
      const followUpBlock = container.querySelector('.requests-container');
      expect(spy).not.toHaveBeenCalled();
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 1');
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 2');
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 3');
      expect(followUpBlock).not.toHaveTextContent('Opération Tranquillité Vacances 4');
      expect(followUpBlock).toHaveTextContent('Retrouvez et suivez vos démarches ici.');
    });
  });

  test('Should display first request found from API', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATUREFLAG_REQUESTS_ENABLED = 'true';
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'current', 'get').mockReturnValue([
      new RequestItem(
        'Opération Tranquillité Vacances 1',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        null,
        'wip',
        'En cours',
        null
      ),
      new RequestItem(
        'Opération Tranquillité Vacances 2',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        null,
        'wip',
        'En cours',
        null
      ),
    ]);
    vi.spyOn(followUp, 'past', 'get').mockReturnValue([
      new RequestItem(
        'Opération Tranquillité Vacances 3',
        'Votre demande est terminée.',
        new Date('2026-02-20T15:55:00.000Z'),
        null,
        'closed',
        'Terminée',
        null
      ),
      new RequestItem(
        'Opération Tranquillité Vacances 4',
        'Votre demande est terminée.',
        new Date('2026-02-20T15:55:00.000Z'),
        null,
        'closed',
        'Terminée',
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

  test('Should display first request found from API - current is empty', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATUREFLAG_REQUESTS_ENABLED = 'true';
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'current', 'get').mockReturnValue([]);
    vi.spyOn(followUp, 'past', 'get').mockReturnValue([
      new RequestItem(
        'Opération Tranquillité Vacances 1',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        null,
        'wip',
        'En cours',
        null
      ),
      new RequestItem(
        'Opération Tranquillité Vacances 2',
        'Votre demande est en cours de traitement.',
        new Date('2026-02-22T15:55:00.000Z'),
        null,
        'wip',
        'En cours',
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
      expect(followUpBlock).not.toHaveTextContent(
        'Retrouvez et suivez vos démarches ici.'
      );
    });
  });

  test('should display requests block if follow-up is empty', async () => {
    // Given
    vi.mocked(envModule).PUBLIC_FEATUREFLAG_REQUESTS_ENABLED = 'true';
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'current', 'get').mockReturnValue([]);
    vi.spyOn(followUp, 'past', 'get').mockReturnValue([]);
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

  test('should call userStore.logout', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }));
    const spyLogout = vi.spyOn(userStore, 'logout').mockResolvedValue();

    // When
    render(ConnectedHomepage);
    const franceConnectLogoutButton = screen.getByRole('button', {
      name: 'Me déconnecter',
    });
    await franceConnectLogoutButton.click();

    const confirmButton = screen.getByTestId('logout-submit-button');
    await confirmButton.click();

    // Then
    expect(spyLogout).toHaveBeenCalled();
  });

  test('should not call userStore.logout if cancel button is clicked', async () => {
    // Given
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 200 }));
    const spyLogout = vi.spyOn(userStore, 'logout').mockResolvedValue();

    // When
    render(ConnectedHomepage);
    const franceConnectLogoutButton = screen.getByRole('button', {
      name: 'Me déconnecter',
    });
    await franceConnectLogoutButton.click();

    const confirmButton = screen.getByTestId('logout-cancel-button');
    await confirmButton.click();

    // Then
    expect(spyLogout).not.toHaveBeenCalled();
  });
});
