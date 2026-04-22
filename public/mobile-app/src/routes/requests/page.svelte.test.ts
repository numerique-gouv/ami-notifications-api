import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(new FollowUp());

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(window.location.href).toEqual('/');
    });
  });
  test('Should display requests from API', async () => {
    // Given
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'current', 'get').mockReturnValue([
      new RequestItem(
        'Opération Tranquillité Vacances',
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
        'Opération Tranquillité Vacances',
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
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('requests-current')).toHaveTextContent(
        'Votre demande est en cours de traitement.'
      );
      expect(screen.getByTestId('requests-current')).not.toHaveTextContent(
        'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
      );
      expect(screen.getByTestId('requests-past')).toHaveTextContent(
        'Votre demande est terminée.'
      );
      expect(screen.getByTestId('requests-past')).not.toHaveTextContent(
        'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
      );
    });
  });
  test('Should display empty tabs', async () => {
    // Given
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'current', 'get').mockReturnValue([]);
    vi.spyOn(followUp, 'past', 'get').mockReturnValue([]);
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('requests-current')).toHaveTextContent(
        'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
      );
      expect(screen.getByTestId('requests-past')).toHaveTextContent(
        'Après avoir effectué vos démarches, vous pouvez les suivre en temps réel depuis l’application.'
      );
    });
  });
});
