import { describe, expect, test, vi } from 'vitest';
import * as partnersMethods from '$lib/partners';
import { Partners } from '$lib/partners';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should call partners method', async () => {
    // Given
    const partners = new Partners();
    vi.spyOn(partnersMethods, 'buildPartners').mockResolvedValue(partners);

    // When
    // @ts-expect-error
    const result = await load({});

    // Then
    // @ts-expect-error
    expect(result.partners).toEqual(partners);
  });
});
