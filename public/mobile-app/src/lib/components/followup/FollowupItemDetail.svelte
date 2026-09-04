<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';
  import FollowupItemDetailHeader from '$lib/components/followup/FollowupItemDetailHeader.svelte';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupSubItem } from '$lib/followup';

  interface Props {
    item: FollowupSubItem;
  }
  let { item }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(item.icon, 'fr-icon-information-fill'));
</script>

<div class="demarche-content-container">
  <FollowupItemDetailHeader item={item} />

  {#if item.events.length}
    <ul class="demarche--events fr-m-0 fr-p-0" data-testid="item-events-list">
      {#each item.events as event}
        <li class="fr-py-2v">
          <p
            class="fr-text--sm am-text-mention-grey demarche--events--date fr-m-0 fr-p-0"
          >
            {event.formattedDate}
          </p>
          <p class="fr-text--sm fr-m-0 fr-p-0">{event.description}</p>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  div.demarche-content-container {
    padding: 4rem 1rem 1rem;
    ul.demarche--events {
      li {
        list-style: none;
        border-bottom: solid 1px var(--border-default-grey);
      }
    }
  }
</style>
