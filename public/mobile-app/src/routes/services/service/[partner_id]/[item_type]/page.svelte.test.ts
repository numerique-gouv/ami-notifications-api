import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as servicesMethods from '$lib/services';
import { Services, ServicesItem } from '$lib/services';
import { userStore } from '$lib/state/User.svelte';
import { expectBackButtonPresent, mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(servicesMethods, 'buildServices').mockResolvedValue(new Services());
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
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();
    vi.spyOn(Services.prototype, 'find').mockReturnValueOnce(
      new ServicesItem(
        'psl',
        'OperationTranquilliteVacances',
        'Opération Tranquillité Vacances',
        'Sécurisez votre logement !',
        'Vous partez en vacances ? **Securisez votre logement.**',
        'http://external-url',
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
        'http://external-url',
        true
      )
    );

    // When
    render(Page, {
      props: { params: { partner_id: 'foo', item_type: 'bar' } },
    });

    // Then
    await waitFor(() => {
      expectBackButtonPresent(screen);
    });
  });
});
