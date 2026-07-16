import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as followupMethods from '$lib/followup';
import { Followup } from '$lib/followup';
import * as servicesMethods from '$lib/services';
import { Services, ServicesItem } from '$lib/services';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
  test('redirect to services if service is not found', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
    const spyFind = vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(null);

    // When
    render(Page, {
      props: { params: { partner_id: 'foo', item_type: 'bar' } },
    });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/services');
      expect(spyFind).toHaveBeenCalledTimes(1);
      expect(spyFind).toHaveBeenCalledWith('foo', 'bar');
    });
  });
  test('should display service title and description', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
    vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
      new ServicesItem(
        'psl',
        'OperationTranquilliteVacances',
        'Opération Tranquillité Vacances',
        'Sécurisez votre logement !',
        'Vous partez en vacances ? **Securisez votre logement.**',
        'fake-link',
        true
      )
    );

    // When
    render(Page, {
      props: { params: { partner_id: 'foo', item_type: 'bar' } },
    });

    // Then
    await waitFor(() => {
      expect(spy).not.toHaveBeenCalled();
      expect(screen.getByText('Opération Tranquillité Vacances')).toBeInTheDocument();
      expect(screen.getByText('Vous partez en vacances ?')).toBeInTheDocument();
      expect(screen.getByText('Securisez votre logement.')).toBeInTheDocument();
      expect(screen.queryByText('Sécurisez votre logement !')).toBeNull();
    });
  });
  test('should call getServiceUrl from ServicesItem', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
    vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
      new ServicesItem(
        'psl',
        'OperationTranquilliteVacances',
        'Opération Tranquillité Vacances',
        'Sécurisez votre logement !',
        'Vous partez en vacances ? **Securisez votre logement.**',
        'fake-link',
        true
      )
    );
    const spy = vi
      .spyOn(ServicesItem.prototype, 'getServiceUrl')
      .mockResolvedValue('http://external-url');

    // When
    render(Page, {
      props: { params: { partner_id: 'foo', item_type: 'bar' } },
    });

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
    });
  });
  test('should render a Back button', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
    vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
      new ServicesItem(
        'psl',
        'OperationTranquilliteVacances',
        'Opération Tranquillité Vacances',
        'Sécurisez votre logement !',
        'Vous partez en vacances ? **Securisez votre logement.**',
        'fake-link',
        true
      )
    );
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());

    // When
    render(Page, {
      props: { params: { partner_id: 'foo', item_type: 'bar' } },
    });

    // Then
    await waitFor(() => {
      expectBackButtonPresent(screen);
    });
  });
  describe('description parameters', () => {
    test('should format description with date from url param', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
      vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
        new ServicesItem(
          'psl',
          'OperationTranquilliteVacances',
          'Opération Tranquillité Vacances',
          'Sécurisez votre logement !',
          'Vous partez en vacances ? **Securisez votre logement.** À partir du {date}',
          'fake-link',
          true
        )
      );
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
      const spyFormatDescription = vi
        .spyOn(ServicesItem.prototype, 'formatDescription')
        .mockReturnValueOnce('formatted description');
      window.location.hash = '#/services/service/foo/bar?date=2025-12-05';

      // When
      render(Page, {
        props: { params: { partner_id: 'foo', item_type: 'bar' } },
      });

      // Then
      await waitFor(() => {
        expect(screen.getByText(/formatted description/)).toBeInTheDocument();
        expect(spyFormatDescription).toHaveBeenCalledTimes(1);
        expect(spyFormatDescription).toHaveBeenCalledWith('5 décembre');
      });
    });
    test('should format description with default date if url param is empty', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
      const spyFormatDescription = vi
        .spyOn(ServicesItem.prototype, 'formatDescription')
        .mockReturnValueOnce('formatted description');
      vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
        new ServicesItem(
          'psl',
          'OperationTranquilliteVacances',
          'Opération Tranquillité Vacances',
          'Sécurisez votre logement !',
          'Vous partez en vacances ? **Securisez votre logement.** À partir du {date}',
          'fake-link',
          true
        )
      );
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
      const date = new Date(2026, 5, 17, 12, 22);
      vi.setSystemTime(date);
      window.location.hash = '#/services/service/foo/bar?date=';

      // When
      render(Page, {
        props: { params: { partner_id: 'foo', item_type: 'bar' } },
      });

      // Then
      await waitFor(() => {
        expect(screen.getByText(/formatted description/)).toBeInTheDocument();
        expect(spyFormatDescription).toHaveBeenCalledTimes(1);
        expect(spyFormatDescription).toHaveBeenCalledWith('17 juin');
      });
    });
    test('should format description with default date if url param is missing', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
      vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
        new ServicesItem(
          'psl',
          'OperationTranquilliteVacances',
          'Opération Tranquillité Vacances',
          'Sécurisez votre logement !',
          'Vous partez en vacances ? **Securisez votre logement.** À partir du {date}',
          'fake-link',
          true
        )
      );
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
      const spyFormatDescription = vi
        .spyOn(ServicesItem.prototype, 'formatDescription')
        .mockReturnValueOnce('formatted description');
      const date = new Date(2026, 5, 17, 12, 22);
      vi.setSystemTime(date);
      window.location.hash = '#/services/service/foo/bar';

      // When
      render(Page, {
        props: { params: { partner_id: 'foo', item_type: 'bar' } },
      });

      // Then
      await waitFor(() => {
        expect(screen.getByText(/formatted description/)).toBeInTheDocument();
        expect(spyFormatDescription).toHaveBeenCalledTimes(1);
        expect(spyFormatDescription).toHaveBeenCalledWith('17 juin');
      });
    });
    test('should format description with default if url param is an invalid date', async () => {
      // Given
      await userStore.login(mockUserInfo);
      vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
      vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
        new ServicesItem(
          'psl',
          'OperationTranquilliteVacances',
          'Opération Tranquillité Vacances',
          'Sécurisez votre logement !',
          'Vous partez en vacances ? **Securisez votre logement.** À partir du {date}',
          'fake-link',
          true
        )
      );
      vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
      const spyFormatDescription = vi
        .spyOn(ServicesItem.prototype, 'formatDescription')
        .mockReturnValueOnce('formatted description');
      const date = new Date(2026, 5, 17, 12, 22);
      vi.setSystemTime(date);
      window.location.hash = '#/services/service/foo/bar?date=coucou';

      // When
      render(Page, {
        props: { params: { partner_id: 'foo', item_type: 'bar' } },
      });

      // Then
      await waitFor(() => {
        expect(screen.getByText(/formatted description/)).toBeInTheDocument();
        expect(spyFormatDescription).toHaveBeenCalledTimes(1);
        expect(spyFormatDescription).toHaveBeenCalledWith('17 juin');
      });
    });
  });
  describe('buttons', () => {
    describe('buttons display', () => {
      test('should retrieve service url', async () => {
        // Given
        await userStore.login(mockUserInfo);
        vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
        vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
          new ServicesItem(
            'partner',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement !',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'fake-link',
            true
          )
        );
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
        const spyHasNonArchivedItems = vi
          .spyOn(Followup.prototype, 'hasNonArchivedItems')
          .mockReturnValue(false);

        // When
        render(Page, {
          props: { params: { partner_id: 'foo', item_type: 'bar' } },
        });

        // Then
        await waitFor(async () => {
          expect(screen.queryByTestId('service-button')).not.toBeNull();
          expect(screen.queryByTestId('followup-button')).toBeNull();
          expect(spyHasNonArchivedItems).toHaveBeenCalledTimes(1);
          expect(spyHasNonArchivedItems).toHaveBeenCalledWith(
            'partner',
            'OperationTranquilliteVacances'
          );
        });
      });

      test('should retrieve service url - non archived items exists', async () => {
        // Given
        await userStore.login(mockUserInfo);
        vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
        vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
          new ServicesItem(
            'psl',
            'MonService',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement !',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'fake-link',
            true
          )
        );
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
        const spyHasNonArchivedItems = vi
          .spyOn(Followup.prototype, 'hasNonArchivedItems')
          .mockReturnValue(true);

        // When
        render(Page, {
          props: { params: { partner_id: 'foo', item_type: 'bar' } },
        });

        // Then
        await waitFor(() => {
          expect(screen.queryByTestId('service-button')).not.toBeNull();
          expect(screen.queryByTestId('followup-button')).not.toBeNull();
          expect(spyHasNonArchivedItems).toHaveBeenCalledTimes(1);
          expect(spyHasNonArchivedItems).toHaveBeenCalledWith('psl', 'MonService');
        });
      });

      test('should disable button when service url is empty', async () => {
        // Given
        await userStore.login(mockUserInfo);
        vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
        vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
          new ServicesItem(
            'partner',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement !',
            'Vous partez en vacances ? **Securisez votre logement.**',
            '',
            true
          )
        );
        const spyUrl = vi
          .spyOn(ServicesItem.prototype, 'getServiceUrl')
          .mockResolvedValue('');
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
        vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(false);

        // When
        render(Page, {
          props: { params: { partner_id: 'foo', item_type: 'bar' } },
        });

        // Then
        await waitFor(async () => {
          const serviceButton = screen.getByTestId('service-button');
          expect(serviceButton).toBeDisabled();
          expect(screen.queryByTestId('followup-button')).toBeNull();
          expect(spyUrl).toHaveBeenCalledTimes(1);
        });
      });
    });
    describe('buttons onclick', () => {
      describe('followup button', () => {
        test('should redirect to followup', async () => {
          // Given
          await userStore.login(mockUserInfo);
          vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
          vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
            new ServicesItem(
              'psl',
              'MonService',
              'Opération Tranquillité Vacances',
              'Sécurisez votre logement !',
              'Vous partez en vacances ? **Securisez votre logement.**',
              'fake-link',
              true
            )
          );
          const spyUrl = vi
            .spyOn(ServicesItem.prototype, 'getServiceUrl')
            .mockResolvedValue('http://external-url');
          vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
          vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);
          const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

          render(Page, {
            props: { params: { partner_id: 'foo', item_type: 'bar' } },
          });

          // When
          await waitFor(async () => {
            const followupButton = screen.getByTestId('followup-button');
            await fireEvent.click(followupButton);
          });

          // Then
          expect(spyUrl).toHaveBeenCalledTimes(1);
          expect(spy).toHaveBeenCalledTimes(1);
          expect(spy).toHaveBeenCalledWith('/#/followup');
        });
      });
      describe('service button', () => {
        test('should redirect to service link - with non archived items', async () => {
          // Given
          await userStore.login(mockUserInfo);
          vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
          vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
            new ServicesItem(
              'psl',
              'MonService',
              'Opération Tranquillité Vacances',
              'Sécurisez votre logement !',
              'Vous partez en vacances ? **Securisez votre logement.**',
              'fake-link',
              true
            )
          );
          const spyUrl = vi
            .spyOn(ServicesItem.prototype, 'getServiceUrl')
            .mockResolvedValue('http://external-url');
          vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
          vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);
          vi.stubGlobal('location', {
            href: 'fake-link',
            hash: '',
            origin: 'http://localhost',
          });

          render(Page, {
            props: { params: { partner_id: 'foo', item_type: 'bar' } },
          });

          // When
          await waitFor(async () => {
            const serviceButton = screen.getByTestId('service-button');
            await fireEvent.click(serviceButton);
          });

          // Then
          expect(spyUrl).toHaveBeenCalledTimes(2);
          expect(window.location.href).toBe('http://external-url');
        });
        test('should redirect to service link - no non archived items', async () => {
          // Given
          await userStore.login(mockUserInfo);
          vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
          vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
            new ServicesItem(
              'psl',
              'MonService',
              'Opération Tranquillité Vacances',
              'Sécurisez votre logement !',
              'Vous partez en vacances ? **Securisez votre logement.**',
              'fake-link',
              true
            )
          );
          const spyUrl = vi
            .spyOn(ServicesItem.prototype, 'getServiceUrl')
            .mockResolvedValue('http://external-url');
          vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
          vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(false);
          vi.stubGlobal('location', {
            href: 'fake-link',
            hash: '',
            origin: 'http://localhost',
          });

          render(Page, {
            props: { params: { partner_id: 'foo', item_type: 'bar' } },
          });

          // When
          await waitFor(async () => {
            const serviceButton = screen.getByTestId('service-button');
            await fireEvent.click(serviceButton);
          });

          // Then
          expect(spyUrl).toHaveBeenCalledTimes(2);
          expect(window.location.href).toBe('http://external-url');
        });
      });
    });
  });
});
