import { describe, expect, test, vi } from 'vitest';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem, FollowupItemEvent } from '$lib/followup';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should return non archived item when url does not have is_archived query param', async () => {
    // Given
    window.location.hash = '#/followup';

    const event = new FollowupItemEvent(
      'event-id',
      new Date('2026-02-03T08:05:42Z'),
      'lorem ipsum'
    );
    const nonArchivedItem = new FollowupItem(
      'partner',
      'partner-name',
      'type',
      'id1',
      'notifications',
      [event],
      'Opération Tranquillité Vacances',
      'Votre demande est en cours de traitement.',
      'icon',
      new Date('2026-02-22T15:55:00.000Z'),
      'wip',
      'En cours',
      false,
      null
    );
    const archivedItem = new FollowupItem(
      'partner',
      'partner-name',
      'type',
      'id2',
      'notifications',
      [event],
      'Opération Tranquillité Vacances',
      'Votre demande est terminée.',
      'icon',
      new Date('2026-02-20T15:55:00.000Z'),
      'closed',
      'Terminée',
      true,
      null
    );
    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([nonArchivedItem]);
    vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([archivedItem]);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id1',
    };

    // When
    // @ts-expect-error
    const result = await load({
      params: params,
    });

    // Then
    // @ts-expect-error
    expect(result.item).toEqual(nonArchivedItem);
  });
  test('load should return archived item when url has is_archived query param', async () => {
    // Given
    window.location.hash = '#/followup/archived';

    const event = new FollowupItemEvent(
      'event-id',
      new Date('2026-02-03T08:05:42Z'),
      'lorem ipsum'
    );
    const nonArchivedItem = new FollowupItem(
      'partner',
      'partner-name',
      'type',
      'id1',
      'notifications',
      [event],
      'Opération Tranquillité Vacances',
      'Votre demande est en cours de traitement.',
      'icon',
      new Date('2026-02-22T15:55:00.000Z'),
      'wip',
      'En cours',
      false,
      null
    );
    const archivedItem = new FollowupItem(
      'partner',
      'partner-name',
      'type',
      'id2',
      'notifications',
      [event],
      'Opération Tranquillité Vacances',
      'Votre demande est terminée.',
      'icon',
      new Date('2026-02-20T15:55:00.000Z'),
      'closed',
      'Terminée',
      true,
      null
    );
    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([nonArchivedItem]);
    vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([archivedItem]);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id2',
    };

    // When
    // @ts-expect-error
    const result = await load({
      params: params,
    });

    // Then
    // @ts-expect-error
    expect(result.item).toEqual(archivedItem);
  });
});
