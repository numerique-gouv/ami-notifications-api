import { buildConsents, type Consents, type ConsentsItem } from '$lib/consents';
import type { Followup } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import { buildPartners, type Partners } from '$lib/partners';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const partners: Partners | null = await buildPartners();
  const consents: Consents = await buildConsents(partners);
  const consentItems: ConsentsItem[] | undefined = consents.items;
  const followup: Followup | null = await buildFollowup();

  return {
    consentItems: consentItems,
    partners: partners,
    followup: followup,
  };
};
