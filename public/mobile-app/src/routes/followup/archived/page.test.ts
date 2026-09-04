import { describe, expect, test, vi } from 'vitest';
import * as consentsMethods from '$lib/consents';
import * as followupMethods from '$lib/followup';
import { Followup, FollowupItem } from '$lib/followup';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should call followup and partners methods', async () => {
    // Given
    const followup = new Followup();
    vi.spyOn(followup, 'archived_items', 'get').mockReturnValue([
      new FollowupItem(
        'partner',
        'type',
        'id1',
        'ref1',
        'notifications',
        [],
        'Opération Tranquillité Vacances 1',
        'subheading',
        'Votre demande est en cours de traitement.',
        'icon',
        new Date('2026-02-22T15:55:00.000Z'),
        'wip',
        'En cours',
        false,
        null,
        []
      ),
    ]);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    vi.spyOn(consentsMethods, 'hasAnyConsents').mockResolvedValue(true);
    const partners = new Partners();
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

    // When
    // @ts-expect-error
    const result = await load({});

    // Then
    // @ts-expect-error
    expect(result.followup).toEqual(followup);
    // @ts-expect-error
    expect(result.isFollowupEmpty).toEqual(false);
    // @ts-expect-error
    expect(result.hasAnyConsents).toEqual(true);
    // @ts-expect-error
    expect(result.partners).toEqual(partners);
  });
});
