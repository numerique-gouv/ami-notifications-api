import { describe, expect, test, vi } from 'vitest';
import * as consentsMethods from '$lib/consents';
import { Consents } from '$lib/consents';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should call consents and partners method', async () => {
    // Given
    const consents = new Consents();
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
    const partners = new Partners();
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

    // When
    // @ts-expect-error
    const result = await load({});

    // Then
    // @ts-expect-error
    expect(result.consentItems).toEqual(consents.items);
    // @ts-expect-error
    expect(result.partners).toEqual(partners);
  });
});
