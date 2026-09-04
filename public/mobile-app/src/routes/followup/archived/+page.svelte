<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import Followup from '$lib/components/followup/Followup.svelte';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data }: PageProps = $props();

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
  });
</script>

<Followup
  archived={true}
  followupProp="{data.followup}"
  isFollowupEmptyProp="{data.isFollowupEmpty}"
  hasAnyConsentsProp="{data.hasAnyConsents}"
  partnersProp="{data.partners}"
/>
