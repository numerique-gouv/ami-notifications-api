import { buildPartners, type Partners } from '$lib/partners';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const partners: Partners | null = await buildPartners();

  return { partners };
};
