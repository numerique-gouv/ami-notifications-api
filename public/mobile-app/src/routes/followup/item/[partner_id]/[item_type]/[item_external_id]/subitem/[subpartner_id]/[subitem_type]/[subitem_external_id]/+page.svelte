<script lang="ts">
  import { onMount } from 'svelte';
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupItemDetail from '$lib/components/followup/FollowupItemDetail.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { FollowupItem, FollowupSubItem } from '$lib/followup';
  import type { Services } from '$lib/services';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data, params }: PageProps = $props();
  let item: FollowupItem | null = $state(null);
  let sub_item: FollowupSubItem | null = $state(null);
  let services: Services | null = $state(null);

  let backUrl: string = $state('/#/followup');

  onMount(async () => {
    if (!userStore.connected) {
      AMIGoto('/#/login');
    }
    if (data.item && data.sub_item) {
      item = data.item as FollowupItem;
      sub_item = data.sub_item as FollowupSubItem;
      backUrl = item.getItemDetailPageUrl();
    }
    if (data.services) {
      services = data.services as Services;
    }
  });
</script>

<NavWithBackButton {backUrl} />

{#if sub_item && item && services}
  <FollowupItemDetail item={sub_item} parentItem={item} services={services} />
{/if}
