import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as AMINavigationMethods from '$lib/ami-navigation';
import { type User, userStore } from '$lib/state/User.svelte';
import type { FoyerData as FoyerDataType } from '$lib/user-data';
import { mockUserInfo } from '$tests/utils';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/#/login');
    });
  });

  test('redirect to silent login if there is no data yet', async () => {
    // Given
    await userStore.login(mockUserInfo);
    const spy = vi.spyOn(AMINavigationMethods, 'AMIGoto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('foyer-undefined')).not.toBeNull();
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/silent-login-ami-fi?data-mode=foyer');
    });
  });

  test('should display text if there is no foyer data', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(<User>userStore.connected, 'getFoyer').mockReturnValue(null);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('foyer-null')).not.toBeNull();
    });
  });

  test('should display foyer data', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(<User>userStore.connected, 'getFoyer').mockReturnValue(<FoyerDataType>{
      enfants: [],
      quotient_familial: {
        fournisseur: 'CAF',
        valeur: 2550,
        annee: 2024,
        mois: 2,
        annee_calcul: 2024,
        mois_calcul: 12,
      },
    });

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('foyer-null')).toBeNull();
      expect(screen.queryByTestId('foyer-data')).toHaveTextContent('pas d’enfants');
    });
  });

  test('should display foyer data (children)', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(<User>userStore.connected, 'getFoyer').mockReturnValue(<FoyerDataType>{
      enfants: [
        {
          nom_naissance: 'DUBOIS',
          nom_usage: null,
          prenoms: 'PIERRE',
          date_naissance: '2004-01-10',
          sexe: 'M',
        },
      ],
      quotient_familial: {
        fournisseur: 'CAF',
        valeur: 2550,
        annee: 2024,
        mois: 2,
        annee_calcul: 2024,
        mois_calcul: 12,
      },
    });

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('foyer-null')).toBeNull();
      expect(screen.queryByTestId('foyer-data')).toHaveTextContent('né le 10/01/2004');
    });
  });

  test('should display foyer data (qf)', async () => {
    // Given
    await userStore.login(mockUserInfo);
    vi.spyOn(<User>userStore.connected, 'getFoyer').mockReturnValue(<FoyerDataType>{
      enfants: [],
      quotient_familial: {
        fournisseur: 'CAF',
        valeur: 2550,
        annee: 2024,
        mois: 2,
        annee_calcul: 2024,
        mois_calcul: 12,
      },
    });

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(screen.queryByTestId('foyer-null')).toBeNull();
      expect(screen.queryByTestId('foyer-data')).toHaveTextContent('février 2024');
    });
  });
});
