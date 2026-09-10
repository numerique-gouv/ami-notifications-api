import { describe, expect, test, vi } from 'vitest';
import * as consentsMethods from '$lib/consents';
import * as followupMethods from '$lib/followup';
import '@testing-library/jest-dom/vitest';
import { Consents } from '$lib/consents';
import { Followup } from '$lib/followup';
import { load } from './+page';

describe('/+page.ts', () => {
  test('load should call build consents and followup', async () => {
    // Given
    const followup = new Followup();
    vi.spyOn(followup, 'items', 'get').mockReturnValue([]);
    vi.spyOn(followupMethods, 'buildFollowup').mockResolvedValue(followup);
    vi.spyOn(followup, 'isEmpty').mockReturnValue(false);
    const consents = new Consents();
    vi.spyOn(consentsMethods, 'buildConsents').mockResolvedValue(consents);
    vi.spyOn(consents, 'hasAnyConsents').mockReturnValue(true);

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
  });
});
