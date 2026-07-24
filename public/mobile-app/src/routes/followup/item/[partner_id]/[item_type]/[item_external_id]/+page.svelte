<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
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
      goto('/');
    }
    if (data.item) {
      item = data.item as FollowupItem;
      backUrl = item.is_archived ? '/#/followup/archived' : '/#/followup';
      checkedIcon = getDSFRIcon(item.icon, 'fr-icon-information-fill');
    }
  });

  const gotoExternalItem = (item: FollowupItem | null) => {
    if (item?.link) {
      window.location.href = item.link;
    }
  };
</script>

<NavWithBackButton {backUrl} />

{#if item}
  <div class="demarche-content-container">
    <p
      class="fr-badge am-badge--blue-dsfr fr-mb-1w fr-badge--icon-left {checkedIcon} {item.status_id}"
    >
      {item.status_label}
    </p>

    <div class="fr-mb-1w">
      <h1 class="fr-h2 fr-mb-2v">{item.title}</h1>
    </div>

    <p class="fr-text--sm am-text-mention-grey demarche--subheading fr-mb-1w">
      {item.subheading}
    </p>
    <p class="fr-text--sm demarche--item-external-id">
      <span class="am-text-mention-grey">référence dossier :</span>
      {item.item_external_id}
    </p>

    <button
      id="external-item-button"
      class="fr-btn fr-btn--secondary fr-btn--lg fr-mb-6v"
      type="button"
      onclick={(e) => gotoExternalItem(item)}
      data-testid="external-item-button-{item.id}"
    >
      Accéder à ma démarche
    </button>

    {#if item.events.length}
      <ul class="demarche--events fr-m-0 fr-p-0">
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
{/if}

<style>
  div.demarche-content-container {
    padding: 4rem 1rem 1rem;
    button#external-item-button {
      width: 100%;
      display: flex;
      justify-content: center;
    }
    ul.demarche--events {
      li {
        list-style: none;
        border-bottom: solid 1px var(--border-default-grey);
      }
    }
  }
</style>
