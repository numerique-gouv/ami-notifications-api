<script lang="ts">
  import { AMIGoto } from '$lib/ami-navigation';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { ariaHideDecorativeEmoji } from '$lib/emoji';
  import { FollowupSubItem } from '$lib/followup';
  import type { Services, ServicesItem } from '$lib/services';

  interface Props {
    item: FollowupSubItem;
    services: Services;
  }
  let { item, services }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(item.icon, 'fr-icon-information-fill'));
  const duration = $derived(item.duration);

  const goToExternalItem = () => {
    let silentLogin: boolean = true;
    const service: ServicesItem | null = services.find(item.partner_id, item.item_type);
    if (service !== null) {
      silentLogin = service.with_silent_login;
    }
    if (item.link) {
      AMIGoto(item.link, silentLogin);
    }
  };
</script>

<div class="demarche-content-header">
  <p
    class="fr-badge fr-mb-1w fr-badge--icon-left {checkedIcon} {item.status_id} {item.badgeClassName}"
  >
    {item.status_label}
  </p>

  <div class="fr-mb-1w">
    <h1 class="fr-h3 fr-mb-3v">{@html ariaHideDecorativeEmoji(item.title)}</h1>
  </div>

  {#if item.subheading}
    <p
      class="fr-text--sm am-text-mention-grey am-text--smbold demarche--subheading fr-mb-1w"
      data-testid="item-subheading"
    >
      {@html ariaHideDecorativeEmoji(item.subheading)}
    </p>
  {/if}
  {#if item.reference}
    <p
      class="fr-text--sm am-text--smbold demarche--item-external-id"
      data-testid="item-reference"
    >
      <span class="am-text-mention-grey">référence dossier :</span>
      {item.reference}
    </p>
  {/if}

  {#if item.hasMilestone()}
    <div class="fr-mb-3w">
      <p
        class="fr-text--sm fr-badge demarche--item-period fr-mb-1w"
        data-testid="item-period"
      >
        {item.period}
      </p>
      {#if duration}
        <p class="fr-text--sm demarche--item-duration" data-testid="item-duration">
          Durée&nbsp;: {duration}
        </p>
      {/if}
    </div>
  {/if}

  {#if item.link}
    <button
      id="external-item-button"
      class="fr-btn fr-btn--secondary fr-btn--lg fr-mb-6v"
      type="button"
      onclick={goToExternalItem}
      data-testid="external-item-button"
    >
      {#if item.hasMilestone()}
        Accéder au détail du rendez-vous
      {:else}
        Accéder à ma démarche
      {/if}
    </button>
  {/if}
</div>

<style>
  div.demarche-content-header {
    .demarche--item-period {
      text-transform: none;
    }
    button#external-item-button {
      width: 100%;
      display: flex;
      justify-content: center;
    }
  }
</style>
