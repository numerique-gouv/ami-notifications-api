import { describe, expect, test, vi } from 'vitest';
import type { APIPartnersItem } from '$lib/api-partners';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import * as followupMethods from '$lib/followup';
import { Followup } from '$lib/followup';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should call consents and partners method', async () => {
    // Given
    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link-1',
    };
    const partners = new Partners([apiPartnersItem]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

    const consentsItem = {
      partner_id: 'dinum-ami',
      consent_datetime: new Date('2026-02-21T15:50:00Z'),
    };
    const consents = new Consents({ consents: [consentsItem] }, ['dinum-ami']);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

    const followup = new Followup();
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);

    const displayWarningBlocks = new Map<string, boolean>();
    displayWarningBlocks.set('dinum-ami', false);

    // When
    // @ts-expect-error
    const result = await load({});

    // Then
    // @ts-expect-error
    expect(result.consentItems).toEqual(consents.items);
    // @ts-expect-error
    expect(result.partners).toEqual(partners);
    // @ts-expect-error
    expect(result.followup).toEqual(followup);
    // @ts-expect-error
    expect(result.displayWarningBlocks).toEqual(displayWarningBlocks);
  });
});
