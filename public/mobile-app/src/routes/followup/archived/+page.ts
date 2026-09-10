import type { Consents } from '$lib/consents';
import { buildConsents } from '$lib/consents';
import type { Followup } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const followup: Followup = await buildFollowup();
  const isFollowupEmpty: boolean = !followup.items.length;
  const consents: Consents = await buildConsents();
  const hasAnyConsents: boolean = consents.hasAnyConsents();

  return { followup, isFollowupEmpty, hasAnyConsents };
};
