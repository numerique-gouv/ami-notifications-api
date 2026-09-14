<script lang="ts">
  import { FollowupItem, FollowupSubItem } from '$lib/followup';

  interface Props {
    item: FollowupItem | FollowupSubItem;
    displayTitle: boolean;
  }
  let { item, displayTitle }: Props = $props();
</script>

<div class="demarche-content-messages">
  {#if item.events.length}
    {#if displayTitle}
      <h2 class="fr-h6 fr-mb-0">Messages :</h2>
    {/if}
    <ul class="demarche--events fr-mb-3w fr-raw-list" data-testid="item-events-list">
      {#each item.events as event}
        <li class="fr-py-1w">
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
  div.demarche-content-messages {
    .demarche--events {
      li {
        border-bottom: 1px solid var(--background-alt-grey-active);
      }
    }
  }
</style>
