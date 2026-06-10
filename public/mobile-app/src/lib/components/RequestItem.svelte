<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { RequestItem } from '$lib/follow-up';

  interface Props {
    item: RequestItem;
    onOpen: () => void;
  }
  let { item, onOpen }: Props = $props();

  const gotoExternalItem = (item: RequestItem) => {
    if (item.link) {
      goto(item.link);
    }
  };
</script>

<div class="request--item">
  <div
    class="request--item--detail fr-tile fr-tile-sm fr-tile--horizontal fr-enlarge-link no-link"
  >
    {#if !item.is_archived}
      <button
        onclick={onOpen}
        title="Ouvrir la modale liée à l'élément du suivi"
        aria-label="Ouvrir la modale liée à l'élément du suivi"
        data-testid="open-request-item-modal-{item.id}"
        class="open-request-item-modal fr-icon-more-2-fill"
      ></button>
    {/if}
    <div class="fr-tile__body">
      <div class="fr-tile__content {item.link ? '': 'no-link'}">
        <h3 class="fr-tile__title">
          <a
            href="{item.link}"
            onclick={(e) => {if (!item.link) {e.preventDefault();}}}
            data-testid="request-item-link"
            class="{item.link ? '': 'no-link'}"
          >
            {item.title}
          </a>
        </h3>
        <p class="fr-tile__detail">
          <span>{item.description}</span>
          {#if !item.is_archived && item.status_id == 'new' && item.link}
            <div class="action-buttons">
              <button
                class="fr-btn fr-btn--lg"
                type="button"
                onclick={(e) => gotoExternalItem(item)}
                data-testid="external-item-buttom-{item.id}"
              >
                Reprendre ma démarche
              </button>
            </div>
          {/if}
        </p>
        <div class="fr-tile__start">
          <p class="fr-badge fr-badge--icon-left {item.icon} {item.status_id}">
            {item.status_label}
          </p>
          <p class="request--item--detail--date">{item.formattedDate}</p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .request--item {
    display: flex;
    flex-direction: column;
    width: 100%;
    &:not(:last-child) {
      margin-bottom: 1.5rem;
    }
    .request--item--detail.fr-enlarge-link {
      padding: 1rem 2rem 0.5rem 1rem;
      width: 100%;
      &.no-link {
        --hover: transparent;
      }
      button.open-request-item-modal {
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
            &.no-link {
              cursor: default;
              &::after {
                display: none;
              }
            }
          }
        }
        .fr-tile__detail {
          font-size: 14px;
          line-height: 24px;
          margin: 0;
          padding-right: 0;
          flex-direction: column;
          .action-buttons {
            display: flex;
            flex-direction: column;
            width: 100%;
            margin: 0.75rem 0 1rem;
            button {
              display: flex;
              justify-content: center;
              width: 100%;
              font-size: 16px;
              padding: 0.5rem 1rem;
            }
          }
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
          .request--item--detail--date {
            font-size: 12px;
            line-height: 20px;
            color: var(--text-mention-grey);
          }
        }
      }
    }
  }
</style>
