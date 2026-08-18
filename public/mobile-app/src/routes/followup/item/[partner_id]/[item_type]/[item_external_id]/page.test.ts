import { describe, expect, test, vi } from 'vitest';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import { load } from './+page';

describe('/+page.ts', () => {
  test("load should call followup's findItem method", async () => {
    // Given

    const item = new FollowupItem(
      'partner',
      'type',
      'id',
      'ref',
      'notifications',
      [],
      'Opération Tranquillité Vacances',
      'subheading',
      'Votre demande est terminée.',
      'icon',
      new Date('2026-02-20T15:55:00.000Z'),
      'closed',
      'Terminée',
      false,
      null,
      []
    );
    const followup = new Followup();
    const spy = vi.spyOn(followup, 'findItem').mockReturnValue(item);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
    };

    // When
    // @ts-expect-error
    const result = await load({
      params: params,
    });

    // Then
    // @ts-expect-error
    expect(result.item).toEqual(item);
    expect(spy).toHaveBeenCalledTimes(1);
    expect(spy).toHaveBeenCalledWith('partner', 'type', 'id');
  });
});
