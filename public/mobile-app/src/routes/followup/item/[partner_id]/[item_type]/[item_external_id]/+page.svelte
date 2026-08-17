<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import FollowupItemDetail from '$lib/components/FollowupItemDetail.svelte';
  import FollowupParentItemDetail from '$lib/components/FollowupParentItemDetail.svelte';
  import NavWithBackButton from '$lib/components/NavWithBackButton.svelte';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupItem } from '$lib/followup';
  import { userStore } from '$lib/state/User.svelte';
  import type { PageProps } from './$types';

  let { data, params }: PageProps = $props();
  let item: FollowupItem | null = $state(null);

  let backUrl: string = $state('/#/followup');
  let checkedIcon: string = $state('');

  onMount(async () => {
    if (!userStore.connected) {
      goto('/#/login');
    }
    if (data.item) {
      item = data.item as FollowupItem;
      backUrl = item.is_archived ? '/#/followup/archived' : '/#/followup';
    }
  });
</script>

<NavWithBackButton {backUrl} />

{#if item}
  {#if item.sub_items.length}
    <FollowupParentItemDetail item={item} />
  {:else}
    <FollowupItemDetail item={item} />
  {/if}
{/if}
