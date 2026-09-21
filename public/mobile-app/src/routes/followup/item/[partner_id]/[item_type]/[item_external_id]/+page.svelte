<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupItemDetail from '$lib/components/followup/FollowupItemDetail.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { FollowupItem } from '$lib/followup';
  import type { Services } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data, params }: PageProps = $props();
  let item: FollowupItem | null = $state(null);
  let services: Services | null = $state(null);

  let backUrl: string = $state('/#/followup');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
    if (data.item) {
      item = data.item as FollowupItem;
      backUrl = item.is_archived ? '/#/followup/archived' : '/#/followup';
    }
    if (data.services) {
      services = data.services as Services;
    }
  });
</script>

<NavWithBackButton {backUrl} />

{#if item && services}
  <FollowupItemDetail item={item} services={services} />
{/if}
