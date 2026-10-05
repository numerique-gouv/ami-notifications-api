import { AMIGoto } from '$lib/ami-navigation';
import type { Consents } from '$lib/consents';
import { buildConsents } from '$lib/consents';
import { buildFollowup, type Followup } from '$lib/followup';
import type { Partners } from '$lib/partners';
import { buildPartners } from '$lib/partners';
import { toastStore } from '$lib/state/toast.svelte';
import { userStore } from '$lib/state/User.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  const searchParams = new URLSearchParams(window?.location?.search || '');

  if (!userStore.connected) {
    AMIGoto('/#/login');
    return;
  }

  if (searchParams.has('passkey_toast')) {
    toastStore.addToast('La clé a bien été ajoutée', 'success', 3000, false);
  }
  if (searchParams.has('user_does_not_match')) {
    toastStore.addToast(
      'Vous ne pouvez pas continuer la démarche sous le compte d’un autre usager',
      'warning',
      null,
      true
    );
    const hash = searchParams.get('redirect_to_hash') || '';
    if (hash !== '') {
      AMIGoto(`/#${hash}`);
      return;
    }
  }

  const followup: Followup = await buildFollowup();
  const isFollowupEmpty: boolean = followup.isEmpty();
  const partners: Partners = await buildPartners();
  const consents: Consents = await buildConsents(partners);
  const hasAnyConsents: boolean = consents.hasAnyConsents();

  return { followup, isFollowupEmpty, hasAnyConsents };
};
