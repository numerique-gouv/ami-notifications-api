import type { Followup, FollowupItem } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  const partner_id: string = params.partner_id;
  const item_type: string = params.item_type;
  const item_external_id: string = params.item_external_id;

  const followup: Followup = await buildFollowup();
  const item: FollowupItem | null = followup.findItem(
    partner_id,
    item_type,
    item_external_id
  );

  return { item };
};
