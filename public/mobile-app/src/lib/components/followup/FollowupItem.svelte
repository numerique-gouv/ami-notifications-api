<script lang="ts">
  import { goto } from '$app/navigation';
  import { getDSFRIcon } from '$lib/dsfr-icon';
  import { FollowupItem } from '$lib/followup';

  interface Props {
    item: FollowupItem;
    onOpen: () => void;
  }
  let { item, onOpen }: Props = $props();

  let checkedIcon = $derived(getDSFRIcon(item.icon, 'fr-icon-information-fill'));
  let withDetailButton = $derived(
    !item.sub_items.length && !item.is_archived && item.status_id === 'new' && item.link
  );
</script>

<div class="followup--item">
  <div
    class="followup--item--detail fr-tile fr-tile--sm fr-tile--horizontal fr-enlarge-button { withDetailButton  && 'fr-tile--no-icon' }"
  >
    {#if !item.is_archived}
      <button
        type="button"
        onclick={onOpen}
        data-testid="open-followup-item-modal-{item.id}"
        class="fr-btn fr-btn--icon fr-icon-more-2-fill fr-btn--tertiary-no-outline fr-pt-2w am-icon-20 am-btn-modal open-followup-item-modal fr-icon-more-2-fill"
      >
        Ouvrir la modale liée à l'élément du suivi
      </button>
    {/if}
    <div class="fr-tile__body">
      <div class="fr-tile__content fr-pb-0">
        <h3 class="fr-tile__title">
          <button
            type="button"
            onclick={(e) => goto(item.getItemDetailPageUrl())}
            data-testid="followup-item-link"
          >
            {item.title}
          </button>
        </h3>
        <p
          class="fr-tile__detail fr-text--sm fr-m-0 fr-pr-0"
          data-testid="followup-item-detail-{item.id}"
        >
          <span>
            {#if item.sub_items.length}
              {#if item.wipSubItems.length}
                <strong>En cours</strong> par {item.wipSubItems.length}
                {item.wipSubItems.length === 1 ? 'service': 'services'}
                {#if item.closedSubItems.length}
                  <br>
                {/if}
              {/if}
              {#if item.closedSubItems.length}
                <strong>Terminé</strong> par {item.closedSubItems.length}
                {item.closedSubItems.length === 1 ? 'service': 'services'}
              {/if}
            {:else}
              {item.description}
            {/if}
          </span>
        </p>
        <div class="fr-tile__start fr-mb-3v">
          <p
            class="fr-badge fr-badge--icon-left {checkedIcon} {item.status_id} {item.badgeClassName}"
          >
            {item.status_label}
          </p>
          <p
            class="fr-pr-2w fr-text--xs am-text-mention-grey followup--item--detail--date"
          >
            {item.formattedDate}
          </p>
        </div>
      </div>
      {#if withDetailButton}
        <div class="am-tile__footer fr-pt-1w fr-mr-n2w">
          <div class="fr-btns-group">
            <button
              type="button"
              class="fr-btn fr-mb-0"
              onclick={(e) => goto(item.getItemDetailPageUrl())}
              data-testid="external-item-button-{item.id}"
            >
              Reprendre ma démarche
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .followup--item {
    display: flex;
    flex-direction: column;
    width: 100%;
    &:not(:last-child) {
      margin-bottom: 1.5rem;
    }
    .followup--item--detail {
      padding: 1rem 2rem 1.25rem 1rem;
      width: 100%;
      button.am-btn-modal {
        z-index: 2;
        position: absolute;
        top: 0;
        right: 0;
        min-height: 2.75rem;
        outline-width: 2px;
        &:before {
          position: relative;
          width: var(--icon-size);
          height: var(--icon-size);
        }
      }
      .fr-tile__content {
        .fr-tile__title {
          button {
            &::after {
              bottom: 1rem;
              right: 0.5rem;
              --icon-size: 1.25rem;
              -webkit-mask-image: url("../../../../node_modules/@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
              mask-image: url("../../../../node_modules/@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
            }
          }
        }
        .fr-tile__start {
          width: 100%;
          display: flex;
          justify-content: space-between;
          align-items: center;
          line-height: 1;
        }
      }
    }

    .am-tile__footer {
      button:before {
        display: none;
      }
    }
  }
</style>
