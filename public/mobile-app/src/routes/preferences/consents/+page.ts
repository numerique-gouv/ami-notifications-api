import { buildConsents, type Consents, type ConsentsItem } from '$lib/consents';
import type { Followup } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import { buildPartners, type Partners, type PartnersItem } from '$lib/partners';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const partners: Partners | null = await buildPartners();
  const partnerIds: string[] = partners.items.map((item: PartnersItem) => item.slug);
  const consents: Consents = await buildConsents(partnerIds);
  const consentItems: ConsentsItem[] | undefined = consents.items;
  const followup: Followup | null = await buildFollowup();
  const displayWarningBlocks = new Map<string, boolean>();
  consentItems.forEach((consentItem: ConsentsItem) => {
    displayWarningBlocks.set(consentItem.partner_id, false);
  });

  return {
    consentItems: consentItems,
    partners: partners,
    followup: followup,
    displayWarningBlocks: displayWarningBlocks,
  };
};
