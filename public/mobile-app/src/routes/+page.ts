import { page } from '$app/state';
import { AMIGoto } from '$lib/ami-navigation';
import type { Consents } from '$lib/consents';
import { buildConsents } from '$lib/consents';
import { buildFollowup, type Followup } from '$lib/followup';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  if (page.url.searchParams.has('is_logged_out')) {
    AMIGoto('/?is_logged_out#/login');
    return;
  }

  if (!userStore.connected) {
    AMIGoto('/#/login');
    return;
  }

  if (page.url.searchParams.has('passkey_toast')) {
    toastStore.addToast('La clé a bien été ajoutée', 'success', 3000, false);
  }
  if (page.url.searchParams.has('user_does_not_match')) {
    toastStore.addToast(
      'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
      'warning',
      null,
      true
    );
    const hash = page.url.searchParams.get('redirect_to_hash') || '';
    if (hash !== '') {
      AMIGoto(`/#${hash}`);
      return;
    }
  }

  const followup: Followup = await buildFollowup();
  const isFollowupEmpty: boolean = followup.isEmpty();
  const consents: Consents = await buildConsents();
  const hasAnyConsents: boolean = consents.hasAnyConsents();

  return { followup, isFollowupEmpty, hasAnyConsents };
};
