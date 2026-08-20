import { describe, expect, test, vi } from 'vitest';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem, FollowupSubItem } from '$lib/followup';
import { load } from './+page';

describe('/+page.ts', () => {
  test("load should call followup's findItem method and FollowupItem findSubItem method", async () => {
    // Given
    const sub_item = new FollowupSubItem(
      'subpartner',
      'subtype',
      'subid',
      'ref',
      'notifications',
      [],
      'title',
      'subheading',
      'description',
      'icon',
      new Date('2026-01-03T08:05:42Z'),
      'new',
      'new',
      false,
      null
    );
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
      [sub_item]
    );
    const followup = new Followup();
    const spy = vi.spyOn(followup, 'findItem').mockReturnValue(item);
    const spy2 = vi.spyOn(item, 'findSubItem').mockReturnValue(sub_item);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    const params = {
      partner_id: 'partner',
      item_type: 'type',
      item_external_id: 'id',
      subpartner_id: 'subpartner',
      subitem_type: 'subtype',
      subitem_external_id: 'subid',
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
    expect(spy2).toHaveBeenCalledWith('subpartner', 'subtype', 'subid');
  });
});
