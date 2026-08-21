import type { Followup, FollowupItem, FollowupSubItem } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  const partner_id: string = params.partner_id;
  const item_type: string = params.item_type;
  const item_external_id: string = params.item_external_id;
  const subpartner_id: string = params.subpartner_id;
  const subitem_type: string = params.subitem_type;
  const subitem_external_id: string = params.subitem_external_id;

  const followup: Followup = await buildFollowup();
  const item: FollowupItem | null = followup.findItem(
    partner_id,
    item_type,
    item_external_id
  );
  let sub_item: FollowupSubItem | null = null;
  if (item) {
    sub_item = item.findSubItem(subpartner_id, subitem_type, subitem_external_id);
  }

  return { item, sub_item };
};
