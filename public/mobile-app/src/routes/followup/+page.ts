import { hasAnyConsents as hasAnyConsentsFunc } from '$lib/consents';
import type { Followup } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import { buildPartners, type Partners } from '$lib/partners';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const followup: Followup | null = await buildFollowup();
  const isFollowupEmpty: boolean = !followup.items.length;
  const hasAnyConsents: boolean = await hasAnyConsentsFunc();
  const partners: Partners | null = await buildPartners();

  return { followup, isFollowupEmpty, hasAnyConsents, partners };
};
