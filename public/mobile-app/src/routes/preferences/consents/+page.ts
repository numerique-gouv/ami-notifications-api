import { buildConsents, type Consents, type ConsentsItem } from '$lib/consents';
import { buildPartners, type Partners } from '$lib/partners';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const consents: Consents = await buildConsents();
  const consentItems: ConsentsItem[] | undefined = consents.items;
  const partners: Partners | null = await buildPartners();

  return { consentItems: consentItems, partners: partners };
};
