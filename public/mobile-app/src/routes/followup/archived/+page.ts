import { hasAnyConsents as hasAnyConsentsFunc } from '$lib/consents';
import type { Followup } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const followup: Followup | null = await buildFollowup();
  const isFollowupEmpty: boolean = !followup.archived_items.length;
  const hasAnyConsents: boolean = await hasAnyConsentsFunc();

  return { followup, isFollowupEmpty, hasAnyConsents };
};
