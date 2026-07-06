import type { Followup, FollowupItem } from '$lib/followup';
import { buildFollowup } from '$lib/followup';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  const is_archived = window.location.hash === '#/followup/archived';
  const partner_id: string = params.partner_id;
  const item_type: string = params.item_type;
  const item_external_id: string = params.item_external_id;

  const followup: Followup = await buildFollowup();

  const source: FollowupItem[] = is_archived ? followup.archived_items : followup.items;
  let item: FollowupItem | undefined;

  item = source.find(
    (item) =>
      item.partner_id === partner_id &&
      item.item_type === item_type &&
      item.item_external_id === item_external_id
  );

  return { item };
};
