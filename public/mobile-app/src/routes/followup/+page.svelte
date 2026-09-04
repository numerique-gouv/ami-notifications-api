<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import Followup from '$lib/components/followup/Followup.svelte';
  import Navigation from '$lib/components/Navigation.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
  });
</script>

<Navigation currentItem="followup" />
<Followup
  followupProp="{data.followup}"
  isFollowupEmptyProp="{data.isFollowupEmpty}"
  hasAnyConsentsProp="{data.hasAnyConsents}"
  partnersProp="{data.partners}"
/>
