import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as servicesMethods from '$lib/services';
import { Services, ServicesItem } from '$lib/services';
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
  test('Should display services', async () => {
    // Given
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
});
