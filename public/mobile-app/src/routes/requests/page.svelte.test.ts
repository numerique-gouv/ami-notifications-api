import { render, screen, waitFor } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';
import * as navigationMethods from '$app/navigation';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import Page from './+page.svelte';

describe('/+page.svelte', () => {
  test('user has to be connected', async () => {
    // Given
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
  test('Should display current followup', async () => {
    // Given
    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([
      new FollowupItem(
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
    vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
      new FollowupItem(
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
    const spy = vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    // When
    render(Page);

    // Then
    await waitFor(() => {
      expect(spy).toHaveBeenCalledTimes(1);
      expect(screen.getByTestId('followup')).toHaveTextContent(
        'Votre demande est en cours de traitement.'
      );
      expect(screen.getByTestId('followup')).not.toHaveTextContent(
        'Votre demande est terminée.'
      );
    });
  });
});
