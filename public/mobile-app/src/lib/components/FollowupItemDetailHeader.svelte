<script lang="ts">
  import { goto } from '$app/navigation';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupItem } from '$lib/followup';

  interface Props {
    item: FollowupItem;
  }
  let { item }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(item.icon, 'fr-icon-information-fill'));

  const gotoExternalItem = () => {
    if (item?.link) {
      window.location.href = item.link;
    }
  };
</script>

<div class="demarche-content-header">
  <p
    class="fr-badge am-badge--blue-dsfr fr-mb-1w fr-badge--icon-left {checkedIcon} {item.status_id}"
  >
    {item.status_label}
  </p>

  <div class="fr-mb-1w">
    <h1 class="fr-h2 fr-mb-2v">{item.title}</h1>
  </div>

  {#if item.subheading}
    <p
      class="fr-text--sm am-text-mention-grey demarche--subheading fr-mb-1w"
      data-testid="item-subheading"
    >
      {item.subheading}
    </p>
  {/if}
  {#if item.reference}
    <p class="fr-text--sm demarche--item-external-id" data-testid="item-reference">
      <span class="am-text-mention-grey">référence dossier :</span>
      {item.reference}
    </p>
  {/if}

  {#if item.link}
    <button
      id="external-item-button"
      class="fr-btn fr-btn--secondary fr-btn--lg fr-mb-6v"
      type="button"
      onclick={gotoExternalItem}
      data-testid="external-item-button"
    >
      Accéder à ma démarche
    </button>
  {/if}
</div>

<style>
  div.demarche-content-header {
    button#external-item-button {
      width: 100%;
      display: flex;
      justify-content: center;
    }
  }
</style>
