import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as followUpMethods from '$lib/follow-up';
import { FollowUp, RequestItem } from '$lib/follow-up';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
    vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(new FollowUp());
    const spy = vi.spyOn(navigationMethods, 'goto').mockResolvedValue();

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(spy).toHaveBeenCalledWith('/');
    });
  });
  test('Should display current requests', async () => {
    // Given
    const followUp = new FollowUp();
    vi.spyOn(followUp, 'items', 'get').mockReturnValue([
      new RequestItem(
        'partner',
        'type',
        'id1',
        'notifications',
        'Opération Tranquillité Vacances',
        'Votre demande est en cours de traitement.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'wip',
        'En cours',
        false,
        null
      ),
    ]);
    vi.spyOn(followUp, 'archived_items', 'get').mockReturnValue([
      new RequestItem(
        'partner',
        'type',
        'id2',
        'notifications',
        'Opération Tranquillité Vacances',
        'Votre demande est terminée.',
        'icon',
        new Date('2026-02-20T15:55:00.000Z'),
        'closed',
        'Terminée',
        true,
        null
      ),
    ]);
    const spy = vi.spyOn(followUpMethods, 'buildFollowUp').mockResolvedValue(followUp);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('requests')).toHaveTextContent(
        'Votre demande est en cours de traitement.'
      );
      expect(screen.getByTestId('requests')).not.toHaveTextContent(
        'Votre demande est terminée.'
      );
    });
  });
});
