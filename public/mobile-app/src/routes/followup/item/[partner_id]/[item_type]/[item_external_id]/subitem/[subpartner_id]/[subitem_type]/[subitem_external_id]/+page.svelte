<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import FollowupItemDetail from '$lib/components/followup/FollowupItemDetail.svelte';
  import FollowupParentItemDetail from '$lib/components/followup/FollowupParentItemDetail.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupItem, FollowupSubItem } from '$lib/followup';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data, params }: PageProps = $props();
  let item: FollowupItem | null = $state(null);
  let sub_item: FollowupSubItem | null = $state(null);

  let backUrl: string = $state('/#/followup');
  let checkedIcon: string = $state('');

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
    if (data.item && data.sub_item) {
      item = data.item as FollowupItem;
      sub_item = data.sub_item as FollowupSubItem;
      backUrl = item.getItemDetailPageUrl();
    }
  });
</script>

<NavWithBackButton {backUrl} />

{#if sub_item}
  <FollowupItemDetail item={sub_item} />
{/if}
