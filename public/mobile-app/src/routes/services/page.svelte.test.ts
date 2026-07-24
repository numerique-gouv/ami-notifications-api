import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMIGotoMethods from '$lib/ami-goto';
import * as followupMethods from '$lib/followup';
import { Followup } from '$lib/followup';
import * as servicesMethods from '$lib/services';
import { Services, ServicesItem } from '$lib/services';
import { userStore } from '$lib/state/User.svelte';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
    const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
  test('Should display services', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const services = new Services();
    vi.spyOn(services, 'items', 'get').mockReturnValue([
      new ServicesItem(
        'psl',
        'OperationTranquilliteVacances',
        'Opération Tranquillité Vacances',
        'Sécurisez votre logement',
        'Vous partez en vacances ? **Securisez votre logement.**',
        'http://external-url',
        true
      ),
    ]);
    const spy = vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('services')).toHaveTextContent(
        'Opération Tranquillité Vacances'
      );
      expect(screen.getByTestId('services')).toHaveTextContent(
        'Sécurisez votre logement'
      );
      expect(screen.getByTestId('services')).not.toHaveTextContent(
        'Vous partez en vacances ? **Securisez votre logement.**'
      );
    });
  });
  describe('click on service', () => {
    describe('no non archived items', async () => {
      test('should redirect to service link - without silent-login', async () => {
        // Given
        await userStore.login(mockUserInfo);
        const services = new Services();
        vi.spyOn(services, 'items', 'get').mockReturnValue([
          new ServicesItem(
            'psl',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'http://external-url',
            false
          ),
        ]);
        vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);
        const spyUrl = vi
          .spyOn(ServicesItem.prototype, 'getServiceUrl')
          .mockResolvedValue('http://external-url');
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
        vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(false);
        const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

        render(Page);

        // When
        await waitFor(async () => {
          const link = screen.getByTestId('service-psl:OperationTranquilliteVacances');
          await fireEvent.click(link);
        });

        // Then
        expect(screen.queryByTestId('service-button')).toBeNull();
        expect(screen.queryByTestId('followup-button')).toBeNull();
        expect(spyUrl).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('http://external-url', false);
      });
      test('should redirect to service link - with silent-login', async () => {
        // Given
        await userStore.login(mockUserInfo);
        const services = new Services();
        vi.spyOn(services, 'items', 'get').mockReturnValue([
          new ServicesItem(
            'psl',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'http://external-url',
            true
          ),
        ]);
        vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);
        const spyUrl = vi
          .spyOn(ServicesItem.prototype, 'getServiceUrl')
          .mockResolvedValue('http://external-url');
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
        vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(false);
        const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

        render(Page);

        // When
        await waitFor(async () => {
          const link = screen.getByTestId('service-psl:OperationTranquilliteVacances');
          await fireEvent.click(link);
        });

        // Then
        expect(screen.queryByTestId('service-button')).toBeNull();
        expect(screen.queryByTestId('followup-button')).toBeNull();
        expect(spyUrl).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('http://external-url', true);
      });
    });
    describe('with non archived items', () => {
      test('buttons display', async () => {
        // Given
        await userStore.login(mockUserInfo);
        const services = new Services();
        vi.spyOn(services, 'items', 'get').mockReturnValue([
          new ServicesItem(
            'psl',
            'OperationTranquilliteVacances',
            'Opération Tranquillité Vacances',
            'Sécurisez votre logement',
            'Vous partez en vacances ? **Securisez votre logement.**',
            'http://external-url',
            true
          ),
        ]);
        vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);
        vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(new Followup());
        vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);

        render(Page);

        // When
        await waitFor(async () => {
          const link = screen.getByTestId('service-psl:OperationTranquilliteVacances');
          await fireEvent.click(link);
        });

        expect(screen.queryByTestId('service-button')).not.toBeNull();
        expect(screen.queryByTestId('followup-button')).not.toBeNull();
      });
      describe('buttons onclick', () => {
        describe('followup button', () => {
          test('should redirect to followup', async () => {
            // Given
            await userStore.login(mockUserInfo);
            const services = new Services();
            vi.spyOn(services, 'items', 'get').mockReturnValue([
              new ServicesItem(
                'psl',
                'OperationTranquilliteVacances',
                'Opération Tranquillité Vacances',
                'Sécurisez votre logement',
                'Vous partez en vacances ? **Securisez votre logement.**',
                'http://external-url',
                true
              ),
            ]);
            vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);
            vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(
              new Followup()
            );
            vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);
            const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

            render(Page);

            await waitFor(async () => {
              const link = screen.getByTestId(
                'service-psl:OperationTranquilliteVacances'
              );
              await fireEvent.click(link);
            });

            // When
            await waitFor(async () => {
              const followupButton = screen.getByTestId('followup-button');
              await fireEvent.click(followupButton);
            });

            // Then
            expect(spy).toHaveBeenCalledTimes(1);
            expect(spy).toHaveBeenCalledWith('/#/followup');
          });
        });
        describe('service button', () => {
          test('should redirect to service link - without silent-login', async () => {
            // Given
            await userStore.login(mockUserInfo);
            const services = new Services();
            vi.spyOn(services, 'items', 'get').mockReturnValue([
              new ServicesItem(
                'psl',
                'OperationTranquilliteVacances',
                'Opération Tranquillité Vacances',
                'Sécurisez votre logement',
                'Vous partez en vacances ? **Securisez votre logement.**',
                'http://external-url',
                false
              ),
            ]);
            vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);
            const spyUrl = vi
              .spyOn(ServicesItem.prototype, 'getServiceUrl')
              .mockResolvedValue('http://external-url');
            vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(
              new Followup()
            );
            vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);
            const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

            render(Page);

            await waitFor(async () => {
              const link = screen.getByTestId(
                'service-psl:OperationTranquilliteVacances'
              );
              await fireEvent.click(link);
            });

            // When
            await waitFor(async () => {
              const serviceButton = screen.getByTestId('service-button');
              await fireEvent.click(serviceButton);
            });

            // Then
            expect(spyUrl).toHaveBeenCalledTimes(1);
            expect(spy).toHaveBeenCalledTimes(1);
            expect(spy).toHaveBeenCalledWith('http://external-url', false);
          });
          test('should redirect to service link - with silent-login', async () => {
            // Given
            await userStore.login(mockUserInfo);
            const services = new Services();
            vi.spyOn(services, 'items', 'get').mockReturnValue([
              new ServicesItem(
                'psl',
                'OperationTranquilliteVacances',
                'Opération Tranquillité Vacances',
                'Sécurisez votre logement',
                'Vous partez en vacances ? **Securisez votre logement.**',
                'http://external-url',
                true
              ),
            ]);
            vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(services);
            const spyUrl = vi
              .spyOn(ServicesItem.prototype, 'getServiceUrl')
              .mockResolvedValue('http://external-url');
            vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(
              new Followup()
            );
            vi.spyOn(Followup.prototype, 'hasNonArchivedItems').mockReturnValue(true);
            const spy = vi.spyOn(AMIGotoMethods, 'AMIGoto').mockResolvedValue();

            render(Page);

            await waitFor(async () => {
              const link = screen.getByTestId(
                'service-psl:OperationTranquilliteVacances'
              );
              await fireEvent.click(link);
            });

            // When
            await waitFor(async () => {
              const serviceButton = screen.getByTestId('service-button');
              await fireEvent.click(serviceButton);
            });

            // Then
            expect(spyUrl).toHaveBeenCalledTimes(1);
            expect(spy).toHaveBeenCalledTimes(1);
            expect(spy).toHaveBeenCalledWith('http://external-url', true);
          });
        });
      });
    });
  });
});
