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

  const gotoDetailPage = (itemDetailPageUrl: string) => {
    goto(itemDetailPageUrl);
  };
</script>

<div class="followup--item">
  <div
    class="followup--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link"
  >
    {#if !item.is_archived}
      <button
        onclick={onOpen}
        title="Ouvrir la modale liée à l'élément du suivi"
        aria-label="Ouvrir la modale liée à l'élément du suivi"
        data-testid="open-followup-item-modal-{item.id}"
        class="open-followup-item-modal fr-icon-more-2-fill"
      ></button>
    {/if}
    <div class="fr-tile__body">
      <div class="fr-tile__content">
        <h3 class="fr-tile__title">
          <a
            href="{item.itemDetailPageUrl}"
            onclick={(e) => {if (!item.itemDetailPageUrl) {e.preventDefault();}}}
            data-testid="followup-item-link"
          >
            {item.title}
          </a>
        </h3>
        <p class="fr-tile__detail"><span>{item.description}</span></p>
        <div class="fr-tile__start">
          <p class="fr-badge fr-badge--icon-left {checkedIcon} {item.status_id}">
            {item.status_label}
          </p>
          <p class="followup--item--detail--date">{item.formattedDate}</p>
        </div>
      </div>
      {#if !item.is_archived && item.status_id == 'new' && item.link}
        <div class="am-tile__footer fr-pt-1w">
          <div class="fr-btns-group">
            <button
              class="fr-btn fr-mb-0"
              type="button"
              onclick={(e) => gotoDetailPage(item.itemDetailPageUrl)}
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
    .followup--item--detail.fr-enlarge-link {
      padding: 1rem 2rem 1.25rem 1rem;
      width: 100%;
      button.open-followup-item-modal {
        z-index: 2;
        position: absolute;
        right: 0.25rem;
        color: var(--text-active-blue-france);
        &::before {
          --icon-size: 1.25rem;
        }
      }
      .fr-tile__content {
        padding-bottom: 0;
        .fr-tile__title {
          font-size: 16px;
          a {
            color: var(--text-action-high-blue-france);
            &::after {
              bottom: 0.5rem;
              right: 0.5rem;
              --icon-size: 1.25rem;
              -webkit-mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
              mask-image: url("@gouvfr/dsfr/dist/icons/arrows/arrow-right-s-line.svg");
            }
          }
        }
        .fr-tile__detail {
          font-size: 14px;
          line-height: 24px;
          margin: 0;
          padding-right: 0;
          flex-direction: column;
        }
        .fr-tile__start {
          width: 100%;
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          .fr-badge {
            font-size: 12px;
            font-weight: 700;
            line-height: 20px;
            color: var(--text-active-blue-france);
            background-color: var(--background-action-low-blue-france);
            margin-bottom: 0.5rem;
            &::before {
              --icon-size: 0.75rem;
            }
          }
          .followup--item--detail--date {
            font-size: 12px;
            line-height: 20px;
            color: var(--text-mention-grey);
          }
        }
      }
    }
  }
</style>
