import type { Followup, FollowupItem } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import type { PageLoad } from './$types';

const findItem = (
  source: FollowupItem[],
  partner_id: string,
  item_type: string,
  item_external_id: string
) =>
  source.find(
    (item) =>
      item.partner_id === partner_id &&
      item.item_type === item_type &&
      item.item_external_id === item_external_id
  );

export const load: PageLoad = async ({ params }) => {
  const partner_id: string = params.partner_id;
  const item_type: string = params.item_type;
  const item_external_id: string = params.item_external_id;

  const followup: Followup = await buildFollowup();

  let item: FollowupItem | undefined;

  item = findItem(followup.items, partner_id, item_type, item_external_id);

  if (!item) {
    item = findItem(followup.archived_items, partner_id, item_type, item_external_id);
  }

  return { item };
};
