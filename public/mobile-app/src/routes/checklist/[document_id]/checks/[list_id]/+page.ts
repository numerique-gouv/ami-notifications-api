import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
  return { list_id: params.list_id };
};
