<script lang="ts">
  import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';
  import FollowupItemMessages from '$lib/components/followup/FollowupItemMessages.svelte';
  import { FollowupSubItem } from '$lib/followup';

  interface Props {
    item: FollowupSubItem;
  }
  let { item }: Props = $props();
</script>

<div class="demarche-content-container">
  <FollowupItemDetailHeader item={item} />

  <FollowupItemMessages item={item} displayTitle={false} />
</div>

<style>
  div.demarche-content-container {
    padding: 4rem 1rem 1rem;
  }
</style>
