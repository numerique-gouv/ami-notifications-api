import { describe, expect, test, vi } from 'vitest';
import * as consentsMethods from '$lib/consents';
import * as followupMethods from '$lib/followup';
import '@testing-library/jest-dom/vitest';
import type { APIPartnersItem } from '$lib/api-partners';
import { Consents } from '$lib/consents';
import { Followup } from '$lib/followup';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should call build consents, followup and partners', async () => {
    // Given
    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    vi.spyOn(followup, 'isEmpty').mockReturnValue(false);

    const apiPartnersItem: APIPartnersItem = {
      slug: 'dinum-ami',
      name: 'AMI',
      link: 'http://fake-link-1',
    };
    const partners = new Partners([apiPartnersItem]);
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

    const consentsItem = {
      partner_id: 'dinum-ami',
      partner_name: 'AMI',
      consent_datetime: new Date('2026-02-21T15:50:00Z'),
    };
    const consents = new Consents({ consents: [consentsItem] }, partners.items);
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);

    vi.spyOn(consents, 'hasAnyConsents').mockReturnValue(true);
    vi.spyOn(consents, 'hasAllConsents').mockReturnValue(false);

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
    expect(result.hasAllConsents).toEqual(false);
    // @ts-expect-error
    expect(result.partners).toEqual(partners);
  });
});
