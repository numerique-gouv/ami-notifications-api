import type { Consents } from '$lib/consents';
import { buildConsents } from '$lib/consents';
import type { Followup } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import { buildPartners, type Partners, type PartnersItem } from '$lib/partners';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const followup: Followup = await buildFollowup();
  const isFollowupEmpty: boolean = followup.isEmpty();
  const partners: Partners | null = await buildPartners();
  const partnerIds: string[] = partners.items.map((item: PartnersItem) => item.slug);
  const consents: Consents = await buildConsents(partnerIds);
  const hasAnyConsents: boolean = consents.hasAnyConsents();
  const hasAllConsents: boolean = consents.hasAllConsents();

  return { followup, isFollowupEmpty, hasAnyConsents, hasAllConsents, partners };
};
